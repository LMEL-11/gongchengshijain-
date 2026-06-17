<script setup>
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  districts: { type: Array, default: () => [] },
  height: { type: String, default: '480px' },
})
const emit = defineEmits(['select'])

const container = ref(null)
const tooltip = ref({ show: false, x: 0, y: 0, name: '', price: 0, count: 0 })
const priceRange = ref({ min: 0, max: 0 })

// --- Three.js objects (intentionally non-reactive plain vars) ---
let scene, camera, renderer, controls, raycaster, pointer
let cityGroup = null
let columns = []
let hovered = null
let frameId = null
let resizeObserver = null

const SPACING = 6
const BOX = 3.4

// Low price → teal, high price → red (matches the legend gradient below).
function colorForT(t) {
  const hue = THREE.MathUtils.lerp(160, 0, t) / 360
  return new THREE.Color().setHSL(hue, 0.72, 0.52)
}

function makeLabel(text) {
  const canvas = document.createElement('canvas')
  canvas.width = 256
  canvas.height = 64
  const ctx = canvas.getContext('2d')
  ctx.font = 'bold 40px "PingFang SC", "Microsoft YaHei", sans-serif'
  ctx.fillStyle = 'rgba(255,255,255,0.96)'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, canvas.width / 2, canvas.height / 2)
  const texture = new THREE.CanvasTexture(canvas)
  texture.minFilter = THREE.LinearFilter
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }),
  )
  sprite.scale.set(6, 1.5, 1)
  return sprite
}

function disposeGroup() {
  if (!cityGroup || !scene) return
  scene.remove(cityGroup)
  cityGroup.traverse((obj) => {
    obj.geometry?.dispose()
    if (obj.material) {
      obj.material.map?.dispose()
      obj.material.dispose()
    }
  })
  cityGroup = null
  columns = []
}

function buildColumns() {
  if (!scene) return
  disposeGroup()
  const list = props.districts || []
  if (!list.length) return

  cityGroup = new THREE.Group()

  // 真实数据的“区”多为商圈，且无预设网格坐标（grid 全为 0）；此时按序号自动排成近似方阵。
  // 若数据自带有效网格（旧种子数据），则沿用其布局。
  const degenerate = list.every((d) => !d.grid_x && !d.grid_y)
  const cols = Math.max(1, Math.ceil(Math.sqrt(list.length)))
  const cells = list.map((d, i) => ({
    d,
    gx: degenerate ? i % cols : (d.grid_x ?? 0),
    gy: degenerate ? Math.floor(i / cols) : (d.grid_y ?? 0),
  }))
  const maxX = Math.max(...cells.map((c) => c.gx))
  const maxY = Math.max(...cells.map((c) => c.gy))
  const offsetX = (maxX * SPACING) / 2
  const offsetZ = (maxY * SPACING) / 2

  const prices = list.map((d) => d.avg_unit_price || 0)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  priceRange.value = { min, max }

  const groundSize = Math.max(maxX, maxY) * SPACING + SPACING * 2.5
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(groundSize, groundSize),
    new THREE.MeshStandardMaterial({ color: 0x111a2e, roughness: 0.95 }),
  )
  ground.rotation.x = -Math.PI / 2
  ground.position.y = -0.02
  cityGroup.add(ground)
  cityGroup.add(new THREE.GridHelper(groundSize, Math.max(maxX, maxY) + 4, 0x1e3a8a, 0x1e293b))

  for (const { d, gx, gy } of cells) {
    const t = ((d.avg_unit_price || 0) - min) / range
    const height = 3 + t * 22
    const mesh = new THREE.Mesh(
      new THREE.BoxGeometry(BOX, height, BOX),
      new THREE.MeshStandardMaterial({ color: colorForT(t), roughness: 0.4, metalness: 0.1 }),
    )
    const x = gx * SPACING - offsetX
    const z = gy * SPACING - offsetZ
    mesh.position.set(x, height / 2, z)
    mesh.userData = { district: d }
    cityGroup.add(mesh)
    columns.push(mesh)

    const label = makeLabel(d.name)
    label.position.set(x, height + 2.4, z)
    cityGroup.add(label)
  }

  scene.add(cityGroup)
  controls?.target.set(0, 6, 0)
  controls?.update()
}

function setHover(mesh) {
  hovered = mesh
  mesh.material.emissive = new THREE.Color(0x3b82f6)
  mesh.material.emissiveIntensity = 0.6
}

