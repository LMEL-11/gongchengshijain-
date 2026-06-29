<!-- 文件功能：渲染全国、省、市多层级 3D 地图并处理钻取、返回和悬停交互。 -->
<script setup>
import { geoMercator } from '@/utils/projection'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { fetchArea, normalizeName } from '@/utils/geo'

const props = defineProps({
  // { 规范化区域名: 数值 }，用于给区域着色
  dataMap: { type: Object, default: () => ({}) },
  valueLabel: { type: String, default: '二手房挂牌量' },
  unit: { type: String, default: '套' },
  leafClickLabel: { type: String, default: '' },
})
const emit = defineEmits(['levelchange', 'regionclick'])

const container = ref(null)
const loading = ref(false)
const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  name: '',
  value: null,
  drillable: false,
  leafHint: '',
})

// --- 非响应式 Three 对象 ---
let scene, camera, renderer, controls, raycaster, pointer
let mapGroup = null
let regions = [] // { group, meshes:[], capMat, meta }
let pickMeshes = []
let hovered = null
let frameId = null
let resizeObserver = null

let levels = [{ adcode: 100000, name: '全国' }]

const FIT = 38 // 投影适配半径
const DEPTH = 2.4 // 立体厚度
const RAISE = 1.6 // 悬停抬升
const NEUTRAL = new THREE.Color('#1e3a5f')
const LOW = new THREE.Color('#16407a')
const HIGH = new THREE.Color('#3fe0ff')

// props.dataMap 是“规范化区域名 -> 指标值”，颜色表达的是当前地图层级内的相对高低。
// 函数功能：根据数值和层级计算地图区域颜色。
function colorFor(t) {
  return new THREE.Color().lerpColors(LOW, HIGH, Math.max(0, Math.min(1, t)))
}

// 函数功能：将大数值压缩为适合地图标签的短文本。
function compactValue(value) {
  if (typeof value !== 'number') return ''
  if (value >= 10000) {
    const text = (value / 10000).toFixed(value >= 100000 ? 0 : 1).replace(/\.0$/, '')
    return `${text}万${props.unit}`
  }
  return `${Number(value).toLocaleString()}${props.unit}`
}

// 函数功能：绘制 3D 地图标签所需的 Canvas 纹理。
function makeLabelTexture(text, value = null) {
  const canvas = document.createElement('canvas')
  canvas.width = 320
  canvas.height = 104
  const ctx = canvas.getContext('2d')
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.shadowColor = 'rgba(0,40,80,0.9)'
  ctx.shadowBlur = 8

  const valueText = compactValue(value)
  ctx.font = 'bold 29px "Microsoft YaHei", sans-serif'
  ctx.fillStyle = '#eaf6ff'
  ctx.fillText(text, 160, valueText ? 34 : 52)

  if (valueText) {
    ctx.font = 'bold 24px "Microsoft YaHei", sans-serif'
    ctx.fillStyle = '#5fe9ff'
    ctx.fillText(valueText, 160, 74)
  }

  const tex = new THREE.CanvasTexture(canvas)
  tex.minFilter = THREE.LinearFilter
  return tex
}

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text, value = null) {
  const tex = makeLabelTexture(text, value)
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }),
  )
  sprite.scale.set(8.5, 2.75, 1)
  sprite.renderOrder = 10
  return sprite
}

// 函数功能：根据相机距离更新标签可见性和缩放。
function updateLabel(meta) {
  if (!meta.label) return
  const key = `${meta.name}:${meta.value ?? ''}`
  if (meta.labelKey === key) return
  const oldMap = meta.label.material.map
  meta.label.material.map = makeLabelTexture(meta.name, meta.value)
  meta.label.material.needsUpdate = true
  oldMap?.dispose?.()
  meta.labelKey = key
}

// 函数功能：释放当前 3D 地图对象及其材质资源。
function disposeMap() {
  if (!mapGroup) return
  mapGroup.traverse((o) => {
    o.geometry?.dispose?.()
    if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose())
    else if (o.material) {
      o.material.map?.dispose?.()
      o.material.dispose()
    }
  })
  scene.remove(mapGroup)
  mapGroup = null
  regions = []
  pickMeshes = []
  hovered = null
}

