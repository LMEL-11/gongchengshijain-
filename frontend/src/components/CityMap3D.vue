<!-- 文件功能：渲染城市区域房价 3D 柱状地图，并处理悬停、点击和自适应。 -->
<script setup>
import * as THREE from 'three' // 导入本行所需的依赖。
import { OrbitControls } from 'three/addons/controls/OrbitControls.js' // 导入本行所需的依赖。
import { onBeforeUnmount, onMounted, ref, watch } from 'vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  districts: { type: Array, default: () => [] }, // 配置当前对象字段。
  height: { type: String, default: '480px' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。
const emit = defineEmits(['select']) // 声明并初始化当前变量。

const container = ref(null) // 声明并初始化当前变量。
const tooltip = ref({ show: false, x: 0, y: 0, name: '', price: 0, count: 0 }) // 声明并初始化当前变量。
const priceRange = ref({ min: 0, max: 0 }) // 声明并初始化当前变量。

// --- Three.js objects (intentionally non-reactive plain vars) ---
let scene, camera, renderer, controls, raycaster, pointer // 声明并初始化当前变量。
let cityGroup = null // 声明并初始化当前变量。
let columns = [] // 声明并初始化当前变量。
let hovered = null // 声明并初始化当前变量。
let frameId = null // 声明并初始化当前变量。
let resizeObserver = null // 声明并初始化当前变量。

const SPACING = 6 // 声明并初始化当前变量。
const BOX = 3.4 // 声明并初始化当前变量。

// Low price → teal, high price → red (matches the legend gradient below).
// 函数功能：按归一化价格生成 3D 柱体颜色。
function colorForT(t) { // 声明当前函数入口。
  const hue = THREE.MathUtils.lerp(160, 0, t) / 360 // 声明并初始化当前变量。
  return new THREE.Color().setHSL(hue, 0.72, 0.52) // 返回当前表达式结果。
} // 结束当前代码块或数据结构。

// 函数功能：创建地图或柱体上方的文字标签精灵。
function makeLabel(text) { // 声明当前函数入口。
  const canvas = document.createElement('canvas') // 声明并初始化当前变量。
  canvas.width = 256 // 赋值或更新当前变量/状态。
  canvas.height = 64 // 赋值或更新当前变量/状态。
  const ctx = canvas.getContext('2d') // 声明并初始化当前变量。
  ctx.font = 'bold 40px "PingFang SC", "Microsoft YaHei", sans-serif' // 赋值或更新当前变量/状态。
  ctx.fillStyle = 'rgba(255,255,255,0.96)' // 赋值或更新当前变量/状态。
  ctx.textAlign = 'center' // 赋值或更新当前变量/状态。
  ctx.textBaseline = 'middle' // 赋值或更新当前变量/状态。
  ctx.fillText(text, canvas.width / 2, canvas.height / 2) // 执行本行前端逻辑。
  const texture = new THREE.CanvasTexture(canvas) // 声明并初始化当前变量。
  texture.minFilter = THREE.LinearFilter // 赋值或更新当前变量/状态。
  const sprite = new THREE.Sprite( // 声明并初始化当前变量。
    new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }), // 配置当前对象字段。
  ) // 结束当前代码块或数据结构。
  sprite.scale.set(6, 1.5, 1) // 执行本行前端逻辑。
  return sprite // 返回当前表达式结果。
} // 结束当前代码块或数据结构。

