<!-- 文件功能：渲染全国、省、市多层级 3D 地图并处理钻取、返回和悬停交互。 -->
<script setup>
import { geoMercator } from '@/utils/projection' // 逐行注释：导入本行所需的依赖。
import * as THREE from 'three' // 逐行注释：导入本行所需的依赖。
import { OrbitControls } from 'three/addons/controls/OrbitControls.js' // 逐行注释：导入本行所需的依赖。
import { onBeforeUnmount, onMounted, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。

import { fetchArea, normalizeName } from '@/utils/geo' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  // { 规范化区域名: 数值 }，用于给区域着色
  dataMap: { type: Object, default: () => ({}) }, // 逐行注释：配置当前对象字段。
  valueLabel: { type: String, default: '二手房挂牌量' }, // 逐行注释：配置当前对象字段。
  unit: { type: String, default: '套' }, // 逐行注释：配置当前对象字段。
  leafClickLabel: { type: String, default: '' }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。
const emit = defineEmits(['levelchange', 'regionclick']) // 逐行注释：声明并初始化当前变量。

const container = ref(null) // 逐行注释：声明并初始化当前变量。
const loading = ref(false) // 逐行注释：声明并初始化当前变量。
const tooltip = ref({ // 逐行注释：声明并初始化当前变量。
  show: false, // 逐行注释：配置当前对象字段。
  x: 0, // 逐行注释：配置当前对象字段。
  y: 0, // 逐行注释：配置当前对象字段。
  name: '', // 逐行注释：配置当前对象字段。
  value: null, // 逐行注释：配置当前对象字段。
  drillable: false, // 逐行注释：配置当前对象字段。
  leafHint: '', // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。

// --- 非响应式 Three 对象 ---
let scene, camera, renderer, controls, raycaster, pointer // 逐行注释：声明并初始化当前变量。
let mapGroup = null // 逐行注释：声明并初始化当前变量。
let regions = [] // { group, meshes:[], capMat, meta }
let pickMeshes = [] // 逐行注释：声明并初始化当前变量。
let hovered = null // 逐行注释：声明并初始化当前变量。
let frameId = null // 逐行注释：声明并初始化当前变量。
let resizeObserver = null // 逐行注释：声明并初始化当前变量。

let levels = [{ adcode: 100000, name: '全国' }] // 逐行注释：声明并初始化当前变量。

const FIT = 38 // 投影适配半径
const DEPTH = 2.4 // 立体厚度
const RAISE = 1.6 // 悬停抬升
const NEUTRAL = new THREE.Color('#1e3a5f') // 逐行注释：声明并初始化当前变量。
const LOW = new THREE.Color('#16407a') // 逐行注释：声明并初始化当前变量。
const HIGH = new THREE.Color('#3fe0ff') // 逐行注释：声明并初始化当前变量。

// 函数功能：根据数值和层级计算地图区域颜色。
function colorFor(t) { // 逐行注释：声明当前函数入口。
  return new THREE.Color().lerpColors(LOW, HIGH, Math.max(0, Math.min(1, t))) // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：将大数值压缩为适合地图标签的短文本。
function compactValue(value) { // 逐行注释：声明当前函数入口。
  if (typeof value !== 'number') return '' // 逐行注释：根据条件判断是否执行分支。
  if (value >= 10000) { // 逐行注释：根据条件判断是否执行分支。
    const text = (value / 10000).toFixed(value >= 100000 ? 0 : 1).replace(/\.0$/, '') // 逐行注释：声明并初始化当前变量。
    return `${text}万${props.unit}` // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。
  return `${Number(value).toLocaleString()}${props.unit}` // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：绘制 3D 地图标签所需的 Canvas 纹理。
function makeLabelTexture(text, value = null) { // 逐行注释：声明当前函数入口。
  const canvas = document.createElement('canvas') // 逐行注释：声明并初始化当前变量。
  canvas.width = 320 // 逐行注释：赋值或更新当前变量/状态。
  canvas.height = 104 // 逐行注释：赋值或更新当前变量/状态。
  const ctx = canvas.getContext('2d') // 逐行注释：声明并初始化当前变量。
  ctx.textAlign = 'center' // 逐行注释：赋值或更新当前变量/状态。
  ctx.textBaseline = 'middle' // 逐行注释：赋值或更新当前变量/状态。
  ctx.shadowColor = 'rgba(0,40,80,0.9)' // 逐行注释：赋值或更新当前变量/状态。
  ctx.shadowBlur = 8 // 逐行注释：赋值或更新当前变量/状态。

  const valueText = compactValue(value) // 逐行注释：声明并初始化当前变量。
  ctx.font = 'bold 29px "Microsoft YaHei", sans-serif' // 逐行注释：赋值或更新当前变量/状态。
  ctx.fillStyle = '#eaf6ff' // 逐行注释：赋值或更新当前变量/状态。
  ctx.fillText(text, 160, valueText ? 34 : 52) // 逐行注释：执行本行前端逻辑。

  if (valueText) { // 逐行注释：根据条件判断是否执行分支。
    ctx.font = 'bold 24px "Microsoft YaHei", sans-serif' // 逐行注释：赋值或更新当前变量/状态。
    ctx.fillStyle = '#5fe9ff' // 逐行注释：赋值或更新当前变量/状态。
    ctx.fillText(valueText, 160, 74) // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。

  const tex = new THREE.CanvasTexture(canvas) // 逐行注释：声明并初始化当前变量。
  tex.minFilter = THREE.LinearFilter // 逐行注释：赋值或更新当前变量/状态。
  return tex // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text, value = null) { // 逐行注释：声明当前函数入口。
  const tex = makeLabelTexture(text, value) // 逐行注释：声明并初始化当前变量。
  const sprite = new THREE.Sprite( // 逐行注释：声明并初始化当前变量。
    new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }), // 逐行注释：配置当前对象字段。
  ) // 逐行注释：结束当前代码块或数据结构。
  sprite.scale.set(8.5, 2.75, 1) // 逐行注释：执行本行前端逻辑。
  sprite.renderOrder = 10 // 逐行注释：赋值或更新当前变量/状态。
  return sprite // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据相机距离更新标签可见性和缩放。
function updateLabel(meta) { // 逐行注释：声明当前函数入口。
  if (!meta.label) return // 逐行注释：根据条件判断是否执行分支。
  const key = `${meta.name}:${meta.value ?? ''}` // 逐行注释：声明并初始化当前变量。
  if (meta.labelKey === key) return // 逐行注释：根据条件判断是否执行分支。
  const oldMap = meta.label.material.map // 逐行注释：声明并初始化当前变量。
  meta.label.material.map = makeLabelTexture(meta.name, meta.value) // 逐行注释：赋值或更新当前变量/状态。
  meta.label.material.needsUpdate = true // 逐行注释：赋值或更新当前变量/状态。
  oldMap?.dispose?.() // 逐行注释：执行本行前端逻辑。
  meta.labelKey = key // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：释放当前 3D 地图对象及其材质资源。
function disposeMap() { // 逐行注释：声明当前函数入口。
  if (!mapGroup) return // 逐行注释：根据条件判断是否执行分支。
  mapGroup.traverse((o) => { // 逐行注释：执行本行前端逻辑。
    o.geometry?.dispose?.() // 逐行注释：执行本行前端逻辑。
    if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose()) // 逐行注释：根据条件判断是否执行分支。
    else if (o.material) { // 逐行注释：处理条件不满足时的分支。
      o.material.map?.dispose?.() // 逐行注释：执行本行前端逻辑。
      o.material.dispose() // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
  }) // 逐行注释：执行本行前端逻辑。
  scene.remove(mapGroup) // 逐行注释：执行本行前端逻辑。
  mapGroup = null // 逐行注释：赋值或更新当前变量/状态。
  regions = [] // 逐行注释：赋值或更新当前变量/状态。
  pickMeshes = [] // 逐行注释：赋值或更新当前变量/状态。
  hovered = null // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据 GeoJSON 和统计数据构建当前层级 3D 地图。
function buildMap(features) { // 逐行注释：声明当前函数入口。
  disposeMap() // 逐行注释：执行本行前端逻辑。
  const projection = geoMercator().fitExtent( // 逐行注释：声明并初始化当前变量。
    [ // 逐行注释：执行本行前端逻辑。
      [-FIT, -FIT], // 逐行注释：继续声明当前列表项或参数项。
      [FIT, FIT], // 逐行注释：继续声明当前列表项或参数项。
    ], // 逐行注释：结束当前代码块或数据结构。
    { type: 'FeatureCollection', features }, // 逐行注释：配置当前对象字段。
  ) // 逐行注释：结束当前代码块或数据结构。
  // 函数功能：将经纬度坐标投影到当前地图平面坐标。
  const project = ([lng, lat]) => { // 逐行注释：声明并初始化当前变量。
    const p = projection([lng, lat]) // 逐行注释：声明并初始化当前变量。
    return [p[0], -p[1]] // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。

  mapGroup = new THREE.Group() // 逐行注释：赋值或更新当前变量/状态。
  mapGroup.rotation.x = -Math.PI / 2 // 平铺：局部 z -> 世界 +y（高度）

  const sideMat = new THREE.MeshStandardMaterial({ // 逐行注释：声明并初始化当前变量。
    color: '#0c2747', // 逐行注释：配置当前对象字段。
    metalness: 0.4, // 逐行注释：配置当前对象字段。
    roughness: 0.55, // 逐行注释：配置当前对象字段。
  }) // 逐行注释：执行本行前端逻辑。
  const outlineMat = new THREE.LineBasicMaterial({ color: '#5fe9ff', transparent: true, opacity: 0.9 }) // 逐行注释：声明并初始化当前变量。

  for (const feature of features) { // 逐行注释：遍历集合或范围并逐项处理。
    const polygons = // 逐行注释：声明并初始化当前变量。
      feature.geometry.type === 'Polygon' // 逐行注释：执行本行前端逻辑。
        ? [feature.geometry.coordinates] // 逐行注释：执行本行前端逻辑。
        : feature.geometry.coordinates // 逐行注释：执行本行前端逻辑。

    const group = new THREE.Group() // 逐行注释：声明并初始化当前变量。
    const capMat = new THREE.MeshStandardMaterial({ // 逐行注释：声明并初始化当前变量。
      color: NEUTRAL.clone(), // 逐行注释：配置当前对象字段。
      metalness: 0.25, // 逐行注释：配置当前对象字段。
      roughness: 0.7, // 逐行注释：配置当前对象字段。
    }) // 逐行注释：执行本行前端逻辑。
    const meta = { // 逐行注释：声明并初始化当前变量。
      name: feature.properties.name, // 逐行注释：配置当前对象字段。
      normName: normalizeName(feature.properties.name), // 逐行注释：配置当前对象字段。
      adcode: feature.properties.adcode, // 逐行注释：配置当前对象字段。
      childrenNum: feature.properties.childrenNum ?? 0, // 逐行注释：配置当前对象字段。
      value: null, // 逐行注释：配置当前对象字段。
      group, // 逐行注释：继续声明当前列表项或参数项。
      label: null, // 逐行注释：配置当前对象字段。
      labelKey: '', // 逐行注释：配置当前对象字段。
    } // 逐行注释：结束当前代码块或数据结构。
    const meshes = [] // 逐行注释：声明并初始化当前变量。

    for (const poly of polygons) { // 逐行注释：遍历集合或范围并逐项处理。
      const outer = poly[0] // 逐行注释：声明并初始化当前变量。
      const shape = new THREE.Shape() // 逐行注释：声明并初始化当前变量。
      outer.forEach((c, i) => { // 逐行注释：执行本行前端逻辑。
        const [x, y] = project(c) // 逐行注释：声明并初始化当前变量。
        i === 0 ? shape.moveTo(x, y) : shape.lineTo(x, y) // 逐行注释：执行本行前端逻辑。
      }) // 逐行注释：执行本行前端逻辑。
      for (let h = 1; h < poly.length; h++) { // 逐行注释：遍历集合或范围并逐项处理。
        const path = new THREE.Path() // 逐行注释：声明并初始化当前变量。
        poly[h].forEach((c, i) => { // 逐行注释：执行本行前端逻辑。
          const [x, y] = project(c) // 逐行注释：声明并初始化当前变量。
          i === 0 ? path.moveTo(x, y) : path.lineTo(x, y) // 逐行注释：执行本行前端逻辑。
        }) // 逐行注释：执行本行前端逻辑。
        shape.holes.push(path) // 逐行注释：执行本行前端逻辑。
      } // 逐行注释：结束当前代码块或数据结构。

      const geom = new THREE.ExtrudeGeometry(shape, { depth: DEPTH, bevelEnabled: false }) // 逐行注释：声明并初始化当前变量。
      const mesh = new THREE.Mesh(geom, [capMat, sideMat]) // 0=顶/底面 1=侧壁
      mesh.userData.meta = meta // 逐行注释：赋值或更新当前变量/状态。
      group.add(mesh) // 逐行注释：执行本行前端逻辑。
      meshes.push(mesh) // 逐行注释：执行本行前端逻辑。
      pickMeshes.push(mesh) // 逐行注释：执行本行前端逻辑。

      // 顶部发光轮廓
      const pts = outer.map((c) => { // 逐行注释：声明并初始化当前变量。
        const [x, y] = project(c) // 逐行注释：声明并初始化当前变量。
        return new THREE.Vector3(x, y, DEPTH + 0.02) // 逐行注释：返回当前表达式结果。
      }) // 逐行注释：执行本行前端逻辑。
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), outlineMat) // 逐行注释：声明并初始化当前变量。
      line.raycast = () => {} // 逐行注释：执行本行前端逻辑。
      group.add(line) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。

    // 标签置于质心上方
    const c = feature.properties.centroid || feature.properties.center // 逐行注释：声明并初始化当前变量。
    if (c) { // 逐行注释：根据条件判断是否执行分支。
      const [lx, ly] = project(c) // 逐行注释：声明并初始化当前变量。
      const label = makeLabel(feature.properties.name) // 逐行注释：声明并初始化当前变量。
      label.position.set(lx, ly, DEPTH + 0.8) // 逐行注释：执行本行前端逻辑。
      meta.label = label // 逐行注释：赋值或更新当前变量/状态。
      group.add(label) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。

    meta.capMat = capMat // 逐行注释：赋值或更新当前变量/状态。
    meta.meshes = meshes // 逐行注释：赋值或更新当前变量/状态。
    regions.push(meta) // 逐行注释：执行本行前端逻辑。
    mapGroup.add(group) // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。

  scene.add(mapGroup) // 逐行注释：执行本行前端逻辑。
  applyColors() // 逐行注释：执行本行前端逻辑。
  controls.target.set(0, 0, 0) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 依据 dataMap 给区域着色
// 函数功能：根据数据指标刷新地图区域颜色。
function applyColors() { // 逐行注释：声明当前函数入口。
  if (!regions.length) return // 逐行注释：根据条件判断是否执行分支。
  const values = regions // 逐行注释：声明并初始化当前变量。
    .map((r) => props.dataMap[r.normName] ?? props.dataMap[r.name]) // 逐行注释：执行本行前端逻辑。
    .filter((v) => typeof v === 'number') // 逐行注释：执行本行前端逻辑。
  const min = values.length ? Math.min(...values) : 0 // 逐行注释：声明并初始化当前变量。
  const max = values.length ? Math.max(...values) : 1 // 逐行注释：声明并初始化当前变量。
  const span = max - min || 1 // 逐行注释：声明并初始化当前变量。
  for (const r of regions) { // 逐行注释：遍历集合或范围并逐项处理。
    const v = props.dataMap[r.normName] ?? props.dataMap[r.name] // 逐行注释：声明并初始化当前变量。
    r.value = typeof v === 'number' ? v : null // 逐行注释：执行本行前端逻辑。
    r.capMat.color.copy(r.value == null ? NEUTRAL : colorFor((r.value - min) / span)) // 逐行注释：执行本行前端逻辑。
    updateLabel(r) // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(meta) { // 逐行注释：声明当前函数入口。
  hovered = meta // 逐行注释：赋值或更新当前变量/状态。
  meta.capMat.emissive = new THREE.Color('#1d6fa5') // 逐行注释：赋值或更新当前变量/状态。
  meta.capMat.emissiveIntensity = 0.6 // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。
// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() { // 逐行注释：声明当前函数入口。
  if (hovered) { // 逐行注释：根据条件判断是否执行分支。
    hovered.capMat.emissive = new THREE.Color('#000000') // 逐行注释：赋值或更新当前变量/状态。
    hovered = null // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(e) { // 逐行注释：声明当前函数入口。
  const rect = renderer.domElement.getBoundingClientRect() // 逐行注释：声明并初始化当前变量。
  pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1 // 逐行注释：赋值或更新当前变量/状态。
  pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1 // 逐行注释：赋值或更新当前变量/状态。
  raycaster.setFromCamera(pointer, camera) // 逐行注释：执行本行前端逻辑。
  const hits = raycaster.intersectObjects(pickMeshes, false) // 逐行注释：声明并初始化当前变量。
  if (hits.length) { // 逐行注释：根据条件判断是否执行分支。
    const meta = hits[0].object.userData.meta // 逐行注释：声明并初始化当前变量。
    if (hovered !== meta) { // 逐行注释：根据条件判断是否执行分支。
      clearHover() // 逐行注释：执行本行前端逻辑。
      setHover(meta) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
    tooltip.value = { // 逐行注释：赋值或更新当前变量/状态。
      show: true, // 逐行注释：配置当前对象字段。
      x: e.clientX - rect.left, // 逐行注释：配置当前对象字段。
      y: e.clientY - rect.top, // 逐行注释：配置当前对象字段。
      name: meta.name, // 逐行注释：配置当前对象字段。
      value: meta.value, // 逐行注释：配置当前对象字段。
      drillable: meta.childrenNum > 0, // 逐行注释：配置当前对象字段。
      leafHint: meta.childrenNum > 0 ? '' : props.leafClickLabel, // 逐行注释：配置当前对象字段。
    } // 逐行注释：结束当前代码块或数据结构。
    renderer.domElement.style.cursor = meta.childrenNum > 0 || props.leafClickLabel ? 'pointer' : 'default' // 逐行注释：赋值或更新当前变量/状态。
  } else { // 逐行注释：执行本行前端逻辑。
    clearHover() // 逐行注释：执行本行前端逻辑。
    tooltip.value.show = false // 逐行注释：赋值或更新当前变量/状态。
    renderer.domElement.style.cursor = 'grab' // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() { // 逐行注释：声明当前函数入口。
  if (!hovered) return // 逐行注释：根据条件判断是否执行分支。
  if (hovered.childrenNum > 0) { // 逐行注释：根据条件判断是否执行分支。
    navigate([...levels, { adcode: hovered.adcode, name: hovered.name }]) // 逐行注释：执行本行前端逻辑。
    return // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。
  if (props.leafClickLabel) { // 逐行注释：根据条件判断是否执行分支。
    emit('regionclick', { // 逐行注释：向父组件派发事件。
      name: hovered.name, // 逐行注释：配置当前对象字段。
      normName: hovered.normName, // 逐行注释：配置当前对象字段。
      adcode: hovered.adcode, // 逐行注释：配置当前对象字段。
      value: hovered.value, // 逐行注释：配置当前对象字段。
      path: levels.map((l) => ({ ...l })), // 逐行注释：配置当前对象字段。
    }) // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：切换到指定地图层级并加载对应区域数据。
async function navigate(newLevels) { // 逐行注释：声明当前函数入口。
  levels = newLevels // 逐行注释：赋值或更新当前变量/状态。
  const cur = levels[levels.length - 1] // 逐行注释：声明并初始化当前变量。
  loading.value = true // 逐行注释：赋值或更新当前变量/状态。
  try { // 逐行注释：开始执行可能失败的逻辑。
    const geo = await fetchArea(cur.adcode) // 逐行注释：声明并初始化当前变量。
    buildMap(geo.features) // 逐行注释：执行本行前端逻辑。
    emit('levelchange', { adcode: cur.adcode, name: cur.name, path: levels.map((l) => ({ ...l })) }) // 逐行注释：向父组件派发事件。
  } catch (err) { // 逐行注释：执行本行前端逻辑。
    console.error(err) // 逐行注释：执行本行前端逻辑。
  } finally { // 逐行注释：执行本行前端逻辑。
    loading.value = false // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：返回上一级地图层级。
function back() { // 逐行注释：声明当前函数入口。
  if (levels.length > 1) navigate(levels.slice(0, -1)) // 逐行注释：根据条件判断是否执行分支。
} // 逐行注释：结束当前代码块或数据结构。
// 函数功能：根据面包屑跳转到指定地图层级。
function goToLevel(i) { // 逐行注释：声明当前函数入口。
  if (i >= 0 && i < levels.length - 1) navigate(levels.slice(0, i + 1)) // 逐行注释：根据条件判断是否执行分支。
} // 逐行注释：结束当前代码块或数据结构。
// 函数功能：重置地图到全国层级。
function reset() { // 逐行注释：声明当前函数入口。
  navigate([{ adcode: 100000, name: '全国' }]) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。
defineExpose({ back, goToLevel, reset }) // 逐行注释：执行本行前端逻辑。

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() { // 逐行注释：声明当前函数入口。
  frameId = requestAnimationFrame(animate) // 逐行注释：赋值或更新当前变量/状态。
  // 悬停区域平滑抬升
  for (const r of regions) { // 逐行注释：遍历集合或范围并逐项处理。
    const target = r === hovered ? RAISE : 0 // 逐行注释：声明并初始化当前变量。
    r.group.position.z += (target - r.group.position.z) * 0.18 // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
  controls.update() // 逐行注释：执行本行前端逻辑。
  renderer.render(scene, camera) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() { // 逐行注释：声明当前函数入口。
  const el = container.value // 逐行注释：声明并初始化当前变量。
  if (!el || !renderer) return // 逐行注释：根据条件判断是否执行分支。
  camera.aspect = el.clientWidth / el.clientHeight // 逐行注释：赋值或更新当前变量/状态。
  camera.updateProjectionMatrix() // 逐行注释：执行本行前端逻辑。
  renderer.setSize(el.clientWidth, el.clientHeight) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() { // 逐行注释：声明当前函数入口。
  const el = container.value // 逐行注释：声明并初始化当前变量。
  const w = el.clientWidth // 逐行注释：声明并初始化当前变量。
  const h = el.clientHeight || 600 // 逐行注释：声明并初始化当前变量。

  scene = new THREE.Scene() // 逐行注释：赋值或更新当前变量/状态。
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000) // 逐行注释：赋值或更新当前变量/状态。
  camera.position.set(0, 60, 64) // 逐行注释：执行本行前端逻辑。

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }) // 逐行注释：赋值或更新当前变量/状态。
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 逐行注释：执行本行前端逻辑。
  renderer.setSize(w, h) // 逐行注释：执行本行前端逻辑。
  renderer.setClearColor(0x000000, 0) // 透明，露出大屏背景
  el.appendChild(renderer.domElement) // 逐行注释：执行本行前端逻辑。

  controls = new OrbitControls(camera, renderer.domElement) // 逐行注释：赋值或更新当前变量/状态。
  controls.enableDamping = true // 逐行注释：赋值或更新当前变量/状态。
  controls.dampingFactor = 0.08 // 逐行注释：赋值或更新当前变量/状态。
  controls.minDistance = 28 // 逐行注释：赋值或更新当前变量/状态。
  controls.maxDistance = 180 // 逐行注释：赋值或更新当前变量/状态。
  controls.maxPolarAngle = Math.PI / 2.1 // 逐行注释：赋值或更新当前变量/状态。

  scene.add(new THREE.AmbientLight(0xffffff, 0.9)) // 逐行注释：执行本行前端逻辑。
  const key = new THREE.DirectionalLight(0xa9d8ff, 0.8) // 逐行注释：声明并初始化当前变量。
  key.position.set(10, 80, 40) // 逐行注释：执行本行前端逻辑。
  scene.add(key) // 逐行注释：执行本行前端逻辑。

  raycaster = new THREE.Raycaster() // 逐行注释：赋值或更新当前变量/状态。
  pointer = new THREE.Vector2() // 逐行注释：赋值或更新当前变量/状态。

  renderer.domElement.addEventListener('pointermove', onPointerMove) // 逐行注释：执行本行前端逻辑。
  renderer.domElement.addEventListener('click', onClick) // 逐行注释：执行本行前端逻辑。
  renderer.domElement.addEventListener('pointerleave', () => { // 逐行注释：执行本行前端逻辑。
    tooltip.value.show = false // 逐行注释：赋值或更新当前变量/状态。
    clearHover() // 逐行注释：执行本行前端逻辑。
  }) // 逐行注释：执行本行前端逻辑。
  resizeObserver = new ResizeObserver(onResize) // 逐行注释：赋值或更新当前变量/状态。
  resizeObserver.observe(el) // 逐行注释：执行本行前端逻辑。

  animate() // 逐行注释：执行本行前端逻辑。
  navigate(levels) // 初始加载全国
} // 逐行注释：结束当前代码块或数据结构。

onMounted(initThree) // 逐行注释：注册 Vue 生命周期回调。
watch(() => props.dataMap, applyColors, { deep: true }) // 逐行注释：监听响应式数据变化。

onBeforeUnmount(() => { // 逐行注释：注册 Vue 生命周期回调。
  if (frameId) cancelAnimationFrame(frameId) // 逐行注释：根据条件判断是否执行分支。
  resizeObserver?.disconnect() // 逐行注释：执行本行前端逻辑。
  renderer?.domElement.removeEventListener('pointermove', onPointerMove) // 逐行注释：执行本行前端逻辑。
  renderer?.domElement.removeEventListener('click', onClick) // 逐行注释：执行本行前端逻辑。
  disposeMap() // 逐行注释：执行本行前端逻辑。
  renderer?.dispose() // 逐行注释：执行本行前端逻辑。
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) { // 逐行注释：根据条件判断是否执行分支。
    container.value.removeChild(renderer.domElement) // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。
  scene = camera = renderer = controls = raycaster = pointer = null // 逐行注释：赋值或更新当前变量/状态。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString()) // 逐行注释：声明并初始化当前变量。
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
.geo-map { /* 逐行注释：开始当前样式规则块。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
  width: 100%; /* 逐行注释：设置当前样式属性。 */
  height: 100%; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.canvas-host { /* 逐行注释：开始当前样式规则块。 */
  width: 100%; /* 逐行注释：设置当前样式属性。 */
  height: 100%; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.overlay { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  top: 14px; /* 逐行注释：设置当前样式属性。 */
  left: 50%; /* 逐行注释：设置当前样式属性。 */
  transform: translateX(-50%); /* 逐行注释：设置当前样式属性。 */
  color: #9fd6ff; /* 逐行注释：设置当前样式属性。 */
  font-size: 14px; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 8px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.spin { /* 逐行注释：开始当前样式规则块。 */
  width: 14px; /* 逐行注释：设置当前样式属性。 */
  height: 14px; /* 逐行注释：设置当前样式属性。 */
  border: 2px solid rgba(95, 233, 255, 0.3); /* 逐行注释：设置当前样式属性。 */
  border-top-color: #5fe9ff; /* 逐行注释：设置当前样式属性。 */
  border-radius: 50%; /* 逐行注释：设置当前样式属性。 */
  animation: spin 0.8s linear infinite; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
@keyframes spin { /* 逐行注释：开始当前样式规则块。 */
  to { /* 逐行注释：开始当前样式规则块。 */
    transform: rotate(360deg); /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
} /* 逐行注释：结束当前样式规则块。 */
.tip { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  pointer-events: none; /* 逐行注释：设置当前样式属性。 */
  background: rgba(7, 25, 50, 0.92); /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(95, 233, 255, 0.5); /* 逐行注释：设置当前样式属性。 */
  border-radius: 8px; /* 逐行注释：设置当前样式属性。 */
  padding: 10px 14px; /* 逐行注释：设置当前样式属性。 */
  color: #dbeeff; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  z-index: 5; /* 逐行注释：设置当前样式属性。 */
  min-width: 150px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.tip-name { /* 逐行注释：开始当前样式规则块。 */
  font-size: 15px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
  color: #fff; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 4px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.tip-row b { /* 逐行注释：开始当前样式规则块。 */
  color: #5fe9ff; /* 逐行注释：设置当前样式属性。 */
  font-size: 15px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.tip-hint { /* 逐行注释：开始当前样式规则块。 */
  margin-top: 4px; /* 逐行注释：设置当前样式属性。 */
  color: #ffd166; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
