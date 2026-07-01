<!-- 文件功能：渲染城市区域房价 3D 柱状地图，并处理悬停、点击和自适应。 -->
<script setup>
import * as THREE from 'three' // 导入 * as THREE，供当前前端模块渲染或交互逻辑使用。
import { OrbitControls } from 'three/addons/controls/OrbitControls.js' // 导入 { OrbitControls }，供当前前端模块渲染或交互逻辑使用。
import { onBeforeUnmount, onMounted, ref, watch } from 'vue' // 导入 { onBeforeUnmount, onMounted, ref, watch }，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  districts: { type: Array, default: () => [] }, // 设置 districts: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  height: { type: String, default: '480px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。
const emit = defineEmits(['select']) // 创建 emit，用于保存页面状态、计算结果或接口参数。

const container = ref(null) // 创建 container，用于保存页面状态、计算结果或接口参数。
const tooltip = ref({ show: false, x: 0, y: 0, name: '', price: 0, count: 0 }) // 创建 tooltip，用于保存页面状态、计算结果或接口参数。
const priceRange = ref({ min: 0, max: 0 }) // 创建 priceRange，用于保存页面状态、计算结果或接口参数。

// --- Three.js objects (intentionally non-reactive plain vars) ---
let scene, camera, renderer, controls, raycaster, pointer // 创建 scene, camera, renderer, controls, raycaster, pointer，用于保存页面状态、计算结果或接口参数。
let cityGroup = null // 创建 cityGroup，用于保存页面状态、计算结果或接口参数。
let columns = [] // 创建 columns，用于保存页面状态、计算结果或接口参数。
let hovered = null // 创建 hovered，用于保存页面状态、计算结果或接口参数。
let frameId = null // 创建 frameId，用于保存页面状态、计算结果或接口参数。
let resizeObserver = null // 创建 resizeObserver，用于保存页面状态、计算结果或接口参数。

const SPACING = 6 // 创建 SPACING，用于保存页面状态、计算结果或接口参数。
const BOX = 3.4 // 创建 BOX，用于保存页面状态、计算结果或接口参数。