// 函数功能：根据 GeoJSON 和统计数据构建当前层级 3D 地图。
function buildMap(features) {
  disposeMap()
  // DataV GeoJSON 仍是经纬度坐标，先 fit 到固定视觉范围，再转成 Three.js 平面坐标。
  const projection = geoMercator().fitExtent(
    [
      [-FIT, -FIT],
      [FIT, FIT],
    ],
    { type: 'FeatureCollection', features },
  )
  // 函数功能：将经纬度坐标投影到当前地图平面坐标。
  const project = ([lng, lat]) => {
    const p = projection([lng, lat])
    return [p[0], -p[1]]
  }

  mapGroup = new THREE.Group()
  mapGroup.rotation.x = -Math.PI / 2 // 平铺：局部 z -> 世界 +y（高度）

  const sideMat = new THREE.MeshStandardMaterial({
    color: '#0c2747',
    metalness: 0.4,
    roughness: 0.55,
  })
  const outlineMat = new THREE.LineBasicMaterial({ color: '#5fe9ff', transparent: true, opacity: 0.9 })

  for (const feature of features) {
    const polygons =
      feature.geometry.type === 'Polygon'
        ? [feature.geometry.coordinates]
        : feature.geometry.coordinates

    const group = new THREE.Group()
    const capMat = new THREE.MeshStandardMaterial({
      color: NEUTRAL.clone(),
      metalness: 0.25,
      roughness: 0.7,
    })
    // meta 统一保存地图区域的业务信息和 Three.js 对象引用，点击/悬停/着色都复用它。
    const meta = {
      name: feature.properties.name,
      normName: normalizeName(feature.properties.name),
      adcode: feature.properties.adcode,
      childrenNum: feature.properties.childrenNum ?? 0,
      value: null,
      group,
      label: null,
      labelKey: '',
    }
    const meshes = []

    for (const poly of polygons) {
      const outer = poly[0]
      const shape = new THREE.Shape()
      outer.forEach((c, i) => {
        const [x, y] = project(c)
        i === 0 ? shape.moveTo(x, y) : shape.lineTo(x, y)
      })
      for (let h = 1; h < poly.length; h++) {
        const path = new THREE.Path()
        poly[h].forEach((c, i) => {
          const [x, y] = project(c)
          i === 0 ? path.moveTo(x, y) : path.lineTo(x, y)
        })
        shape.holes.push(path)
      }

      const geom = new THREE.ExtrudeGeometry(shape, { depth: DEPTH, bevelEnabled: false })
      const mesh = new THREE.Mesh(geom, [capMat, sideMat]) // 0=顶/底面 1=侧壁
      mesh.userData.meta = meta
      group.add(mesh)
      meshes.push(mesh)
      pickMeshes.push(mesh)

      // 顶部发光轮廓
      const pts = outer.map((c) => {
        const [x, y] = project(c)
        return new THREE.Vector3(x, y, DEPTH + 0.02)
      })
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), outlineMat)
      line.raycast = () => {}
      group.add(line)
    }

    // 标签置于质心上方
    const c = feature.properties.centroid || feature.properties.center
    if (c) {
      const [lx, ly] = project(c)
      const label = makeLabel(feature.properties.name)
      label.position.set(lx, ly, DEPTH + 0.8)
      meta.label = label
      group.add(label)
    }

    meta.capMat = capMat
    meta.meshes = meshes
    regions.push(meta)
    mapGroup.add(group)
  }

  scene.add(mapGroup)
  applyColors()
  controls.target.set(0, 0, 0)
}

// 依据 dataMap 给区域着色
// 函数功能：根据数据指标刷新地图区域颜色。
function applyColors() {
  if (!regions.length) return
  // 每次数据或层级变化都按当前可见区域重新归一化，避免全国和城市级数值跨度互相干扰。
  const values = regions
    .map((r) => props.dataMap[r.normName] ?? props.dataMap[r.name])
    .filter((v) => typeof v === 'number')
  const min = values.length ? Math.min(...values) : 0
  const max = values.length ? Math.max(...values) : 1
  const span = max - min || 1
  for (const r of regions) {
    const v = props.dataMap[r.normName] ?? props.dataMap[r.name]
    r.value = typeof v === 'number' ? v : null
    r.capMat.color.copy(r.value == null ? NEUTRAL : colorFor((r.value - min) / span))
    updateLabel(r)
  }
}

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(meta) {
  hovered = meta
  meta.capMat.emissive = new THREE.Color('#1d6fa5')
  meta.capMat.emissiveIntensity = 0.6
}
// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() {
  if (hovered) {
    hovered.capMat.emissive = new THREE.Color('#000000')
    hovered = null
  }
}

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(e) {
  const rect = renderer.domElement.getBoundingClientRect()
  pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  const hits = raycaster.intersectObjects(pickMeshes, false)
  if (hits.length) {
    const meta = hits[0].object.userData.meta
    if (hovered !== meta) {
      clearHover()
      setHover(meta)
    }
    tooltip.value = {
      show: true,
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      name: meta.name,
      value: meta.value,
      drillable: meta.childrenNum > 0,
      leafHint: meta.childrenNum > 0 ? '' : props.leafClickLabel,
    }
    renderer.domElement.style.cursor = meta.childrenNum > 0 || props.leafClickLabel ? 'pointer' : 'default'
  } else {
    clearHover()
    tooltip.value.show = false
    renderer.domElement.style.cursor = 'grab'
  }
}

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() {
  if (!hovered) return
  if (hovered.childrenNum > 0) {
    navigate([...levels, { adcode: hovered.adcode, name: hovered.name }])
    return
  }
  if (props.leafClickLabel) {
    emit('regionclick', {
      name: hovered.name,
      normName: hovered.normName,
      adcode: hovered.adcode,
      value: hovered.value,
      path: levels.map((l) => ({ ...l })),
    })
  }
}