function clearHover() {
  if (hovered) {
    hovered.material.emissive = new THREE.Color(0x000000)
    hovered = null
  }
}

function onPointerMove(event) {
  const rect = renderer.domElement.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  const hits = raycaster.intersectObjects(columns, false)
  if (hits.length) {
    const mesh = hits[0].object
    if (hovered !== mesh) {
      clearHover()
      setHover(mesh)
    }
    const d = mesh.userData.district
    tooltip.value = {
      show: true,
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      name: d.name,
      price: d.avg_unit_price,
      count: d.property_count,
    }
    renderer.domElement.style.cursor = 'pointer'
  } else {
    clearHover()
    tooltip.value.show = false
    renderer.domElement.style.cursor = 'grab'
  }
}

function onClick() {
  if (hovered) emit('select', hovered.userData.district)
}

function onResize() {
  const el = container.value
  if (!el || !renderer) return
  const w = el.clientWidth
  const h = el.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

function animate() {
  frameId = requestAnimationFrame(animate)
  controls.update()
  renderer.render(scene, camera)
}

function initThree() {
  const el = container.value
  const w = el.clientWidth
  const h = el.clientHeight || 480

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b1120)
  scene.fog = new THREE.Fog(0x0b1120, 70, 180)

  camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 1000)
  camera.position.set(38, 40, 52)

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setSize(w, h)
  renderer.domElement.style.cursor = 'grab'
  el.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.minDistance = 22
  controls.maxDistance = 150
  controls.maxPolarAngle = Math.PI / 2.15
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.6
  controls.addEventListener('start', () => {
    controls.autoRotate = false
  })

  scene.add(new THREE.AmbientLight(0xffffff, 0.65))
  const key = new THREE.DirectionalLight(0xffffff, 1.1)
  key.position.set(30, 60, 30)
  scene.add(key)
  const fill = new THREE.DirectionalLight(0x88aaff, 0.4)
  fill.position.set(-40, 20, -30)
  scene.add(fill)

  raycaster = new THREE.Raycaster()
  pointer = new THREE.Vector2()

  buildColumns()

  renderer.domElement.addEventListener('pointermove', onPointerMove)
  renderer.domElement.addEventListener('click', onClick)
  renderer.domElement.addEventListener('pointerleave', () => {
    tooltip.value.show = false
    clearHover()
  })

  resizeObserver = new ResizeObserver(onResize)
  resizeObserver.observe(el)

  animate()
}

onMounted(initThree)

watch(
  () => props.districts,
  () => buildColumns(),
)

onBeforeUnmount(() => {
  if (frameId) cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  if (renderer) {
    renderer.domElement.removeEventListener('pointermove', onPointerMove)
    renderer.domElement.removeEventListener('click', onClick)
  }
  disposeGroup()
  renderer?.dispose()
  if (renderer?.domElement && container.value?.contains(renderer.domElement)) {
    container.value.removeChild(renderer.domElement)
  }
  scene = camera = renderer = controls = raycaster = pointer = null
})

function fmt(n) {
  return Number(n || 0).toLocaleString()
}
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
.map3d {
  position: relative;
  border-radius: var(--card-radius);
  overflow: hidden;
  background: #0b1120;
  box-shadow: var(--shadow);
}
.canvas-host {
  width: 100%;
  height: 100%;
}
.empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #94a3b8;
}
.tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(15, 23, 42, 0.92);
  border: 1px solid rgba(96, 165, 250, 0.5);
  color: #e2e8f0;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  min-width: 150px;
  z-index: 5;
}
.t-name {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 4px;
}
.t-row {
  line-height: 1.6;
}
.t-price {
  color: #fbbf24;
  font-size: 15px;
}
.muted-light {
  color: #94a3b8;
}
.hint {
  position: absolute;
  top: 12px;
  left: 14px;
  color: rgba(226, 232, 240, 0.7);
  font-size: 12px;
}
.legend {
  position: absolute;
  bottom: 14px;
  left: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.legend-bar {
  width: 140px;
  height: 10px;
  border-radius: 5px;
  background: linear-gradient(
    to right,
    hsl(160, 72%, 52%),
    hsl(80, 72%, 52%),
    hsl(40, 72%, 52%),
    hsl(0, 72%, 52%)
  );
}
</style>