// 函数功能：释放当前 3D 城市柱状图分组及其几何和材质资源。
function disposeGroup() { // 声明当前函数入口。
  if (!cityGroup || !scene) return // 根据条件判断是否执行分支。
  scene.remove(cityGroup) // 执行本行前端逻辑。
  cityGroup.traverse((obj) => { // 执行本行前端逻辑。
    obj.geometry?.dispose() // 执行本行前端逻辑。
    if (obj.material) { // 根据条件判断是否执行分支。
      obj.material.map?.dispose() // 执行本行前端逻辑。
      obj.material.dispose() // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
  }) // 执行本行前端逻辑。
  cityGroup = null // 赋值或更新当前变量/状态。
  columns = [] // 赋值或更新当前变量/状态。
} // 结束当前代码块或数据结构。

// 函数功能：根据区域数据重建 3D 房价柱状图。
function buildColumns() { // 声明当前函数入口。
  if (!scene) return // 根据条件判断是否执行分支。
  disposeGroup() // 执行本行前端逻辑。
  const list = props.districts || [] // 声明并初始化当前变量。
  if (!list.length) return // 根据条件判断是否执行分支。

  cityGroup = new THREE.Group() // 赋值或更新当前变量/状态。

  // 真实数据的“区”多为商圈，且无预设网格坐标（grid 全为 0）；此时按序号自动排成近似方阵。
  // 若数据自带有效网格（旧种子数据），则沿用其布局。
  const degenerate = list.every((d) => !d.grid_x && !d.grid_y) // 声明并初始化当前变量。
  const cols = Math.max(1, Math.ceil(Math.sqrt(list.length))) // 声明并初始化当前变量。
  const cells = list.map((d, i) => ({ // 声明并初始化当前变量。
    d, // 继续声明当前列表项或参数项。
    gx: degenerate ? i % cols : (d.grid_x ?? 0), // 配置当前对象字段。
    gy: degenerate ? Math.floor(i / cols) : (d.grid_y ?? 0), // 配置当前对象字段。
  })) // 执行本行前端逻辑。
  const maxX = Math.max(...cells.map((c) => c.gx)) // 声明并初始化当前变量。
  const maxY = Math.max(...cells.map((c) => c.gy)) // 声明并初始化当前变量。
  const offsetX = (maxX * SPACING) / 2 // 声明并初始化当前变量。
  const offsetZ = (maxY * SPACING) / 2 // 声明并初始化当前变量。

  const prices = list.map((d) => d.avg_unit_price || 0) // 声明并初始化当前变量。
  const min = Math.min(...prices) // 声明并初始化当前变量。
  const max = Math.max(...prices) // 声明并初始化当前变量。
  const range = max - min || 1 // 声明并初始化当前变量。
  priceRange.value = { min, max } // 赋值或更新当前变量/状态。

  const groundSize = Math.max(maxX, maxY) * SPACING + SPACING * 2.5 // 声明并初始化当前变量。
  const ground = new THREE.Mesh( // 声明并初始化当前变量。
    new THREE.PlaneGeometry(groundSize, groundSize), // 继续声明当前列表项或参数项。
    new THREE.MeshStandardMaterial({ color: 0x111a2e, roughness: 0.95 }), // 配置当前对象字段。
  ) // 结束当前代码块或数据结构。
  ground.rotation.x = -Math.PI / 2 // 赋值或更新当前变量/状态。
  ground.position.y = -0.02 // 赋值或更新当前变量/状态。
  cityGroup.add(ground) // 执行本行前端逻辑。
  cityGroup.add(new THREE.GridHelper(groundSize, Math.max(maxX, maxY) + 4, 0x1e3a8a, 0x1e293b)) // 执行本行前端逻辑。

  for (const { d, gx, gy } of cells) { // 遍历集合或范围并逐项处理。
    const t = ((d.avg_unit_price || 0) - min) / range // 声明并初始化当前变量。
    const height = 3 + t * 22 // 声明并初始化当前变量。
    const mesh = new THREE.Mesh( // 声明并初始化当前变量。
      new THREE.BoxGeometry(BOX, height, BOX), // 继续声明当前列表项或参数项。
      new THREE.MeshStandardMaterial({ color: colorForT(t), roughness: 0.4, metalness: 0.1 }), // 配置当前对象字段。
    ) // 结束当前代码块或数据结构。
    const x = gx * SPACING - offsetX // 声明并初始化当前变量。
    const z = gy * SPACING - offsetZ // 声明并初始化当前变量。
    mesh.position.set(x, height / 2, z) // 执行本行前端逻辑。
    mesh.userData = { district: d } // 赋值或更新当前变量/状态。
    cityGroup.add(mesh) // 执行本行前端逻辑。
    columns.push(mesh) // 执行本行前端逻辑。

    const label = makeLabel(d.name) // 声明并初始化当前变量。
    label.position.set(x, height + 2.4, z) // 执行本行前端逻辑。
    cityGroup.add(label) // 执行本行前端逻辑。
  } // 结束当前代码块或数据结构。

  scene.add(cityGroup) // 执行本行前端逻辑。
  controls?.target.set(0, 6, 0) // 执行本行前端逻辑。
  controls?.update() // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：设置当前悬停柱体的高亮状态。
function setHover(mesh) { // 声明当前函数入口。
  hovered = mesh // 赋值或更新当前变量/状态。
  mesh.material.emissive = new THREE.Color(0x3b82f6) // 赋值或更新当前变量/状态。
  mesh.material.emissiveIntensity = 0.6 // 赋值或更新当前变量/状态。
} // 结束当前代码块或数据结构。

// 函数功能：清除当前悬停对象的高亮状态。
function clearHover() { // 声明当前函数入口。
  if (hovered) { // 根据条件判断是否执行分支。
    hovered.material.emissive = new THREE.Color(0x000000) // 赋值或更新当前变量/状态。
    hovered = null // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// 函数功能：处理鼠标移动，更新射线命中、悬停提示和光标状态。
function onPointerMove(event) { // 声明当前函数入口。
  const rect = renderer.domElement.getBoundingClientRect() // 声明并初始化当前变量。
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1 // 赋值或更新当前变量/状态。
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1 // 赋值或更新当前变量/状态。
  raycaster.setFromCamera(pointer, camera) // 执行本行前端逻辑。
  const hits = raycaster.intersectObjects(columns, false) // 声明并初始化当前变量。
  if (hits.length) { // 根据条件判断是否执行分支。
    const mesh = hits[0].object // 声明并初始化当前变量。
    if (hovered !== mesh) { // 根据条件判断是否执行分支。
      clearHover() // 执行本行前端逻辑。
      setHover(mesh) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
    const d = mesh.userData.district // 声明并初始化当前变量。
    tooltip.value = { // 赋值或更新当前变量/状态。
      show: true, // 配置当前对象字段。
      x: event.clientX - rect.left, // 配置当前对象字段。
      y: event.clientY - rect.top, // 配置当前对象字段。
      name: d.name, // 配置当前对象字段。
      price: d.avg_unit_price, // 配置当前对象字段。
      count: d.property_count, // 配置当前对象字段。
    } // 结束当前代码块或数据结构。
    renderer.domElement.style.cursor = 'pointer' // 赋值或更新当前变量/状态。
  } else { // 执行本行前端逻辑。
    clearHover() // 执行本行前端逻辑。
    tooltip.value.show = false // 赋值或更新当前变量/状态。
    renderer.domElement.style.cursor = 'grab' // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// 函数功能：处理地图元素点击并向父组件派发选择事件。
function onClick() { // 声明当前函数入口。
  if (hovered) emit('select', hovered.userData.district) // 根据条件判断是否执行分支。
} // 结束当前代码块或数据结构。

// 函数功能：根据容器大小调整相机和渲染器尺寸。
function onResize() { // 声明当前函数入口。
  const el = container.value // 声明并初始化当前变量。
  if (!el || !renderer) return // 根据条件判断是否执行分支。
  const w = el.clientWidth // 声明并初始化当前变量。
  const h = el.clientHeight // 声明并初始化当前变量。
  camera.aspect = w / h // 赋值或更新当前变量/状态。
  camera.updateProjectionMatrix() // 执行本行前端逻辑。
  renderer.setSize(w, h) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：驱动 Three.js 控制器更新和场景循环渲染。
function animate() { // 声明当前函数入口。
  frameId = requestAnimationFrame(animate) // 赋值或更新当前变量/状态。
  controls.update() // 执行本行前端逻辑。
  renderer.render(scene, camera) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：初始化 Three.js 场景、相机、渲染器、灯光和交互控制。
function initThree() { // 声明当前函数入口。
  const el = container.value // 声明并初始化当前变量。
  const w = el.clientWidth // 声明并初始化当前变量。
  const h = el.clientHeight || 480 // 声明并初始化当前变量。

  scene = new THREE.Scene() // 赋值或更新当前变量/状态。
  scene.background = new THREE.Color(0x0b1120) // 赋值或更新当前变量/状态。
  scene.fog = new THREE.Fog(0x0b1120, 70, 180) // 赋值或更新当前变量/状态。

  camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 1000) // 赋值或更新当前变量/状态。
  camera.position.set(38, 40, 52) // 执行本行前端逻辑。

  renderer = new THREE.WebGLRenderer({ antialias: true }) // 赋值或更新当前变量/状态。
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // 执行本行前端逻辑。
  renderer.setSize(w, h) // 执行本行前端逻辑。
  renderer.domElement.style.cursor = 'grab' // 赋值或更新当前变量/状态。
  el.appendChild(renderer.domElement) // 执行本行前端逻辑。

  controls = new OrbitControls(camera, renderer.domElement) // 赋值或更新当前变量/状态。
  controls.enableDamping = true // 赋值或更新当前变量/状态。
  controls.dampingFactor = 0.08 // 赋值或更新当前变量/状态。
  controls.minDistance = 22 // 赋值或更新当前变量/状态。
  controls.maxDistance = 150 // 赋值或更新当前变量/状态。
  controls.maxPolarAngle = Math.PI / 2.15 // 赋值或更新当前变量/状态。
  controls.autoRotate = true // 赋值或更新当前变量/状态。
  controls.autoRotateSpeed = 0.6 // 赋值或更新当前变量/状态。
  controls.addEventListener('start', () => { // 执行本行前端逻辑。
    controls.autoRotate = false // 赋值或更新当前变量/状态。
  }) // 执行本行前端逻辑。

  scene.add(new THREE.AmbientLight(0xffffff, 0.65)) // 执行本行前端逻辑。
  const key = new THREE.DirectionalLight(0xffffff, 1.1) // 声明并初始化当前变量。
  key.position.set(30, 60, 30) // 执行本行前端逻辑。
  scene.add(key) // 执行本行前端逻辑。
  const fill = new THREE.DirectionalLight(0x88aaff, 0.4) // 声明并初始化当前变量。
  fill.position.set(-40, 20, -30) // 执行本行前端逻辑。
  scene.add(fill) // 执行本行前端逻辑。

  raycaster = new THREE.Raycaster() // 赋值或更新当前变量/状态。
  pointer = new THREE.Vector2() // 赋值或更新当前变量/状态。

  buildColumns() // 执行本行前端逻辑。

  renderer.domElement.addEventListener('pointermove', onPointerMove) // 执行本行前端逻辑。
  renderer.domElement.addEventListener('click', onClick) // 执行本行前端逻辑。
  renderer.domElement.addEventListener('pointerleave', () => { // 执行本行前端逻辑。
    tooltip.value.show = false // 赋值或更新当前变量/状态。
    clearHover() // 执行本行前端逻辑。
  }) // 执行本行前端逻辑。

  resizeObserver = new ResizeObserver(onResize) // 赋值或更新当前变量/状态。
  resizeObserver.observe(el) // 执行本行前端逻辑。

  animate() // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

onMounted(initThree) // 注册 Vue 生命周期回调。

watch( // 监听响应式数据变化。
  () => props.districts, // 继续声明当前列表项或参数项。
  () => buildColumns(), // 继续声明当前列表项或参数项。
) // 结束当前代码块或数据结构。

onBeforeUnmount(() => { // 注册 Vue 生命周期回调。
  if (frameId) cancelAnimationFrame(frameId) // 根据条件判断是否执行分支。
  resizeObserver?.disconnect() // 执行本行前端逻辑。
  if (renderer) { // 根据条件判断是否执行分支。
    renderer.domElement.removeEventListener('pointermove', onPointerMove) // 执行本行前端逻辑。
    renderer.domElement.removeEventListener('click', onClick) // 执行本行前端逻辑。
  } // 结束当前代码块或数据结构。
  disposeGroup() // 执行本行前端逻辑。
  renderer?.dispose() // 执行本行前端逻辑。
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) { // 根据条件判断是否执行分支。
    container.value.removeChild(renderer.domElement) // 执行本行前端逻辑。
  } // 结束当前代码块或数据结构。
  scene = camera = renderer = controls = raycaster = pointer = null // 赋值或更新当前变量/状态。
}) // 执行本行前端逻辑。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(n) { // 声明当前函数入口。
  return Number(n || 0).toLocaleString() // 返回当前表达式结果。
} // 结束当前代码块或数据结构。
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
.map3d { /* 开始当前样式规则块。 */
  position: relative; /* 设置当前样式属性。 */
  border-radius: var(--card-radius); /* 设置当前样式属性。 */
  overflow: hidden; /* 设置当前样式属性。 */
  background: #0b1120; /* 设置当前样式属性。 */
  box-shadow: var(--shadow); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.canvas-host { /* 开始当前样式规则块。 */
  width: 100%; /* 设置当前样式属性。 */
  height: 100%; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.empty { /* 开始当前样式规则块。 */
  position: absolute; /* 设置当前样式属性。 */
  inset: 0; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  flex-direction: column; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: center; /* 设置当前样式属性。 */
  gap: 12px; /* 设置当前样式属性。 */
  color: #94a3b8; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.tooltip { /* 开始当前样式规则块。 */
  position: absolute; /* 设置当前样式属性。 */
  pointer-events: none; /* 设置当前样式属性。 */
  background: rgba(15, 23, 42, 0.92); /* 设置当前样式属性。 */
  border: 1px solid rgba(96, 165, 250, 0.5); /* 设置当前样式属性。 */
  color: #e2e8f0; /* 设置当前样式属性。 */
  padding: 10px 14px; /* 设置当前样式属性。 */
  border-radius: 8px; /* 设置当前样式属性。 */
  font-size: 13px; /* 设置当前样式属性。 */
  min-width: 150px; /* 设置当前样式属性。 */
  z-index: 5; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.t-name { /* 开始当前样式规则块。 */
  font-size: 15px; /* 设置当前样式属性。 */
  font-weight: 700; /* 设置当前样式属性。 */
  margin-bottom: 4px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.t-row { /* 开始当前样式规则块。 */
  line-height: 1.6; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.t-price { /* 开始当前样式规则块。 */
  color: #fbbf24; /* 设置当前样式属性。 */
  font-size: 15px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.muted-light { /* 开始当前样式规则块。 */
  color: #94a3b8; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.hint { /* 开始当前样式规则块。 */
  position: absolute; /* 设置当前样式属性。 */
  top: 12px; /* 设置当前样式属性。 */
  left: 14px; /* 设置当前样式属性。 */
  color: rgba(226, 232, 240, 0.7); /* 设置当前样式属性。 */
  font-size: 12px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.legend { /* 开始当前样式规则块。 */
  position: absolute; /* 设置当前样式属性。 */
  bottom: 14px; /* 设置当前样式属性。 */
  left: 14px; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 8px; /* 设置当前样式属性。 */
  font-size: 12px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.legend-bar { /* 开始当前样式规则块。 */
  width: 140px; /* 设置当前样式属性。 */
  height: 10px; /* 设置当前样式属性。 */
  border-radius: 5px; /* 设置当前样式属性。 */
  background: linear-gradient( /* 设置当前样式属性。 */
    to right, /* 声明当前样式规则。 */
    hsl(160, 72%, 52%), /* 声明当前样式规则。 */
    hsl(80, 72%, 52%), /* 声明当前样式规则。 */
    hsl(40, 72%, 52%), /* 声明当前样式规则。 */
    hsl(0, 72%, 52%) /* 声明当前样式规则。 */
  ); /* 声明当前样式规则。 */
} /* 结束当前样式规则块。 */
</style>