// Low price → teal, high price → red (matches the legend gradient below).
// 函数功能：按归一化价格生成 3D 柱体颜色。
function colorForT(t) { // 定义 colorForT 函数，处理页面交互、数据加载或状态同步。
  const hue = THREE.MathUtils.lerp(160, 0, t) / 360 // 创建 hue，用于保存页面状态、计算结果或接口参数。
  return new THREE.Color().setHSL(hue, 0.72, 0.52) // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text) { // 定义 makeLabel 函数，处理页面交互、数据加载或状态同步。
  const canvas = document.createElement('canvas') // 创建 canvas，用于保存页面状态、计算结果或接口参数。
  canvas.width = 256 // 设置 canvas.width 的值，作为后续渲染、计算或请求的输入。
  canvas.height = 64 // 设置 canvas.height 的值，作为后续渲染、计算或请求的输入。
  const ctx = canvas.getContext('2d') // 创建 ctx，用于保存页面状态、计算结果或接口参数。
  ctx.font = 'bold 40px "PingFang SC", "Microsoft YaHei", sans-serif' // 设置 ctx.font 的值，作为后续渲染、计算或请求的输入。
  ctx.fillStyle = 'rgba(255,255,255,0.96)' // 设置 ctx.fillStyle 的值，作为后续渲染、计算或请求的输入。
  ctx.textAlign = 'center' // 设置 ctx.textAlign 的值，作为后续渲染、计算或请求的输入。
  ctx.textBaseline = 'middle' // 设置 ctx.textBaseline 的值，作为后续渲染、计算或请求的输入。
  ctx.fillText(text, canvas.width / 2, canvas.height / 2) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const texture = new THREE.CanvasTexture(canvas) // 创建 texture，用于保存页面状态、计算结果或接口参数。
  texture.minFilter = THREE.LinearFilter // 设置 texture.minFilter 的值，作为后续渲染、计算或请求的输入。
  const sprite = new THREE.Sprite( // 创建 sprite，用于保存页面状态、计算结果或接口参数。
    new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ) // 结束当前函数、对象、数组或组件配置块。
  sprite.scale.set(6, 1.5, 1) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  return sprite // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：释放当前 3D 城市柱状图分组及其几何和材质资源。
function disposeGroup() { // 定义 disposeGroup 函数，处理页面交互、数据加载或状态同步。
  if (!cityGroup || !scene) return // 根据当前页面状态或接口结果决定是否进入该分支。
  scene.remove(cityGroup) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  cityGroup.traverse((obj) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    obj.geometry?.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    if (obj.material) { // 根据当前页面状态或接口结果决定是否进入该分支。
      obj.material.map?.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      obj.material.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
  }) // 结束当前函数、对象、数组或组件配置块。
  cityGroup = null // 设置 cityGroup 的值，作为后续渲染、计算或请求的输入。
  columns = [] // 设置 columns 的值，作为后续渲染、计算或请求的输入。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据区域数据重建 3D 房价柱状图。
function buildColumns() { // 定义 buildColumns 函数，处理页面交互、数据加载或状态同步。
  if (!scene) return // 根据当前页面状态或接口结果决定是否进入该分支。
  disposeGroup() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const list = props.districts || [] // 创建 list，用于保存页面状态、计算结果或接口参数。
  if (!list.length) return // 根据当前页面状态或接口结果决定是否进入该分支。

  cityGroup = new THREE.Group() // 设置 cityGroup 的值，作为后续渲染、计算或请求的输入。

  // 真实数据的“区”多为商圈，且无预设网格坐标（grid 全为 0）；此时按序号自动排成近似方阵。
  // 若数据自带有效网格（旧种子数据），则沿用其布局。
  const degenerate = list.every((d) => !d.grid_x && !d.grid_y) // 创建 degenerate，用于保存页面状态、计算结果或接口参数。
  const cols = Math.max(1, Math.ceil(Math.sqrt(list.length))) // 创建 cols，用于保存页面状态、计算结果或接口参数。
  const cells = list.map((d, i) => ({ // 创建 cells，用于保存页面状态、计算结果或接口参数。
    d, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    gx: degenerate ? i % cols : (d.grid_x ?? 0), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    gy: degenerate ? Math.floor(i / cols) : (d.grid_y ?? 0), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  })) // 结束当前函数、对象、数组或组件配置块。
  const maxX = Math.max(...cells.map((c) => c.gx)) // 创建 maxX，用于保存页面状态、计算结果或接口参数。
  const maxY = Math.max(...cells.map((c) => c.gy)) // 创建 maxY，用于保存页面状态、计算结果或接口参数。
  const offsetX = (maxX * SPACING) / 2 // 创建 offsetX，用于保存页面状态、计算结果或接口参数。
  const offsetZ = (maxY * SPACING) / 2 // 创建 offsetZ，用于保存页面状态、计算结果或接口参数。

  const prices = list.map((d) => d.avg_unit_price || 0) // 创建 prices，用于保存页面状态、计算结果或接口参数。
  const min = Math.min(...prices) // 创建 min，用于保存页面状态、计算结果或接口参数。
  const max = Math.max(...prices) // 创建 max，用于保存页面状态、计算结果或接口参数。
  const range = max - min || 1 // 创建 range，用于保存页面状态、计算结果或接口参数。
  priceRange.value = { min, max } // 更新 priceRange.value 响应式状态，让页面展示与最新数据保持一致。

  const groundSize = Math.max(maxX, maxY) * SPACING + SPACING * 2.5 // 创建 groundSize，用于保存页面状态、计算结果或接口参数。
  const ground = new THREE.Mesh( // 创建 ground，用于保存页面状态、计算结果或接口参数。
    new THREE.PlaneGeometry(groundSize, groundSize), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    new THREE.MeshStandardMaterial({ color: 0x111a2e, roughness: 0.95 }), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ) // 结束当前函数、对象、数组或组件配置块。
  ground.rotation.x = -Math.PI / 2 // 设置 ground.rotation.x 的值，作为后续渲染、计算或请求的输入。
  ground.position.y = -0.02 // 设置 ground.position.y 的值，作为后续渲染、计算或请求的输入。
  cityGroup.add(ground) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  cityGroup.add(new THREE.GridHelper(groundSize, Math.max(maxX, maxY) + 4, 0x1e3a8a, 0x1e293b)) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  for (const { d, gx, gy } of cells) { // 遍历当前数据集合，逐项生成页面需要的数据。
    const t = ((d.avg_unit_price || 0) - min) / range // 创建 t，用于保存页面状态、计算结果或接口参数。
    const height = 3 + t * 22 // 创建 height，用于保存页面状态、计算结果或接口参数。
    const mesh = new THREE.Mesh( // 创建 mesh，用于保存页面状态、计算结果或接口参数。
      new THREE.BoxGeometry(BOX, height, BOX), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      new THREE.MeshStandardMaterial({ color: colorForT(t), roughness: 0.4, metalness: 0.1 }), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ) // 结束当前函数、对象、数组或组件配置块。
    const x = gx * SPACING - offsetX // 创建 x，用于保存页面状态、计算结果或接口参数。
    const z = gy * SPACING - offsetZ // 创建 z，用于保存页面状态、计算结果或接口参数。
    mesh.position.set(x, height / 2, z) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    mesh.userData = { district: d } // 设置 mesh.userData 的值，作为后续渲染、计算或请求的输入。
    cityGroup.add(mesh) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    columns.push(mesh) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

    const label = makeLabel(d.name) // 创建 label，用于保存页面状态、计算结果或接口参数。
    label.position.set(x, height + 2.4, z) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    cityGroup.add(label) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  scene.add(cityGroup) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  controls?.target.set(0, 6, 0) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  controls?.update() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(mesh) { // 定义 setHover 函数，处理页面交互、数据加载或状态同步。
  hovered = mesh // 设置 hovered 的值，作为后续渲染、计算或请求的输入。
  mesh.material.emissive = new THREE.Color(0x3b82f6) // 设置 mesh.material.emissive 的值，作为后续渲染、计算或请求的输入。
  mesh.material.emissiveIntensity = 0.6 // 设置 mesh.material.emissiveIntensity 的值，作为后续渲染、计算或请求的输入。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() { // 定义 clearHover 函数，处理页面交互、数据加载或状态同步。
  if (hovered) { // 根据当前页面状态或接口结果决定是否进入该分支。
    hovered.material.emissive = new THREE.Color(0x000000) // 设置 hovered.material.emissive 的值，作为后续渲染、计算或请求的输入。
    hovered = null // 设置 hovered 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(event) { // 定义 onPointerMove 函数，处理页面交互、数据加载或状态同步。
  const rect = renderer.domElement.getBoundingClientRect() // 创建 rect，用于保存页面状态、计算结果或接口参数。
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1 // 设置 pointer.x 的值，作为后续渲染、计算或请求的输入。
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1 // 设置 pointer.y 的值，作为后续渲染、计算或请求的输入。
  raycaster.setFromCamera(pointer, camera) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const hits = raycaster.intersectObjects(columns, false) // 创建 hits，用于保存页面状态、计算结果或接口参数。
  if (hits.length) { // 根据当前页面状态或接口结果决定是否进入该分支。
    const mesh = hits[0].object // 创建 mesh，用于保存页面状态、计算结果或接口参数。
    if (hovered !== mesh) { // 根据当前页面状态或接口结果决定是否进入该分支。
      clearHover() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      setHover(mesh) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    const d = mesh.userData.district // 创建 d，用于保存页面状态、计算结果或接口参数。
    tooltip.value = { // 更新 tooltip.value 响应式状态，让页面展示与最新数据保持一致。
      show: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      x: event.clientX - rect.left, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      y: event.clientY - rect.top, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: d.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      price: d.avg_unit_price, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      count: d.property_count, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    renderer.domElement.style.cursor = 'pointer' // 设置 renderer.domElement.style.cursor 的值，作为后续渲染、计算或请求的输入。
  } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    clearHover() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    tooltip.value.show = false // 更新 tooltip.value.show 响应式状态，让页面展示与最新数据保持一致。
    renderer.domElement.style.cursor = 'grab' // 设置 renderer.domElement.style.cursor 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() { // 定义 onClick 函数，处理页面交互、数据加载或状态同步。
  if (hovered) emit('select', hovered.userData.district) // 根据当前页面状态或接口结果决定是否进入该分支。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() { // 定义 onResize 函数，处理页面交互、数据加载或状态同步。
  const el = container.value // 创建 el，用于保存页面状态、计算结果或接口参数。
  if (!el || !renderer) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const w = el.clientWidth // 创建 w，用于保存页面状态、计算结果或接口参数。
  const h = el.clientHeight // 创建 h，用于保存页面状态、计算结果或接口参数。
  camera.aspect = w / h // 设置 camera.aspect 的值，作为后续渲染、计算或请求的输入。
  camera.updateProjectionMatrix() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.setSize(w, h) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() { // 定义 animate 函数，处理页面交互、数据加载或状态同步。
  frameId = requestAnimationFrame(animate) // 设置 frameId 的值，作为后续渲染、计算或请求的输入。
  controls.update() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.render(scene, camera) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() { // 定义 initThree 函数，处理页面交互、数据加载或状态同步。
  const el = container.value // 创建 el，用于保存页面状态、计算结果或接口参数。
  const w = el.clientWidth // 创建 w，用于保存页面状态、计算结果或接口参数。
  const h = el.clientHeight || 480 // 创建 h，用于保存页面状态、计算结果或接口参数。

  scene = new THREE.Scene() // 设置 scene 的值，作为后续渲染、计算或请求的输入。
  scene.background = new THREE.Color(0x0b1120) // 设置 scene.background 的值，作为后续渲染、计算或请求的输入。
  scene.fog = new THREE.Fog(0x0b1120, 70, 180) // 设置 scene.fog 的值，作为后续渲染、计算或请求的输入。

  camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 1000) // 设置 camera 的值，作为后续渲染、计算或请求的输入。
  camera.position.set(38, 40, 52) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  renderer = new THREE.WebGLRenderer({ antialias: true }) // 设置 renderer 的值，作为后续渲染、计算或请求的输入。
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.setSize(w, h) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.domElement.style.cursor = 'grab' // 设置 renderer.domElement.style.cursor 的值，作为后续渲染、计算或请求的输入。
  el.appendChild(renderer.domElement) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  controls = new OrbitControls(camera, renderer.domElement) // 设置 controls 的值，作为后续渲染、计算或请求的输入。
  controls.enableDamping = true // 设置 controls.enableDamping 的值，作为后续渲染、计算或请求的输入。
  controls.dampingFactor = 0.08 // 设置 controls.dampingFactor 的值，作为后续渲染、计算或请求的输入。
  controls.minDistance = 22 // 设置 controls.minDistance 的值，作为后续渲染、计算或请求的输入。
  controls.maxDistance = 150 // 设置 controls.maxDistance 的值，作为后续渲染、计算或请求的输入。
  controls.maxPolarAngle = Math.PI / 2.15 // 设置 controls.maxPolarAngle 的值，作为后续渲染、计算或请求的输入。
  controls.autoRotate = true // 设置 controls.autoRotate 的值，作为后续渲染、计算或请求的输入。
  controls.autoRotateSpeed = 0.6 // 设置 controls.autoRotateSpeed 的值，作为后续渲染、计算或请求的输入。
  controls.addEventListener('start', () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    controls.autoRotate = false // 设置 controls.autoRotate 的值，作为后续渲染、计算或请求的输入。
  }) // 结束当前函数、对象、数组或组件配置块。

  scene.add(new THREE.AmbientLight(0xffffff, 0.65)) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const key = new THREE.DirectionalLight(0xffffff, 1.1) // 创建 key，用于保存页面状态、计算结果或接口参数。
  key.position.set(30, 60, 30) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  scene.add(key) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const fill = new THREE.DirectionalLight(0x88aaff, 0.4) // 创建 fill，用于保存页面状态、计算结果或接口参数。
  fill.position.set(-40, 20, -30) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  scene.add(fill) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  raycaster = new THREE.Raycaster() // 设置 raycaster 的值，作为后续渲染、计算或请求的输入。
  pointer = new THREE.Vector2() // 设置 pointer 的值，作为后续渲染、计算或请求的输入。

  buildColumns() // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  renderer.domElement.addEventListener('pointermove', onPointerMove) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.domElement.addEventListener('click', onClick) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer.domElement.addEventListener('pointerleave', () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    tooltip.value.show = false // 更新 tooltip.value.show 响应式状态，让页面展示与最新数据保持一致。
    clearHover() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。

  resizeObserver = new ResizeObserver(onResize) // 设置 resizeObserver 的值，作为后续渲染、计算或请求的输入。
  resizeObserver.observe(el) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

  animate() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(initThree) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => props.districts, // 设置  的值，作为后续渲染、计算或请求的输入。
  () => buildColumns(), // 设置  的值，作为后续渲染、计算或请求的输入。
) // 结束当前函数、对象、数组或组件配置块。

onBeforeUnmount(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  if (frameId) cancelAnimationFrame(frameId) // 根据当前页面状态或接口结果决定是否进入该分支。
  resizeObserver?.disconnect() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  if (renderer) { // 根据当前页面状态或接口结果决定是否进入该分支。
    renderer.domElement.removeEventListener('pointermove', onPointerMove) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    renderer.domElement.removeEventListener('click', onClick) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  disposeGroup() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  renderer?.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) { // 根据当前页面状态或接口结果决定是否进入该分支。
    container.value.removeChild(renderer.domElement) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  scene = camera = renderer = controls = raycaster = pointer = null // 设置 scene 的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(n) { // 定义 fmt 函数，处理页面交互、数据加载或状态同步。
  return Number(n || 0).toLocaleString() // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
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
.map3d { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  border-radius: var(--card-radius); /* 设置圆角半径。 */
  overflow: hidden; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: #0b1120; /* 设置背景样式。 */
  box-shadow: var(--shadow); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.canvas-host { /* 定义当前选择器的样式作用域。 */
  width: 100%; /* 设置元素宽度。 */
  height: 100%; /* 设置元素高度。 */
} /* 结束当前样式规则块。 */
.empty { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  inset: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  gap: 12px; /* 设置子元素之间的间距。 */
  color: #94a3b8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.tooltip { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  pointer-events: none; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(15, 23, 42, 0.92); /* 设置背景样式。 */
  border: 1px solid rgba(96, 165, 250, 0.5); /* 设置边框样式。 */
  color: #e2e8f0; /* 设置文字颜色。 */
  padding: 10px 14px; /* 设置元素内边距。 */
  border-radius: 8px; /* 设置圆角半径。 */
  font-size: 13px; /* 设置文字大小。 */
  min-width: 150px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  z-index: 5; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.t-name { /* 定义当前选择器的样式作用域。 */
  font-size: 15px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
  margin-bottom: 4px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.t-row { /* 定义当前选择器的样式作用域。 */
  line-height: 1.6; /* 设置文本行高。 */
} /* 结束当前样式规则块。 */
.t-price { /* 定义当前选择器的样式作用域。 */
  color: #fbbf24; /* 设置文字颜色。 */
  font-size: 15px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.muted-light { /* 定义当前选择器的样式作用域。 */
  color: #94a3b8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.hint { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  top: 12px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: 14px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: rgba(226, 232, 240, 0.7); /* 设置文字颜色。 */
  font-size: 12px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.legend { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  bottom: 14px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: 14px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 8px; /* 设置子元素之间的间距。 */
  font-size: 12px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.legend-bar { /* 定义当前选择器的样式作用域。 */
  width: 140px; /* 设置元素宽度。 */
  height: 10px; /* 设置元素高度。 */
  border-radius: 5px; /* 设置圆角半径。 */
  background: linear-gradient( /* 设置背景样式。 */
    to right, /* 设置当前样式属性，控制页面布局或视觉展示。 */
    hsl(160, 72%, 52%), /* 设置当前样式属性，控制页面布局或视觉展示。 */
    hsl(80, 72%, 52%), /* 设置当前样式属性，控制页面布局或视觉展示。 */
    hsl(40, 72%, 52%), /* 设置当前样式属性，控制页面布局或视觉展示。 */
    hsl(0, 72%, 52%) /* 设置当前样式属性，控制页面布局或视觉展示。 */
  ); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
</style>
