<!-- 文件功能：渲染城市区域房价 3D 柱状地图，并处理悬停、点击和自适应。 -->
<script setup>
import * as THREE from 'three' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { OrbitControls } from 'three/addons/controls/OrbitControls.js' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { onBeforeUnmount, onMounted, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  districts: { type: Array, default: () => [] }, // 声明districts字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '480px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。
const emit = defineEmits(['select']) // 保存emit相关业务数据，作为后续计算、渲染或请求的输入。

const container = ref(null) // 创建container响应式状态，用于驱动页面渲染、表单输入或接口参数。
const tooltip = ref({ show: false, x: 0, y: 0, name: '', price: 0, count: 0 }) // 创建tooltip响应式状态，用于驱动页面渲染、表单输入或接口参数。
const priceRange = ref({ min: 0, max: 0 }) // 创建priceRange响应式状态，用于驱动页面渲染、表单输入或接口参数。

// --- Three.js objects (intentionally non-reactive plain vars) ---
let scene, camera, renderer, controls, raycaster, pointer // 保存scene相关业务数据，作为后续计算、渲染或请求的输入。
let cityGroup = null // 保存cityGroup相关业务数据，作为后续计算、渲染或请求的输入。
let columns = [] // 保存columns相关业务数据，作为后续计算、渲染或请求的输入。
let hovered = null // 保存hovered相关业务数据，作为后续计算、渲染或请求的输入。
let frameId = null // 保存frameId相关业务数据，作为后续计算、渲染或请求的输入。
let resizeObserver = null // 保存resizeObserver相关业务数据，作为后续计算、渲染或请求的输入。

const SPACING = 6 // 保存SPACING相关业务数据，作为后续计算、渲染或请求的输入。
const BOX = 3.4 // 保存BOX相关业务数据，作为后续计算、渲染或请求的输入。

// Low price → teal, high price → red (matches the legend gradient below).
// 函数功能：按归一化价格生成 3D 柱体颜色。
function colorForT(t) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const hue = THREE.MathUtils.lerp(160, 0, t) / 360 // 保存hue相关业务数据，作为后续计算、渲染或请求的输入。
  return new THREE.Color().setHSL(hue, 0.72, 0.52) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const canvas = document.createElement('canvas') // 保存canvas相关业务数据，作为后续计算、渲染或请求的输入。
  canvas.width = 256 // 更新canvas.width对应的页面状态，使界面展示与最新业务数据一致。
  canvas.height = 64 // 更新canvas.height对应的页面状态，使界面展示与最新业务数据一致。
  const ctx = canvas.getContext('2d') // 保存ctx相关业务数据，作为后续计算、渲染或请求的输入。
  ctx.font = 'bold 40px "PingFang SC", "Microsoft YaHei", sans-serif' // 更新ctx.font对应的页面状态，使界面展示与最新业务数据一致。
  ctx.fillStyle = 'rgba(255,255,255,0.96)' // 更新ctx.fillStyle对应的页面状态，使界面展示与最新业务数据一致。
  ctx.textAlign = 'center' // 更新ctx.textAlign对应的页面状态，使界面展示与最新业务数据一致。
  ctx.textBaseline = 'middle' // 更新ctx.textBaseline对应的页面状态，使界面展示与最新业务数据一致。
  ctx.fillText(text, canvas.width / 2, canvas.height / 2) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const texture = new THREE.CanvasTexture(canvas) // 保存texture相关业务数据，作为后续计算、渲染或请求的输入。
  texture.minFilter = THREE.LinearFilter // 更新texture.minFilter对应的页面状态，使界面展示与最新业务数据一致。
  const sprite = new THREE.Sprite( // 保存sprite相关业务数据，作为后续计算、渲染或请求的输入。
    new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ) // 完成当前参数、配置或响应式数据结构的组装。
  sprite.scale.set(6, 1.5, 1) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  return sprite // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：释放当前 3D 城市柱状图分组及其几何和材质资源。
function disposeGroup() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!cityGroup || !scene) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  scene.remove(cityGroup) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  cityGroup.traverse((obj) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    obj.geometry?.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    if (obj.material) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      obj.material.map?.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      obj.material.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  cityGroup = null // 更新cityGroup对应的页面状态，使界面展示与最新业务数据一致。
  columns = [] // 更新columns对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据区域数据重建 3D 房价柱状图。
function buildColumns() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!scene) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  disposeGroup() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const list = props.districts || [] // 保存list相关业务数据，作为后续计算、渲染或请求的输入。
  if (!list.length) return // 根据当前状态、接口结果或用户输入选择对应交互路径。

  cityGroup = new THREE.Group() // 更新cityGroup对应的页面状态，使界面展示与最新业务数据一致。

  // 真实数据的“区”多为商圈，且无预设网格坐标（grid 全为 0）；此时按序号自动排成近似方阵。
  // 若数据自带有效网格（旧种子数据），则沿用其布局。
  const degenerate = list.every((d) => !d.grid_x && !d.grid_y) // 保存degenerate相关业务数据，作为后续计算、渲染或请求的输入。
  const cols = Math.max(1, Math.ceil(Math.sqrt(list.length))) // 保存cols相关业务数据，作为后续计算、渲染或请求的输入。
  const cells = list.map((d, i) => ({ // 保存cells相关业务数据，作为后续计算、渲染或请求的输入。
    d, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    gx: degenerate ? i % cols : (d.grid_x ?? 0), // 声明gx字段，作为组件配置、请求参数或图表数据的一部分。
    gy: degenerate ? Math.floor(i / cols) : (d.grid_y ?? 0), // 声明gy字段，作为组件配置、请求参数或图表数据的一部分。
  })) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const maxX = Math.max(...cells.map((c) => c.gx)) // 保存maxX相关业务数据，作为后续计算、渲染或请求的输入。
  const maxY = Math.max(...cells.map((c) => c.gy)) // 保存maxY相关业务数据，作为后续计算、渲染或请求的输入。
  const offsetX = (maxX * SPACING) / 2 // 保存offsetX相关业务数据，作为后续计算、渲染或请求的输入。
  const offsetZ = (maxY * SPACING) / 2 // 保存offsetZ相关业务数据，作为后续计算、渲染或请求的输入。

  const prices = list.map((d) => d.avg_unit_price || 0) // 保存prices相关业务数据，作为后续计算、渲染或请求的输入。
  const min = Math.min(...prices) // 保存min相关业务数据，作为后续计算、渲染或请求的输入。
  const max = Math.max(...prices) // 保存max相关业务数据，作为后续计算、渲染或请求的输入。
  const range = max - min || 1 // 保存range相关业务数据，作为后续计算、渲染或请求的输入。
  priceRange.value = { min, max } // 更新priceRange.value对应的页面状态，使界面展示与最新业务数据一致。

  const groundSize = Math.max(maxX, maxY) * SPACING + SPACING * 2.5 // 保存groundSize相关业务数据，作为后续计算、渲染或请求的输入。
  const ground = new THREE.Mesh( // 保存ground相关业务数据，作为后续计算、渲染或请求的输入。
    new THREE.PlaneGeometry(groundSize, groundSize), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    new THREE.MeshStandardMaterial({ color: 0x111a2e, roughness: 0.95 }), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ) // 完成当前参数、配置或响应式数据结构的组装。
  ground.rotation.x = -Math.PI / 2 // 更新ground.rotation.x对应的页面状态，使界面展示与最新业务数据一致。
  ground.position.y = -0.02 // 更新ground.position.y对应的页面状态，使界面展示与最新业务数据一致。
  cityGroup.add(ground) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  cityGroup.add(new THREE.GridHelper(groundSize, Math.max(maxX, maxY) + 4, 0x1e3a8a, 0x1e293b)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  for (const { d, gx, gy } of cells) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    const t = ((d.avg_unit_price || 0) - min) / range // 保存t相关业务数据，作为后续计算、渲染或请求的输入。
    const height = 3 + t * 22 // 保存height相关业务数据，作为后续计算、渲染或请求的输入。
    const mesh = new THREE.Mesh( // 保存mesh相关业务数据，作为后续计算、渲染或请求的输入。
      new THREE.BoxGeometry(BOX, height, BOX), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      new THREE.MeshStandardMaterial({ color: colorForT(t), roughness: 0.4, metalness: 0.1 }), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    ) // 完成当前参数、配置或响应式数据结构的组装。
    const x = gx * SPACING - offsetX // 保存x相关业务数据，作为后续计算、渲染或请求的输入。
    const z = gy * SPACING - offsetZ // 保存z相关业务数据，作为后续计算、渲染或请求的输入。
    mesh.position.set(x, height / 2, z) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    mesh.userData = { district: d } // 更新mesh.userData对应的页面状态，使界面展示与最新业务数据一致。
    cityGroup.add(mesh) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    columns.push(mesh) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

    const label = makeLabel(d.name) // 保存label相关业务数据，作为后续计算、渲染或请求的输入。
    label.position.set(x, height + 2.4, z) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    cityGroup.add(label) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  scene.add(cityGroup) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  controls?.target.set(0, 6, 0) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  controls?.update() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(mesh) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  hovered = mesh // 更新hovered对应的页面状态，使界面展示与最新业务数据一致。
  mesh.material.emissive = new THREE.Color(0x3b82f6) // 更新mesh.material.emissive对应的页面状态，使界面展示与最新业务数据一致。
  mesh.material.emissiveIntensity = 0.6 // 更新mesh.material.emissiveIntensity对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (hovered) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    hovered.material.emissive = new THREE.Color(0x000000) // 更新hovered.material.emissive对应的页面状态，使界面展示与最新业务数据一致。
    hovered = null // 更新hovered对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(event) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const rect = renderer.domElement.getBoundingClientRect() // 保存rect相关业务数据，作为后续计算、渲染或请求的输入。
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1 // 更新pointer.x对应的页面状态，使界面展示与最新业务数据一致。
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1 // 更新pointer.y对应的页面状态，使界面展示与最新业务数据一致。
  raycaster.setFromCamera(pointer, camera) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const hits = raycaster.intersectObjects(columns, false) // 保存hits相关业务数据，作为后续计算、渲染或请求的输入。
  if (hits.length) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    const mesh = hits[0].object // 保存mesh相关业务数据，作为后续计算、渲染或请求的输入。
    if (hovered !== mesh) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      clearHover() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      setHover(mesh) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
    const d = mesh.userData.district // 保存d相关业务数据，作为后续计算、渲染或请求的输入。
    tooltip.value = { // 更新tooltip.value对应的页面状态，使界面展示与最新业务数据一致。
      show: true, // 声明show字段，作为组件配置、请求参数或图表数据的一部分。
      x: event.clientX - rect.left, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
      y: event.clientY - rect.top, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
      name: d.name, // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      price: d.avg_unit_price, // 声明price字段，作为组件配置、请求参数或图表数据的一部分。
      count: d.property_count, // 声明count字段，作为组件配置、请求参数或图表数据的一部分。
    } // 完成当前参数、配置或响应式数据结构的组装。
    renderer.domElement.style.cursor = 'pointer' // 更新renderer.domElement.style.cursor对应的页面状态，使界面展示与最新业务数据一致。
  } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    clearHover() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    tooltip.value.show = false // 更新tooltip.value.show对应的页面状态，使界面展示与最新业务数据一致。
    renderer.domElement.style.cursor = 'grab' // 更新renderer.domElement.style.cursor对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (hovered) emit('select', hovered.userData.district) // 根据当前状态、接口结果或用户输入选择对应交互路径。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const el = container.value // 保存el相关业务数据，作为后续计算、渲染或请求的输入。
  if (!el || !renderer) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const w = el.clientWidth // 保存w相关业务数据，作为后续计算、渲染或请求的输入。
  const h = el.clientHeight // 保存h相关业务数据，作为后续计算、渲染或请求的输入。
  camera.aspect = w / h // 更新camera.aspect对应的页面状态，使界面展示与最新业务数据一致。
  camera.updateProjectionMatrix() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.setSize(w, h) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  frameId = requestAnimationFrame(animate) // 更新frameId对应的页面状态，使界面展示与最新业务数据一致。
  controls.update() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.render(scene, camera) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const el = container.value // 保存el相关业务数据，作为后续计算、渲染或请求的输入。
  const w = el.clientWidth // 保存w相关业务数据，作为后续计算、渲染或请求的输入。
  const h = el.clientHeight || 480 // 保存h相关业务数据，作为后续计算、渲染或请求的输入。

  scene = new THREE.Scene() // 更新scene对应的页面状态，使界面展示与最新业务数据一致。
  scene.background = new THREE.Color(0x0b1120) // 更新scene.background对应的页面状态，使界面展示与最新业务数据一致。
  scene.fog = new THREE.Fog(0x0b1120, 70, 180) // 更新scene.fog对应的页面状态，使界面展示与最新业务数据一致。

  camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 1000) // 更新camera对应的页面状态，使界面展示与最新业务数据一致。
  camera.position.set(38, 40, 52) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  renderer = new THREE.WebGLRenderer({ antialias: true }) // 更新renderer对应的页面状态，使界面展示与最新业务数据一致。
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.setSize(w, h) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.domElement.style.cursor = 'grab' // 更新renderer.domElement.style.cursor对应的页面状态，使界面展示与最新业务数据一致。
  el.appendChild(renderer.domElement) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  controls = new OrbitControls(camera, renderer.domElement) // 更新controls对应的页面状态，使界面展示与最新业务数据一致。
  controls.enableDamping = true // 更新controls.enableDamping对应的页面状态，使界面展示与最新业务数据一致。
  controls.dampingFactor = 0.08 // 更新controls.dampingFactor对应的页面状态，使界面展示与最新业务数据一致。
  controls.minDistance = 22 // 更新controls.minDistance对应的页面状态，使界面展示与最新业务数据一致。
  controls.maxDistance = 150 // 更新controls.maxDistance对应的页面状态，使界面展示与最新业务数据一致。
  controls.maxPolarAngle = Math.PI / 2.15 // 更新controls.maxPolarAngle对应的页面状态，使界面展示与最新业务数据一致。
  controls.autoRotate = true // 更新controls.autoRotate对应的页面状态，使界面展示与最新业务数据一致。
  controls.autoRotateSpeed = 0.6 // 更新controls.autoRotateSpeed对应的页面状态，使界面展示与最新业务数据一致。
  controls.addEventListener('start', () => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    controls.autoRotate = false // 更新controls.autoRotate对应的页面状态，使界面展示与最新业务数据一致。
  }) // 完成当前参数、配置或响应式数据结构的组装。

  scene.add(new THREE.AmbientLight(0xffffff, 0.65)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const key = new THREE.DirectionalLight(0xffffff, 1.1) // 保存key相关业务数据，作为后续计算、渲染或请求的输入。
  key.position.set(30, 60, 30) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  scene.add(key) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const fill = new THREE.DirectionalLight(0x88aaff, 0.4) // 保存fill相关业务数据，作为后续计算、渲染或请求的输入。
  fill.position.set(-40, 20, -30) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  scene.add(fill) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  raycaster = new THREE.Raycaster() // 更新raycaster对应的页面状态，使界面展示与最新业务数据一致。
  pointer = new THREE.Vector2() // 更新pointer对应的页面状态，使界面展示与最新业务数据一致。

  buildColumns() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  renderer.domElement.addEventListener('pointermove', onPointerMove) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.domElement.addEventListener('click', onClick) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer.domElement.addEventListener('pointerleave', () => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    tooltip.value.show = false // 更新tooltip.value.show对应的页面状态，使界面展示与最新业务数据一致。
    clearHover() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }) // 完成当前参数、配置或响应式数据结构的组装。

  resizeObserver = new ResizeObserver(onResize) // 更新resizeObserver对应的页面状态，使界面展示与最新业务数据一致。
  resizeObserver.observe(el) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

  animate() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(initThree) // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => props.districts, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  () => buildColumns(), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

