<!-- 文件功能：渲染全国、省、市多层级 3D 地图并处理钻取、返回和悬停交互。 -->
<script setup>
import { geoMercator } from '@/utils/projection' // 导入 { geoMercator }，供当前前端模块渲染或交互逻辑使用。
import * as THREE from 'three' // 导入 * as THREE，供当前前端模块渲染或交互逻辑使用。
import { OrbitControls } from 'three/addons/controls/OrbitControls.js' // 导入 { OrbitControls }，供当前前端模块渲染或交互逻辑使用。
import { onBeforeUnmount, onMounted, ref, watch } from 'vue' // 导入 { onBeforeUnmount, onMounted, ref, watch }，供当前前端模块渲染或交互逻辑使用。

import { fetchArea, normalizeName } from '@/utils/geo' // 导入 { fetchArea, normalizeName }，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  // { 规范化区域名: 数值 }，用于给区域着色
  dataMap: { type: Object, default: () => ({}) }, // 设置 dataMap: { type: Object, default:  的值，作为后续渲染、计算或请求的输入。
  valueLabel: { type: String, default: '二手房挂牌量' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  unit: { type: String, default: '套' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  leafClickLabel: { type: String, default: '' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。
const emit = defineEmits(['levelchange', 'regionclick']) // 创建 emit，用于保存页面状态、计算结果或接口参数。

const container = ref(null) // 创建 container，用于保存页面状态、计算结果或接口参数。
const loading = ref(false) // 创建 loading，用于保存页面状态、计算结果或接口参数。
const tooltip = ref({ // 创建 tooltip，用于保存页面状态、计算结果或接口参数。
  show: false, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  x: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  y: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  name: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  value: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  drillable: false, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  leafHint: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// --- 非响应式 Three 对象 ---
let scene, camera, renderer, controls, raycaster, pointer // 创建 scene, camera, renderer, controls, raycaster, pointer，用于保存页面状态、计算结果或接口参数。
let mapGroup = null // 创建 mapGroup，用于保存页面状态、计算结果或接口参数。
let regions = [] // 创建 regions，用于保存页面状态、计算结果或接口参数。
let pickMeshes = [] // 创建 pickMeshes，用于保存页面状态、计算结果或接口参数。
let hovered = null // 创建 hovered，用于保存页面状态、计算结果或接口参数。
let frameId = null // 创建 frameId，用于保存页面状态、计算结果或接口参数。
let resizeObserver = null // 创建 resizeObserver，用于保存页面状态、计算结果或接口参数。

let levels = [{ adcode: 100000, name: '全国' }] // 创建 levels，用于保存页面状态、计算结果或接口参数。

const FIT = 38 // 创建 FIT，用于保存页面状态、计算结果或接口参数。
const DEPTH = 2.4 // 创建 DEPTH，用于保存页面状态、计算结果或接口参数。
const RAISE = 1.6 // 创建 RAISE，用于保存页面状态、计算结果或接口参数。
const NEUTRAL = new THREE.Color('#1e3a5f') // 创建 NEUTRAL，用于保存页面状态、计算结果或接口参数。
const LOW = new THREE.Color('#16407a') // 创建 LOW，用于保存页面状态、计算结果或接口参数。
const HIGH = new THREE.Color('#3fe0ff') // 创建 HIGH，用于保存页面状态、计算结果或接口参数。

// props.dataMap 是“规范化区域名 -> 指标值”，颜色表达的是当前地图层级内的相对高低。
// 函数功能：根据数值和层级计算地图区域颜色。
function colorFor(t) { // 定义 colorFor 函数，处理页面交互、数据加载或状态同步。
  return new THREE.Color().lerpColors(LOW, HIGH, Math.max(0, Math.min(1, t))) // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：将大数值压缩为适合地图标签的短文本。
function compactValue(value) { // 定义 compactValue 函数，处理页面交互、数据加载或状态同步。
  if (typeof value !== 'number') return '' // 根据当前页面状态或接口结果决定是否进入该分支。
  if (value >= 10000) { // 根据当前页面状态或接口结果决定是否进入该分支。
    const text = (value / 10000).toFixed(value >= 100000 ? 0 : 1).replace(/\.0$/, '') // 创建 text，用于保存页面状态、计算结果或接口参数。
    return `${text}万${props.unit}` // 返回整理后的数据、组件配置或渲染结果。
  } // 结束当前函数、对象、数组或组件配置块。
  return `${Number(value).toLocaleString()}${props.unit}` // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：绘制 3D 地图标签所需的 Canvas 纹理。
function makeLabelTexture(text, value = null) { // 定义 makeLabelTexture 函数，处理页面交互、数据加载或状态同步。
  const canvas = document.createElement('canvas') // 创建 canvas，用于保存页面状态、计算结果或接口参数。
  canvas.width = 320 // 设置 canvas.width 的值，作为后续渲染、计算或请求的输入。
  canvas.height = 104 // 设置 canvas.height 的值，作为后续渲染、计算或请求的输入。
  const ctx = canvas.getContext('2d') // 创建 ctx，用于保存页面状态、计算结果或接口参数。
  ctx.textAlign = 'center' // 设置 ctx.textAlign 的值，作为后续渲染、计算或请求的输入。
  ctx.textBaseline = 'middle' // 设置 ctx.textBaseline 的值，作为后续渲染、计算或请求的输入。
  ctx.shadowColor = 'rgba(0,40,80,0.9)' // 设置 ctx.shadowColor 的值，作为后续渲染、计算或请求的输入。
  ctx.shadowBlur = 8 // 设置 ctx.shadowBlur 的值，作为后续渲染、计算或请求的输入。

  const valueText = compactValue(value) // 创建 valueText，用于保存页面状态、计算结果或接口参数。
  ctx.font = 'bold 29px "Microsoft YaHei", sans-serif' // 设置 ctx.font 的值，作为后续渲染、计算或请求的输入。
  ctx.fillStyle = '#eaf6ff' // 设置 ctx.fillStyle 的值，作为后续渲染、计算或请求的输入。
  ctx.fillText(text, 160, valueText ? 34 : 52) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  if (valueText) { // 根据当前页面状态或接口结果决定是否进入该分支。
    ctx.font = 'bold 24px "Microsoft YaHei", sans-serif' // 设置 ctx.font 的值，作为后续渲染、计算或请求的输入。
    ctx.fillStyle = '#5fe9ff' // 设置 ctx.fillStyle 的值，作为后续渲染、计算或请求的输入。
    ctx.fillText(valueText, 160, 74) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  const tex = new THREE.CanvasTexture(canvas) // 创建 tex，用于保存页面状态、计算结果或接口参数。
  tex.minFilter = THREE.LinearFilter // 设置 tex.minFilter 的值，作为后续渲染、计算或请求的输入。
  return tex // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text, value = null) { // 定义 makeLabel 函数，处理页面交互、数据加载或状态同步。
  const tex = makeLabelTexture(text, value) // 创建 tex，用于保存页面状态、计算结果或接口参数。
  const sprite = new THREE.Sprite( // 创建 sprite，用于保存页面状态、计算结果或接口参数。
    new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ) // 结束当前函数、对象、数组或组件配置块。
  sprite.scale.set(8.5, 2.75, 1) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  sprite.renderOrder = 10 // 设置 sprite.renderOrder 的值，作为后续渲染、计算或请求的输入。
  return sprite // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据相机距离更新标签可见性和缩放。
function updateLabel(meta) { // 定义 updateLabel 函数，处理页面交互、数据加载或状态同步。
  if (!meta.label) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const key = `${meta.name}:${meta.value ?? ''}` // 创建 key，用于保存页面状态、计算结果或接口参数。
  if (meta.labelKey === key) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const oldMap = meta.label.material.map // 创建 oldMap，用于保存页面状态、计算结果或接口参数。
  meta.label.material.map = makeLabelTexture(meta.name, meta.value) // 更新 meta.label.material.map 响应式状态，让页面展示与最新数据保持一致。
  meta.label.material.needsUpdate = true // 设置 meta.label.material.needsUpdate 的值，作为后续渲染、计算或请求的输入。
  oldMap?.dispose?.() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  meta.labelKey = key // 设置 meta.labelKey 的值，作为后续渲染、计算或请求的输入。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：释放当前 3D 地图对象及其材质资源。
function disposeMap() { // 定义 disposeMap 函数，处理页面交互、数据加载或状态同步。
  if (!mapGroup) return // 根据当前页面状态或接口结果决定是否进入该分支。
  mapGroup.traverse((o) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    o.geometry?.dispose?.() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose()) // 根据当前页面状态或接口结果决定是否进入该分支。
    else if (o.material) { // 处理前面条件未命中的前端交互分支。
      o.material.map?.dispose?.() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      o.material.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
  }) // 结束当前函数、对象、数组或组件配置块。
  scene.remove(mapGroup) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  mapGroup = null // 设置 mapGroup 的值，作为后续渲染、计算或请求的输入。
  regions = [] // 设置 regions 的值，作为后续渲染、计算或请求的输入。
  pickMeshes = [] // 设置 pickMeshes 的值，作为后续渲染、计算或请求的输入。
  hovered = null // 设置 hovered 的值，作为后续渲染、计算或请求的输入。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据 GeoJSON 和统计数据构建当前层级 3D 地图。
function buildMap(features) { // 定义 buildMap 函数，处理页面交互、数据加载或状态同步。
  disposeMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  // DataV GeoJSON 仍是经纬度坐标，先 fit 到固定视觉范围，再转成 Three.js 平面坐标。
  const projection = geoMercator().fitExtent( // 创建 projection，用于保存页面状态、计算结果或接口参数。
    [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      [-FIT, -FIT], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      [FIT, FIT], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ], // 结束当前函数、对象、数组或组件配置块。
    { type: 'FeatureCollection', features }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ) // 结束当前函数、对象、数组或组件配置块。
  // 函数功能：将经纬度坐标投影到当前地图平面坐标。
  const project = ([lng, lat]) => { // 创建 project，用于保存页面状态、计算结果或接口参数。
    const p = projection([lng, lat]) // 创建 p，用于保存页面状态、计算结果或接口参数。
    return [p[0], -p[1]] // 返回整理后的数据、组件配置或渲染结果。
  } // 结束当前函数、对象、数组或组件配置块。

  mapGroup = new THREE.Group() // 设置 mapGroup 的值，作为后续渲染、计算或请求的输入。
  mapGroup.rotation.x = -Math.PI / 2 // 设置 mapGroup.rotation.x 的值，作为后续渲染、计算或请求的输入。

  const sideMat = new THREE.MeshStandardMaterial({ // 创建 sideMat，用于保存页面状态、计算结果或接口参数。
    color: '#0c2747', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    metalness: 0.4, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    roughness: 0.55, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。
  const outlineMat = new THREE.LineBasicMaterial({ color: '#5fe9ff', transparent: true, opacity: 0.9 }) // 创建 outlineMat，用于保存页面状态、计算结果或接口参数。

  for (const feature of features) { // 遍历当前数据集合，逐项生成页面需要的数据。
    const polygons = // 创建 polygons，用于保存页面状态、计算结果或接口参数。
      feature.geometry.type === 'Polygon' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        ? [feature.geometry.coordinates] // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        : feature.geometry.coordinates // 执行当前前端代码行，推动页面数据和交互流程继续运行。

    const group = new THREE.Group() // 创建 group，用于保存页面状态、计算结果或接口参数。
    const capMat = new THREE.MeshStandardMaterial({ // 创建 capMat，用于保存页面状态、计算结果或接口参数。
      color: NEUTRAL.clone(), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      metalness: 0.25, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      roughness: 0.7, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }) // 结束当前函数、对象、数组或组件配置块。
    // meta 统一保存地图区域的业务信息和 Three.js 对象引用，点击/悬停/着色都复用它。
    const meta = { // 创建 meta，用于保存页面状态、计算结果或接口参数。
      name: feature.properties.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      normName: normalizeName(feature.properties.name), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      adcode: feature.properties.adcode, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      childrenNum: feature.properties.childrenNum ?? 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      value: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      group, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      label: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      labelKey: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    const meshes = [] // 创建 meshes，用于保存页面状态、计算结果或接口参数。

    for (const poly of polygons) { // 遍历当前数据集合，逐项生成页面需要的数据。
      const outer = poly[0] // 创建 outer，用于保存页面状态、计算结果或接口参数。
      const shape = new THREE.Shape() // 创建 shape，用于保存页面状态、计算结果或接口参数。
      outer.forEach((c, i) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
        const [x, y] = project(c) // 创建 [x, y]，用于保存页面状态、计算结果或接口参数。
        i === 0 ? shape.moveTo(x, y) : shape.lineTo(x, y) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      }) // 结束当前函数、对象、数组或组件配置块。
      for (let h = 1; h < poly.length; h++) { // 遍历当前数据集合，逐项生成页面需要的数据。
        const path = new THREE.Path() // 创建 path，用于保存页面状态、计算结果或接口参数。
        poly[h].forEach((c, i) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
          const [x, y] = project(c) // 创建 [x, y]，用于保存页面状态、计算结果或接口参数。
          i === 0 ? path.moveTo(x, y) : path.lineTo(x, y) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        }) // 结束当前函数、对象、数组或组件配置块。
        shape.holes.push(path) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      } // 结束当前函数、对象、数组或组件配置块。

      const geom = new THREE.ExtrudeGeometry(shape, { depth: DEPTH, bevelEnabled: false }) // 创建 geom，用于保存页面状态、计算结果或接口参数。
      const mesh = new THREE.Mesh(geom, [capMat, sideMat]) // 创建 mesh，用于保存页面状态、计算结果或接口参数。
      mesh.userData.meta = meta // 设置 mesh.userData.meta 的值，作为后续渲染、计算或请求的输入。
      group.add(mesh) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      meshes.push(mesh) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      pickMeshes.push(mesh) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

      // 顶部发光轮廓
      const pts = outer.map((c) => { // 创建 pts，用于保存页面状态、计算结果或接口参数。
        const [x, y] = project(c) // 创建 [x, y]，用于保存页面状态、计算结果或接口参数。
        return new THREE.Vector3(x, y, DEPTH + 0.02) // 返回整理后的数据、组件配置或渲染结果。
      }) // 结束当前函数、对象、数组或组件配置块。
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), outlineMat) // 创建 line，用于保存页面状态、计算结果或接口参数。
      line.raycast = () => {} // 定义箭头函数回调，处理异步结果、事件或响应式变化。
      group.add(line) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。

    // 标签置于质心上方
    const c = feature.properties.centroid || feature.properties.center // 创建 c，用于保存页面状态、计算结果或接口参数。
    if (c) { // 根据当前页面状态或接口结果决定是否进入该分支。
      const [lx, ly] = project(c) // 创建 [lx, ly]，用于保存页面状态、计算结果或接口参数。
      const label = makeLabel(feature.properties.name) // 创建 label，用于保存页面状态、计算结果或接口参数。
      label.position.set(lx, ly, DEPTH + 0.8) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      meta.label = label // 设置 meta.label 的值，作为后续渲染、计算或请求的输入。
      group.add(label) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。

    meta.capMat = capMat // 设置 meta.capMat 的值，作为后续渲染、计算或请求的输入。
    meta.meshes = meshes // 设置 meta.meshes 的值，作为后续渲染、计算或请求的输入。
    regions.push(meta) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    mapGroup.add(group) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  scene.add(mapGroup) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  applyColors() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  controls.target.set(0, 0, 0) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 依据 dataMap 给区域着色
// 函数功能：根据数据指标刷新地图区域颜色。
function applyColors() { // 定义 applyColors 函数，处理页面交互、数据加载或状态同步。
  if (!regions.length) return // 根据当前页面状态或接口结果决定是否进入该分支。
  // 每次数据或层级变化都按当前可见区域重新归一化，避免全国和城市级数值跨度互相干扰。
  const values = regions // 创建 values，用于保存页面状态、计算结果或接口参数。
    .map((r) => props.dataMap[r.normName] ?? props.dataMap[r.name]) // 设置 .map((r 的值，作为后续渲染、计算或请求的输入。
    .filter((v) => typeof v === 'number') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const min = values.length ? Math.min(...values) : 0 // 创建 min，用于保存页面状态、计算结果或接口参数。
  const max = values.length ? Math.max(...values) : 1 // 创建 max，用于保存页面状态、计算结果或接口参数。
  const span = max - min || 1 // 创建 span，用于保存页面状态、计算结果或接口参数。
  for (const r of regions) { // 遍历当前数据集合，逐项生成页面需要的数据。
    const v = props.dataMap[r.normName] ?? props.dataMap[r.name] // 创建 v，用于保存页面状态、计算结果或接口参数。
    r.value = typeof v === 'number' ? v : null // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    r.capMat.color.copy(r.value == null ? NEUTRAL : colorFor((r.value - min) / span)) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    updateLabel(r) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(meta) { // 定义 setHover 函数，处理页面交互、数据加载或状态同步。
  hovered = meta // 设置 hovered 的值，作为后续渲染、计算或请求的输入。
  meta.capMat.emissive = new THREE.Color('#1d6fa5') // 设置 meta.capMat.emissive 的值，作为后续渲染、计算或请求的输入。
  meta.capMat.emissiveIntensity = 0.6 // 设置 meta.capMat.emissiveIntensity 的值，作为后续渲染、计算或请求的输入。
} // 结束当前函数、对象、数组或组件配置块。
// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() { // 定义 clearHover 函数，处理页面交互、数据加载或状态同步。
  if (hovered) { // 根据当前页面状态或接口结果决定是否进入该分支。
    hovered.capMat.emissive = new THREE.Color('#000000') // 设置 hovered.capMat.emissive 的值，作为后续渲染、计算或请求的输入。
    hovered = null // 设置 hovered 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(e) { // 定义 onPointerMove 函数，处理页面交互、数据加载或状态同步。
  const rect = renderer.domElement.getBoundingClientRect() // 创建 rect，用于保存页面状态、计算结果或接口参数。
  pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1 // 设置 pointer.x 的值，作为后续渲染、计算或请求的输入。
  pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1 // 设置 pointer.y 的值，作为后续渲染、计算或请求的输入。
  raycaster.setFromCamera(pointer, camera) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const hits = raycaster.intersectObjects(pickMeshes, false) // 创建 hits，用于保存页面状态、计算结果或接口参数。
  if (hits.length) { // 根据当前页面状态或接口结果决定是否进入该分支。
    const meta = hits[0].object.userData.meta // 创建 meta，用于保存页面状态、计算结果或接口参数。
    if (hovered !== meta) { // 根据当前页面状态或接口结果决定是否进入该分支。
      clearHover() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      setHover(meta) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    tooltip.value = { // 更新 tooltip.value 响应式状态，让页面展示与最新数据保持一致。
      show: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      x: e.clientX - rect.left, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      y: e.clientY - rect.top, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: meta.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      value: meta.value, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      drillable: meta.childrenNum > 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      leafHint: meta.childrenNum > 0 ? '' : props.leafClickLabel, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    renderer.domElement.style.cursor = meta.childrenNum > 0 || props.leafClickLabel ? 'pointer' : 'default' // 设置 renderer.domElement.style.cursor 的值，作为后续渲染、计算或请求的输入。
  } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    clearHover() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    tooltip.value.show = false // 更新 tooltip.value.show 响应式状态，让页面展示与最新数据保持一致。
    renderer.domElement.style.cursor = 'grab' // 设置 renderer.domElement.style.cursor 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() { // 定义 onClick 函数，处理页面交互、数据加载或状态同步。
  if (!hovered) return // 根据当前页面状态或接口结果决定是否进入该分支。
  if (hovered.childrenNum > 0) { // 根据当前页面状态或接口结果决定是否进入该分支。
    navigate([...levels, { adcode: hovered.adcode, name: hovered.name }]) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  if (props.leafClickLabel) { // 根据当前页面状态或接口结果决定是否进入该分支。
    emit('regionclick', { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: hovered.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      normName: hovered.normName, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      adcode: hovered.adcode, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      value: hovered.value, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      path: levels.map((l) => ({ ...l })), // 设置 path: levels.map((l 的值，作为后续渲染、计算或请求的输入。
    }) // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：切换到指定地图层级并加载对应区域数据。
async function navigate(newLevels) { // 定义 navigate 函数，处理页面交互、数据加载或状态同步。
  levels = newLevels // 设置 levels 的值，作为后续渲染、计算或请求的输入。
  const cur = levels[levels.length - 1] // 创建 cur，用于保存页面状态、计算结果或接口参数。
  loading.value = true // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // 导航时先加载当前 adcode 的下级边界，再把路径抛给父组件刷新排行和指标数据。
    const geo = await fetchArea(cur.adcode) // 创建 geo，用于保存页面状态、计算结果或接口参数。
    buildMap(geo.features) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    emit('levelchange', { adcode: cur.adcode, name: cur.name, path: levels.map((l) => ({ ...l })) }) // 设置 emit('levelchange', { adcode: cur.adcode, name: cur.name, path: levels.map((l 的值，作为后续渲染、计算或请求的输入。
  } catch (err) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    console.error(err) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loading.value = false // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：返回上一级地图层级。
function back() { // 定义 back 函数，处理页面交互、数据加载或状态同步。
  if (levels.length > 1) navigate(levels.slice(0, -1)) // 根据当前页面状态或接口结果决定是否进入该分支。
} // 结束当前函数、对象、数组或组件配置块。
// 函数功能：根据面包屑跳转到指定地图层级。
function goToLevel(i) { // 定义 goToLevel 函数，处理页面交互、数据加载或状态同步。
  if (i >= 0 && i < levels.length - 1) navigate(levels.slice(0, i + 1)) // 根据当前页面状态或接口结果决定是否进入该分支。
} // 结束当前函数、对象、数组或组件配置块。
// 函数功能：重置地图到全国层级。
function reset() { // 定义 reset 函数，处理页面交互、数据加载或状态同步。
  navigate([{ adcode: 100000, name: '全国' }]) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。
defineExpose({ back, goToLevel, reset }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() { // 定义 animate 函数，处理页面交互、数据加载或状态同步。
  frameId = requestAnimationFrame(animate) // 设置 frameId 的值，作为后续渲染、计算或请求的输入。
  // 悬停区域平滑抬升
  for (const r of regions) { // 遍历当前数据集合，逐项生成页面需要的数据。
    const target = r === hovered ? RAISE : 0 // 创建 target，用于保存页面状态、计算结果或接口参数。
    r.group.position.z += (target - r.group.position.z) * 0.18 // 设置 r.group.position.z + 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
  controls.update() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.render(scene, camera) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() { // 定义 onResize 函数，处理页面交互、数据加载或状态同步。
  const el = container.value // 创建 el，用于保存页面状态、计算结果或接口参数。
  if (!el || !renderer) return // 根据当前页面状态或接口结果决定是否进入该分支。
  camera.aspect = el.clientWidth / el.clientHeight // 设置 camera.aspect 的值，作为后续渲染、计算或请求的输入。
  camera.updateProjectionMatrix() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.setSize(el.clientWidth, el.clientHeight) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() { // 定义 initThree 函数，处理页面交互、数据加载或状态同步。
  const el = container.value // 创建 el，用于保存页面状态、计算结果或接口参数。
  const w = el.clientWidth // 创建 w，用于保存页面状态、计算结果或接口参数。
  const h = el.clientHeight || 600 // 创建 h，用于保存页面状态、计算结果或接口参数。

  scene = new THREE.Scene() // 设置 scene 的值，作为后续渲染、计算或请求的输入。
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000) // 设置 camera 的值，作为后续渲染、计算或请求的输入。
  camera.position.set(0, 60, 64) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }) // 设置 renderer 的值，作为后续渲染、计算或请求的输入。
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.setSize(w, h) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.setClearColor(0x000000, 0) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  el.appendChild(renderer.domElement) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  controls = new OrbitControls(camera, renderer.domElement) // 设置 controls 的值，作为后续渲染、计算或请求的输入。
  controls.enableDamping = true // 设置 controls.enableDamping 的值，作为后续渲染、计算或请求的输入。
  controls.dampingFactor = 0.08 // 设置 controls.dampingFactor 的值，作为后续渲染、计算或请求的输入。
  controls.minDistance = 28 // 设置 controls.minDistance 的值，作为后续渲染、计算或请求的输入。
  controls.maxDistance = 180 // 设置 controls.maxDistance 的值，作为后续渲染、计算或请求的输入。
  controls.maxPolarAngle = Math.PI / 2.1 // 设置 controls.maxPolarAngle 的值，作为后续渲染、计算或请求的输入。

  scene.add(new THREE.AmbientLight(0xffffff, 0.9)) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const key = new THREE.DirectionalLight(0xa9d8ff, 0.8) // 创建 key，用于保存页面状态、计算结果或接口参数。
  key.position.set(10, 80, 40) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  scene.add(key) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  raycaster = new THREE.Raycaster() // 设置 raycaster 的值，作为后续渲染、计算或请求的输入。
  pointer = new THREE.Vector2() // 设置 pointer 的值，作为后续渲染、计算或请求的输入。

  renderer.domElement.addEventListener('pointermove', onPointerMove) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.domElement.addEventListener('click', onClick) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.domElement.addEventListener('pointerleave', () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    tooltip.value.show = false // 更新 tooltip.value.show 响应式状态，让页面展示与最新数据保持一致。
    clearHover() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。
  resizeObserver = new ResizeObserver(onResize) // 设置 resizeObserver 的值，作为后续渲染、计算或请求的输入。
  resizeObserver.observe(el) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  animate() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  navigate(levels) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(initThree) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
watch(() => props.dataMap, applyColors, { deep: true }) // 设置 watch 的值，作为后续渲染、计算或请求的输入。

onBeforeUnmount(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  if (frameId) cancelAnimationFrame(frameId) // 根据当前页面状态或接口结果决定是否进入该分支。
  resizeObserver?.disconnect() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer?.domElement.removeEventListener('pointermove', onPointerMove) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer?.domElement.removeEventListener('click', onClick) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  disposeMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer?.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) { // 根据当前页面状态或接口结果决定是否进入该分支。
    container.value.removeChild(renderer.domElement) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  scene = camera = renderer = controls = raycaster = pointer = null // 设置 scene 的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString()) // 创建 fmt，用于保存页面状态、计算结果或接口参数。
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
.geo-map { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  width: 100%; /* 设置元素宽度。 */
  height: 100%; /* 设置元素高度。 */
} /* 结束当前样式规则块。 */
.canvas-host { /* 定义当前选择器的样式作用域。 */
  width: 100%; /* 设置元素宽度。 */
  height: 100%; /* 设置元素高度。 */
} /* 结束当前样式规则块。 */
.overlay { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  top: 14px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: 50%; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  transform: translateX(-50%); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #9fd6ff; /* 设置文字颜色。 */
  font-size: 14px; /* 设置文字大小。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 8px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.spin { /* 定义当前选择器的样式作用域。 */
  width: 14px; /* 设置元素宽度。 */
  height: 14px; /* 设置元素高度。 */
  border: 2px solid rgba(95, 233, 255, 0.3); /* 设置边框样式。 */
  border-top-color: #5fe9ff; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-radius: 50%; /* 设置圆角半径。 */
  animation: spin 0.8s linear infinite; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
@keyframes spin { /* 定义当前选择器的样式作用域。 */
  to { /* 定义当前选择器的样式作用域。 */
    transform: rotate(360deg); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  } /* 结束当前样式规则块。 */
} /* 结束当前样式规则块。 */
.tip { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  pointer-events: none; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(7, 25, 50, 0.92); /* 设置背景样式。 */
  border: 1px solid rgba(95, 233, 255, 0.5); /* 设置边框样式。 */
  border-radius: 8px; /* 设置圆角半径。 */
  padding: 10px 14px; /* 设置元素内边距。 */
  color: #dbeeff; /* 设置文字颜色。 */
  font-size: 13px; /* 设置文字大小。 */
  z-index: 5; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  min-width: 150px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.tip-name { /* 定义当前选择器的样式作用域。 */
  font-size: 15px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
  color: #fff; /* 设置文字颜色。 */
  margin-bottom: 4px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.tip-row b { /* 定义当前选择器的样式作用域。 */
  color: #5fe9ff; /* 设置文字颜色。 */
  font-size: 15px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.tip-hint { /* 定义当前选择器的样式作用域。 */
  margin-top: 4px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #ffd166; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
</style>
