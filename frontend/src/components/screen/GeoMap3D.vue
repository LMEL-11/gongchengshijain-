<!-- 文件功能：渲染全国、省、市多层级 3D 地图并处理钻取、返回和悬停交互。 -->
<script setup>
import { geoMercator } from '@/utils/projection' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import * as THREE from 'three' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { OrbitControls } from 'three/addons/controls/OrbitControls.js' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { onBeforeUnmount, onMounted, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { fetchArea, normalizeName } from '@/utils/geo' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  // { 规范化区域名: 数值 }，用于给区域着色
  dataMap: { type: Object, default: () => ({}) }, // 声明dataMap字段，作为组件配置、请求参数或图表数据的一部分。
  valueLabel: { type: String, default: '二手房挂牌量' }, // 声明valueLabel字段，作为组件配置、请求参数或图表数据的一部分。
  unit: { type: String, default: '套' }, // 声明unit字段，作为组件配置、请求参数或图表数据的一部分。
  leafClickLabel: { type: String, default: '' }, // 声明leafClickLabel字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。
const emit = defineEmits(['levelchange', 'regionclick']) // 保存emit相关业务数据，作为后续计算、渲染或请求的输入。

const container = ref(null) // 创建container响应式状态，用于驱动页面渲染、表单输入或接口参数。
const loading = ref(false) // 创建加载状态，用于驱动页面渲染、表单输入或接口参数。
const tooltip = ref({ // 创建tooltip响应式状态，用于驱动页面渲染、表单输入或接口参数。
  show: false, // 声明show字段，作为组件配置、请求参数或图表数据的一部分。
  x: 0, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
  y: 0, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
  name: '', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
  value: null, // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
  drillable: false, // 声明drillable字段，作为组件配置、请求参数或图表数据的一部分。
  leafHint: '', // 声明leafHint字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// --- 非响应式 Three 对象 ---
let scene, camera, renderer, controls, raycaster, pointer // 保存scene相关业务数据，作为后续计算、渲染或请求的输入。
let mapGroup = null // 保存mapGroup相关业务数据，作为后续计算、渲染或请求的输入。
let regions = [] // { group, meshes:[], capMat, meta }
let pickMeshes = [] // 保存pickMeshes相关业务数据，作为后续计算、渲染或请求的输入。
let hovered = null // 保存hovered相关业务数据，作为后续计算、渲染或请求的输入。
let frameId = null // 保存frameId相关业务数据，作为后续计算、渲染或请求的输入。
let resizeObserver = null // 保存resizeObserver相关业务数据，作为后续计算、渲染或请求的输入。

let levels = [{ adcode: 100000, name: '全国' }] // 保存levels相关业务数据，作为后续计算、渲染或请求的输入。

const FIT = 38 // 投影适配半径
const DEPTH = 2.4 // 立体厚度
const RAISE = 1.6 // 悬停抬升
const NEUTRAL = new THREE.Color('#1e3a5f') // 保存NEUTRAL相关业务数据，作为后续计算、渲染或请求的输入。
const LOW = new THREE.Color('#16407a') // 保存LOW相关业务数据，作为后续计算、渲染或请求的输入。
const HIGH = new THREE.Color('#3fe0ff') // 保存HIGH相关业务数据，作为后续计算、渲染或请求的输入。

// props.dataMap 是“规范化区域名 -> 指标值”，颜色表达的是当前地图层级内的相对高低。
// 函数功能：根据数值和层级计算地图区域颜色。
function colorFor(t) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return new THREE.Color().lerpColors(LOW, HIGH, Math.max(0, Math.min(1, t))) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：将大数值压缩为适合地图标签的短文本。
function compactValue(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (typeof value !== 'number') return '' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (value >= 10000) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    const text = (value / 10000).toFixed(value >= 100000 ? 0 : 1).replace(/\.0$/, '') // 保存text相关业务数据，作为后续计算、渲染或请求的输入。
    return `${text}万${props.unit}` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return `${Number(value).toLocaleString()}${props.unit}` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：绘制 3D 地图标签所需的 Canvas 纹理。
function makeLabelTexture(text, value = null) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const canvas = document.createElement('canvas') // 保存canvas相关业务数据，作为后续计算、渲染或请求的输入。
  canvas.width = 320 // 更新canvas.width对应的页面状态，使界面展示与最新业务数据一致。
  canvas.height = 104 // 更新canvas.height对应的页面状态，使界面展示与最新业务数据一致。
  const ctx = canvas.getContext('2d') // 保存ctx相关业务数据，作为后续计算、渲染或请求的输入。
  ctx.textAlign = 'center' // 更新ctx.textAlign对应的页面状态，使界面展示与最新业务数据一致。
  ctx.textBaseline = 'middle' // 更新ctx.textBaseline对应的页面状态，使界面展示与最新业务数据一致。
  ctx.shadowColor = 'rgba(0,40,80,0.9)' // 更新ctx.shadowColor对应的页面状态，使界面展示与最新业务数据一致。
  ctx.shadowBlur = 8 // 更新ctx.shadowBlur对应的页面状态，使界面展示与最新业务数据一致。

  const valueText = compactValue(value) // 保存valueText相关业务数据，作为后续计算、渲染或请求的输入。
  ctx.font = 'bold 29px "Microsoft YaHei", sans-serif' // 更新ctx.font对应的页面状态，使界面展示与最新业务数据一致。
  ctx.fillStyle = '#eaf6ff' // 更新ctx.fillStyle对应的页面状态，使界面展示与最新业务数据一致。
  ctx.fillText(text, 160, valueText ? 34 : 52) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  if (valueText) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    ctx.font = 'bold 24px "Microsoft YaHei", sans-serif' // 更新ctx.font对应的页面状态，使界面展示与最新业务数据一致。
    ctx.fillStyle = '#5fe9ff' // 更新ctx.fillStyle对应的页面状态，使界面展示与最新业务数据一致。
    ctx.fillText(valueText, 160, 74) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  const tex = new THREE.CanvasTexture(canvas) // 保存tex相关业务数据，作为后续计算、渲染或请求的输入。
  tex.minFilter = THREE.LinearFilter // 更新tex.minFilter对应的页面状态，使界面展示与最新业务数据一致。
  return tex // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text, value = null) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const tex = makeLabelTexture(text, value) // 保存tex相关业务数据，作为后续计算、渲染或请求的输入。
  const sprite = new THREE.Sprite( // 保存sprite相关业务数据，作为后续计算、渲染或请求的输入。
    new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ) // 完成当前参数、配置或响应式数据结构的组装。
  sprite.scale.set(8.5, 2.75, 1) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  sprite.renderOrder = 10 // 更新sprite.renderOrder对应的页面状态，使界面展示与最新业务数据一致。
  return sprite // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据相机距离更新标签可见性和缩放。
function updateLabel(meta) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!meta.label) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const key = `${meta.name}:${meta.value ?? ''}` // 保存key相关业务数据，作为后续计算、渲染或请求的输入。
  if (meta.labelKey === key) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const oldMap = meta.label.material.map // 保存oldMap相关业务数据，作为后续计算、渲染或请求的输入。
  meta.label.material.map = makeLabelTexture(meta.name, meta.value) // 更新meta.label.material.map对应的页面状态，使界面展示与最新业务数据一致。
  meta.label.material.needsUpdate = true // 更新meta.label.material.needsUpdate对应的页面状态，使界面展示与最新业务数据一致。
  oldMap?.dispose?.() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  meta.labelKey = key // 更新meta.labelKey对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：释放当前 3D 地图对象及其材质资源。
function disposeMap() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!mapGroup) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  mapGroup.traverse((o) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    o.geometry?.dispose?.() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    if (Array.isArray(o.material)) o.material.forEach((m) => m.dispose()) // 根据当前状态、接口结果或用户输入选择对应交互路径。
    else if (o.material) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      o.material.map?.dispose?.() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      o.material.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  scene.remove(mapGroup) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  mapGroup = null // 更新mapGroup对应的页面状态，使界面展示与最新业务数据一致。
  regions = [] // 更新regions对应的页面状态，使界面展示与最新业务数据一致。
  pickMeshes = [] // 更新pickMeshes对应的页面状态，使界面展示与最新业务数据一致。
  hovered = null // 更新hovered对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据 GeoJSON 和统计数据构建当前层级 3D 地图。
function buildMap(features) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  disposeMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  // DataV GeoJSON 仍是经纬度坐标，先 fit 到固定视觉范围，再转成 Three.js 平面坐标。
  const projection = geoMercator().fitExtent( // 保存projection相关业务数据，作为后续计算、渲染或请求的输入。
    [ // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      [-FIT, -FIT], // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      [FIT, FIT], // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    ], // 完成当前参数、配置或响应式数据结构的组装。
    { type: 'FeatureCollection', features }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ) // 完成当前参数、配置或响应式数据结构的组装。
  // 函数功能：将经纬度坐标投影到当前地图平面坐标。
  const project = ([lng, lat]) => { // 保存project相关业务数据，作为后续计算、渲染或请求的输入。
    const p = projection([lng, lat]) // 保存p相关业务数据，作为后续计算、渲染或请求的输入。
    return [p[0], -p[1]] // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  } // 完成当前参数、配置或响应式数据结构的组装。

  mapGroup = new THREE.Group() // 更新mapGroup对应的页面状态，使界面展示与最新业务数据一致。
  mapGroup.rotation.x = -Math.PI / 2 // 平铺：局部 z -> 世界 +y（高度）

  const sideMat = new THREE.MeshStandardMaterial({ // 保存sideMat相关业务数据，作为后续计算、渲染或请求的输入。
    color: '#0c2747', // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
    metalness: 0.4, // 声明metalness字段，作为组件配置、请求参数或图表数据的一部分。
    roughness: 0.55, // 声明roughness字段，作为组件配置、请求参数或图表数据的一部分。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  const outlineMat = new THREE.LineBasicMaterial({ color: '#5fe9ff', transparent: true, opacity: 0.9 }) // 保存outlineMat相关业务数据，作为后续计算、渲染或请求的输入。

  for (const feature of features) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    const polygons = // 保存polygons相关业务数据，作为后续计算、渲染或请求的输入。
      feature.geometry.type === 'Polygon' // 更新feature.geometry.type对应的页面状态，使界面展示与最新业务数据一致。
        ? [feature.geometry.coordinates] // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        : feature.geometry.coordinates // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

    const group = new THREE.Group() // 保存group相关业务数据，作为后续计算、渲染或请求的输入。
    const capMat = new THREE.MeshStandardMaterial({ // 保存capMat相关业务数据，作为后续计算、渲染或请求的输入。
      color: NEUTRAL.clone(), // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
      metalness: 0.25, // 声明metalness字段，作为组件配置、请求参数或图表数据的一部分。
      roughness: 0.7, // 声明roughness字段，作为组件配置、请求参数或图表数据的一部分。
    }) // 完成当前参数、配置或响应式数据结构的组装。
    // meta 统一保存地图区域的业务信息和 Three.js 对象引用，点击/悬停/着色都复用它。
    const meta = { // 保存meta相关业务数据，作为后续计算、渲染或请求的输入。
      name: feature.properties.name, // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      normName: normalizeName(feature.properties.name), // 声明normName字段，作为组件配置、请求参数或图表数据的一部分。
      adcode: feature.properties.adcode, // 声明adcode字段，作为组件配置、请求参数或图表数据的一部分。
      childrenNum: feature.properties.childrenNum ?? 0, // 声明childrenNum字段，作为组件配置、请求参数或图表数据的一部分。
      value: null, // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
      group, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      label: null, // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
      labelKey: '', // 声明labelKey字段，作为组件配置、请求参数或图表数据的一部分。
    } // 完成当前参数、配置或响应式数据结构的组装。
    const meshes = [] // 保存meshes相关业务数据，作为后续计算、渲染或请求的输入。

    for (const poly of polygons) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
      const outer = poly[0] // 保存outer相关业务数据，作为后续计算、渲染或请求的输入。
      const shape = new THREE.Shape() // 保存shape相关业务数据，作为后续计算、渲染或请求的输入。
      outer.forEach((c, i) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
        const [x, y] = project(c) // 保存[x相关业务数据，作为后续计算、渲染或请求的输入。
        i === 0 ? shape.moveTo(x, y) : shape.lineTo(x, y) // 更新i对应的页面状态，使界面展示与最新业务数据一致。
      }) // 完成当前参数、配置或响应式数据结构的组装。
      for (let h = 1; h < poly.length; h++) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
        const path = new THREE.Path() // 保存path相关业务数据，作为后续计算、渲染或请求的输入。
        poly[h].forEach((c, i) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
          const [x, y] = project(c) // 保存[x相关业务数据，作为后续计算、渲染或请求的输入。
          i === 0 ? path.moveTo(x, y) : path.lineTo(x, y) // 更新i对应的页面状态，使界面展示与最新业务数据一致。
        }) // 完成当前参数、配置或响应式数据结构的组装。
        shape.holes.push(path) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      } // 完成当前参数、配置或响应式数据结构的组装。

      const geom = new THREE.ExtrudeGeometry(shape, { depth: DEPTH, bevelEnabled: false }) // 保存geom相关业务数据，作为后续计算、渲染或请求的输入。
      const mesh = new THREE.Mesh(geom, [capMat, sideMat]) // 0=顶/底面 1=侧壁
      mesh.userData.meta = meta // 更新mesh.userData.meta对应的页面状态，使界面展示与最新业务数据一致。
      group.add(mesh) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      meshes.push(mesh) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      pickMeshes.push(mesh) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

      // 顶部发光轮廓
      const pts = outer.map((c) => { // 保存pts相关业务数据，作为后续计算、渲染或请求的输入。
        const [x, y] = project(c) // 保存[x相关业务数据，作为后续计算、渲染或请求的输入。
        return new THREE.Vector3(x, y, DEPTH + 0.02) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
      }) // 完成当前参数、配置或响应式数据结构的组装。
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), outlineMat) // 保存line相关业务数据，作为后续计算、渲染或请求的输入。
      line.raycast = () => {} // 更新line.raycast对应的页面状态，使界面展示与最新业务数据一致。
      group.add(line) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。

    // 标签置于质心上方
    const c = feature.properties.centroid || feature.properties.center // 保存c相关业务数据，作为后续计算、渲染或请求的输入。
    if (c) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      const [lx, ly] = project(c) // 保存[lx相关业务数据，作为后续计算、渲染或请求的输入。
      const label = makeLabel(feature.properties.name) // 保存label相关业务数据，作为后续计算、渲染或请求的输入。
      label.position.set(lx, ly, DEPTH + 0.8) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      meta.label = label // 更新meta.label对应的页面状态，使界面展示与最新业务数据一致。
      group.add(label) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。

    meta.capMat = capMat // 更新meta.capMat对应的页面状态，使界面展示与最新业务数据一致。
    meta.meshes = meshes // 更新meta.meshes对应的页面状态，使界面展示与最新业务数据一致。
    regions.push(meta) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    mapGroup.add(group) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  scene.add(mapGroup) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  applyColors() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  controls.target.set(0, 0, 0) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 依据 dataMap 给区域着色
// 函数功能：根据数据指标刷新地图区域颜色。
function applyColors() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!regions.length) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  // 每次数据或层级变化都按当前可见区域重新归一化，避免全国和城市级数值跨度互相干扰。
  const values = regions // 保存values相关业务数据，作为后续计算、渲染或请求的输入。
    .map((r) => props.dataMap[r.normName] ?? props.dataMap[r.name]) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .filter((v) => typeof v === 'number') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const min = values.length ? Math.min(...values) : 0 // 保存min相关业务数据，作为后续计算、渲染或请求的输入。
  const max = values.length ? Math.max(...values) : 1 // 保存max相关业务数据，作为后续计算、渲染或请求的输入。
  const span = max - min || 1 // 保存span相关业务数据，作为后续计算、渲染或请求的输入。
  for (const r of regions) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    const v = props.dataMap[r.normName] ?? props.dataMap[r.name] // 保存v相关业务数据，作为后续计算、渲染或请求的输入。
    r.value = typeof v === 'number' ? v : null // 更新r.value对应的页面状态，使界面展示与最新业务数据一致。
    r.capMat.color.copy(r.value == null ? NEUTRAL : colorFor((r.value - min) / span)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    updateLabel(r) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(meta) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  hovered = meta // 更新hovered对应的页面状态，使界面展示与最新业务数据一致。
  meta.capMat.emissive = new THREE.Color('#1d6fa5') // 更新meta.capMat.emissive对应的页面状态，使界面展示与最新业务数据一致。
  meta.capMat.emissiveIntensity = 0.6 // 更新meta.capMat.emissiveIntensity对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (hovered) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    hovered.capMat.emissive = new THREE.Color('#000000') // 更新hovered.capMat.emissive对应的页面状态，使界面展示与最新业务数据一致。
    hovered = null // 更新hovered对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(e) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const rect = renderer.domElement.getBoundingClientRect() // 保存rect相关业务数据，作为后续计算、渲染或请求的输入。
  pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1 // 更新pointer.x对应的页面状态，使界面展示与最新业务数据一致。
  pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1 // 更新pointer.y对应的页面状态，使界面展示与最新业务数据一致。
  raycaster.setFromCamera(pointer, camera) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const hits = raycaster.intersectObjects(pickMeshes, false) // 保存hits相关业务数据，作为后续计算、渲染或请求的输入。
  if (hits.length) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    const meta = hits[0].object.userData.meta // 保存meta相关业务数据，作为后续计算、渲染或请求的输入。
    if (hovered !== meta) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      clearHover() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      setHover(meta) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
    tooltip.value = { // 更新tooltip.value对应的页面状态，使界面展示与最新业务数据一致。
      show: true, // 声明show字段，作为组件配置、请求参数或图表数据的一部分。
      x: e.clientX - rect.left, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
      y: e.clientY - rect.top, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
      name: meta.name, // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      value: meta.value, // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
      drillable: meta.childrenNum > 0, // 声明drillable字段，作为组件配置、请求参数或图表数据的一部分。
      leafHint: meta.childrenNum > 0 ? '' : props.leafClickLabel, // 声明leafHint字段，作为组件配置、请求参数或图表数据的一部分。
    } // 完成当前参数、配置或响应式数据结构的组装。
    renderer.domElement.style.cursor = meta.childrenNum > 0 || props.leafClickLabel ? 'pointer' : 'default' // 更新renderer.domElement.style.cursor对应的页面状态，使界面展示与最新业务数据一致。
  } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    clearHover() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    tooltip.value.show = false // 更新tooltip.value.show对应的页面状态，使界面展示与最新业务数据一致。
    renderer.domElement.style.cursor = 'grab' // 更新renderer.domElement.style.cursor对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!hovered) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (hovered.childrenNum > 0) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    navigate([...levels, { adcode: hovered.adcode, name: hovered.name }]) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  if (props.leafClickLabel) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    emit('regionclick', { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      name: hovered.name, // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      normName: hovered.normName, // 声明normName字段，作为组件配置、请求参数或图表数据的一部分。
      adcode: hovered.adcode, // 声明adcode字段，作为组件配置、请求参数或图表数据的一部分。
      value: hovered.value, // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
      path: levels.map((l) => ({ ...l })), // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    }) // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：切换到指定地图层级并加载对应区域数据。
async function navigate(newLevels) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  levels = newLevels // 更新levels对应的页面状态，使界面展示与最新业务数据一致。
  const cur = levels[levels.length - 1] // 保存cur相关业务数据，作为后续计算、渲染或请求的输入。
  loading.value = true // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    // 导航时先加载当前 adcode 的下级边界，再把路径抛给父组件刷新排行和指标数据。
    const geo = await fetchArea(cur.adcode) // 保存geo相关业务数据，作为后续计算、渲染或请求的输入。
    buildMap(geo.features) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    emit('levelchange', { adcode: cur.adcode, name: cur.name, path: levels.map((l) => ({ ...l })) }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } catch (err) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    console.error(err) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loading.value = false // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：返回上一级地图层级。
function back() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (levels.length > 1) navigate(levels.slice(0, -1)) // 根据当前状态、接口结果或用户输入选择对应交互路径。
} // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：根据面包屑跳转到指定地图层级。
function goToLevel(i) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (i >= 0 && i < levels.length - 1) navigate(levels.slice(0, i + 1)) // 根据当前状态、接口结果或用户输入选择对应交互路径。
} // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：重置地图到全国层级。
function reset() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  navigate([{ adcode: 100000, name: '全国' }]) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。
defineExpose({ back, goToLevel, reset }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  frameId = requestAnimationFrame(animate) // 更新frameId对应的页面状态，使界面展示与最新业务数据一致。
  // 悬停区域平滑抬升
  for (const r of regions) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    const target = r === hovered ? RAISE : 0 // 保存target相关业务数据，作为后续计算、渲染或请求的输入。
    r.group.position.z += (target - r.group.position.z) * 0.18 // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  controls.update() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.render(scene, camera) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const el = container.value // 保存el相关业务数据，作为后续计算、渲染或请求的输入。
  if (!el || !renderer) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  camera.aspect = el.clientWidth / el.clientHeight // 更新camera.aspect对应的页面状态，使界面展示与最新业务数据一致。
  camera.updateProjectionMatrix() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.setSize(el.clientWidth, el.clientHeight) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const el = container.value // 保存el相关业务数据，作为后续计算、渲染或请求的输入。
  const w = el.clientWidth // 保存w相关业务数据，作为后续计算、渲染或请求的输入。
  const h = el.clientHeight || 600 // 保存h相关业务数据，作为后续计算、渲染或请求的输入。

  scene = new THREE.Scene() // 更新scene对应的页面状态，使界面展示与最新业务数据一致。
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000) // 更新camera对应的页面状态，使界面展示与最新业务数据一致。
  camera.position.set(0, 60, 64) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }) // 更新renderer对应的页面状态，使界面展示与最新业务数据一致。
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.setSize(w, h) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.setClearColor(0x000000, 0) // 透明，露出大屏背景
  el.appendChild(renderer.domElement) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  controls = new OrbitControls(camera, renderer.domElement) // 更新controls对应的页面状态，使界面展示与最新业务数据一致。
  controls.enableDamping = true // 更新controls.enableDamping对应的页面状态，使界面展示与最新业务数据一致。
  controls.dampingFactor = 0.08 // 更新controls.dampingFactor对应的页面状态，使界面展示与最新业务数据一致。
  controls.minDistance = 28 // 更新controls.minDistance对应的页面状态，使界面展示与最新业务数据一致。
  controls.maxDistance = 180 // 更新controls.maxDistance对应的页面状态，使界面展示与最新业务数据一致。
  controls.maxPolarAngle = Math.PI / 2.1 // 更新controls.maxPolarAngle对应的页面状态，使界面展示与最新业务数据一致。

  scene.add(new THREE.AmbientLight(0xffffff, 0.9)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const key = new THREE.DirectionalLight(0xa9d8ff, 0.8) // 保存key相关业务数据，作为后续计算、渲染或请求的输入。
  key.position.set(10, 80, 40) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  scene.add(key) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  raycaster = new THREE.Raycaster() // 更新raycaster对应的页面状态，使界面展示与最新业务数据一致。
  pointer = new THREE.Vector2() // 更新pointer对应的页面状态，使界面展示与最新业务数据一致。

  renderer.domElement.addEventListener('pointermove', onPointerMove) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.domElement.addEventListener('click', onClick) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.domElement.addEventListener('pointerleave', () => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    tooltip.value.show = false // 更新tooltip.value.show对应的页面状态，使界面展示与最新业务数据一致。
    clearHover() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  resizeObserver = new ResizeObserver(onResize) // 更新resizeObserver对应的页面状态，使界面展示与最新业务数据一致。
  resizeObserver.observe(el) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  animate() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  navigate(levels) // 初始加载全国
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(initThree) // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
watch(() => props.dataMap, applyColors, { deep: true }) // 监听响应式数据变化，并在变化后同步关联选项或视图状态。

onBeforeUnmount(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  if (frameId) cancelAnimationFrame(frameId) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  resizeObserver?.disconnect() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer?.domElement.removeEventListener('pointermove', onPointerMove) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer?.domElement.removeEventListener('click', onClick) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  disposeMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer?.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    container.value.removeChild(renderer.domElement) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  scene = camera = renderer = controls = raycaster = pointer = null // 更新scene对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString()) // 保存fmt相关业务数据，作为后续计算、渲染或请求的输入。
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
.geo-map { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: relative; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.canvas-host { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.overlay { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  top: 14px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  left: 50%; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  transform: translateX(-50%); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #9fd6ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 14px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.spin { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border: 2px solid rgba(95, 233, 255, 0.3); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-top-color: #5fe9ff; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border-radius: 50%; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  animation: spin 0.8s linear infinite; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
@keyframes spin { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  to { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    transform: rotate(360deg); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.tip { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  pointer-events: none; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(7, 25, 50, 0.92); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border: 1px solid rgba(95, 233, 255, 0.5); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 8px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 10px 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  color: #dbeeff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  z-index: 5; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  min-width: 150px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.tip-name { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  margin-bottom: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.tip-row b { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #5fe9ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.tip-hint { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-top: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #ffd166; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