onBeforeUnmount(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  if (frameId) cancelAnimationFrame(frameId) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  resizeObserver?.disconnect() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  if (renderer) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    renderer.domElement.removeEventListener('pointermove', onPointerMove) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    renderer.domElement.removeEventListener('click', onClick) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  disposeGroup() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  renderer?.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    container.value.removeChild(renderer.domElement) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  scene = camera = renderer = controls = raycaster = pointer = null // 更新scene对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(n) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return Number(n || 0).toLocaleString() // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <div class="map3d" :style="{ height }">
    <div ref="container" class="canvas-host"></div>

    <div v-if="!districts.length" class="empty">
      <el-icon :size="32"><Loading /></el-icon>
      <span>正在加载 3D 房价地图…</span>
    </div>

    <!-- Hover tooltip -->
    <div
      v-show="tooltip.show"
      class="tooltip"
      :style="{ left: tooltip.x + 14 + 'px', top: tooltip.y + 14 + 'px' }"
    >
      <div class="t-name">{{ tooltip.name }}</div>
      <div class="t-row">
        均价 <b class="t-price">{{ fmt(tooltip.price) }}</b> 元/㎡
      </div>
      <div class="t-row muted-light">在售房源 {{ tooltip.count }} 套 · 点击查看</div>
    </div>

    <!-- Hint -->
    <div class="hint">🖱 拖拽旋转 · 滚轮缩放 · 点击区块查看房源</div>

    <!-- Color legend -->
    <div v-if="districts.length" class="legend">
      <span class="muted-light">{{ fmt(priceRange.min) }}</span>
      <div class="legend-bar"></div>
      <span class="muted-light">{{ fmt(priceRange.max) }} 元/㎡</span>
    </div>
  </div>
</template>

<style scoped>
.map3d { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: relative; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border-radius: var(--card-radius); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  overflow: hidden; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: #0b1120; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  box-shadow: var(--shadow); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.canvas-host { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.empty { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  inset: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  color: #94a3b8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.tooltip { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  pointer-events: none; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(15, 23, 42, 0.92); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border: 1px solid rgba(96, 165, 250, 0.5); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #e2e8f0; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 10px 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-radius: 8px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  min-width: 150px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  z-index: 5; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.t-name { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin-bottom: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.t-row { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  line-height: 1.6; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.t-price { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #fbbf24; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.muted-light { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #94a3b8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hint { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  top: 12px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  left: 14px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: rgba(226, 232, 240, 0.7); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.legend { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  bottom: 14px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  left: 14px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.legend-bar { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 140px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-radius: 5px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: linear-gradient( /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
    to right, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
    hsl(160, 72%, 52%), /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
    hsl(80, 72%, 52%), /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
    hsl(40, 72%, 52%), /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
    hsl(0, 72%, 52%) /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  ); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