// 函数功能：切换到指定地图层级并加载对应区域数据。
async function navigate(newLevels) {
  levels = newLevels
  const cur = levels[levels.length - 1]
  loading.value = true
  try {
    // 导航时先加载当前 adcode 的下级边界，再把路径抛给父组件刷新排行和指标数据。
    const geo = await fetchArea(cur.adcode)
    buildMap(geo.features)
    emit('levelchange', { adcode: cur.adcode, name: cur.name, path: levels.map((l) => ({ ...l })) })
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 函数功能：返回上一级地图层级。
function back() {
  if (levels.length > 1) navigate(levels.slice(0, -1))
}
// 函数功能：根据面包屑跳转到指定地图层级。
function goToLevel(i) {
  if (i >= 0 && i < levels.length - 1) navigate(levels.slice(0, i + 1))
}
// 函数功能：重置地图到全国层级。
function reset() {
  navigate([{ adcode: 100000, name: '全国' }])
}
defineExpose({ back, goToLevel, reset })

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() {
  frameId = requestAnimationFrame(animate)
  // 悬停区域平滑抬升
  for (const r of regions) {
    const target = r === hovered ? RAISE : 0
    r.group.position.z += (target - r.group.position.z) * 0.18
  }
  controls.update()
  renderer.render(scene, camera)
}

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() {
  const el = container.value
  if (!el || !renderer) return
  camera.aspect = el.clientWidth / el.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(el.clientWidth, el.clientHeight)
}

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() {
  const el = container.value
  const w = el.clientWidth
  const h = el.clientHeight || 600

  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000)
  camera.position.set(0, 60, 64)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setSize(w, h)
  renderer.setClearColor(0x000000, 0) // 透明，露出大屏背景
  el.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.minDistance = 28
  controls.maxDistance = 180
  controls.maxPolarAngle = Math.PI / 2.1

  scene.add(new THREE.AmbientLight(0xffffff, 0.9))
  const key = new THREE.DirectionalLight(0xa9d8ff, 0.8)
  key.position.set(10, 80, 40)
  scene.add(key)

  raycaster = new THREE.Raycaster()
  pointer = new THREE.Vector2()

  renderer.domElement.addEventListener('pointermove', onPointerMove)
  renderer.domElement.addEventListener('click', onClick)
  renderer.domElement.addEventListener('pointerleave', () => {
    tooltip.value.show = false
    clearHover()
  })
  resizeObserver = new ResizeObserver(onResize)
  resizeObserver.observe(el)

  animate()
  navigate(levels) // 初始加载全国
}

onMounted(initThree)
watch(() => props.dataMap, applyColors, { deep: true })

onBeforeUnmount(() => {
  if (frameId) cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  renderer?.domElement.removeEventListener('pointermove', onPointerMove)
  renderer?.domElement.removeEventListener('click', onClick)
  disposeMap()
  renderer?.dispose()
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) {
    container.value.removeChild(renderer.domElement)
  }
  scene = camera = renderer = controls = raycaster = pointer = null
})

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString())
</script>

<template>
  <div class="geo-map">
    <div ref="container" class="canvas-host"></div>

    <div v-if="loading" class="overlay">
      <span class="spin"></span> 地图加载中…
    </div>

    <div
      v-show="tooltip.show"
      class="tip"
      :style="{ left: tooltip.x + 16 + 'px', top: tooltip.y + 16 + 'px' }"
    >
      <div class="tip-name">{{ tooltip.name }}</div>
      <div class="tip-row">{{ valueLabel }}：<b>{{ fmt(tooltip.value) }}</b> {{ unit }}</div>
      <div v-if="tooltip.drillable" class="tip-hint">▸ 点击下钻</div>
      <div v-else-if="tooltip.leafHint" class="tip-hint">▸ {{ tooltip.leafHint }}</div>
    </div>
  </div>
</template>

<style scoped>
.geo-map {
  position: relative;
  width: 100%;
  height: 100%;
}
.canvas-host {
  width: 100%;
  height: 100%;
}
.overlay {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  color: #9fd6ff;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.spin {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(95, 233, 255, 0.3);
  border-top-color: #5fe9ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.tip {
  position: absolute;
  pointer-events: none;
  background: rgba(7, 25, 50, 0.92);
  border: 1px solid rgba(95, 233, 255, 0.5);
  border-radius: 8px;
  padding: 10px 14px;
  color: #dbeeff;
  font-size: 13px;
  z-index: 5;
  min-width: 150px;
}
.tip-name {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}
.tip-row b {
  color: #5fe9ff;
  font-size: 15px;
}
.tip-hint {
  margin-top: 4px;
  color: #ffd166;
}
</style>
