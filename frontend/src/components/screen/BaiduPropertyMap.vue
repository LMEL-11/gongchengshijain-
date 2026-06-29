<!-- 文件功能：在百度地图上展示真实房源点位、列表联动和信息窗详情。 -->
<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '' },
  address: { type: String, default: '' },
  payload: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])
const router = useRouter()

const mapEl = ref(null)
const listScrollEl = ref(null)
const mapError = ref('')
const selectedId = ref(null)

const ak = import.meta.env.VITE_BAIDU_MAP_AK || ''
// payload.items 已由后端限制为有坐标的房源，组件只负责把点位和列表联动展示。
// 函数功能：规范化地图房源列表输入，补齐展示字段。
const items = computed(() => props.payload?.items || [])
// 函数功能：计算地图列表的数量、均价和总价摘要。
const summary = computed(() => props.payload || {})

let map = null
let BMapApi = null
let markers = new Map()
let rowEls = new Map()
let scriptPromise = null

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(value) {
  return Number(value || 0).toLocaleString()
}

// 函数功能：转义信息窗 HTML 文本，避免特殊字符破坏结构。
function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

// 函数功能：加载百度地图脚本并复用已创建的加载任务。
function loadBaiduMap() {
  if (window.BMap) return Promise.resolve(window.BMap)
  if (!ak) return Promise.reject(new Error('请先配置 VITE_BAIDU_MAP_AK'))
  if (scriptPromise) return scriptPromise

  scriptPromise = new Promise((resolve, reject) => {
    const callback = `__baiduMapReady_${Date.now()}`
    window[callback] = () => {
      resolve(window.BMap)
      delete window[callback]
    }

    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${encodeURIComponent(ak)}&callback=${callback}`
    script.onerror = () => {
      delete window[callback]
      reject(new Error('百度地图脚本加载失败'))
    }
    document.head.appendChild(script)
  })
  return scriptPromise
}

// 函数功能：生成百度地图信息窗展示 HTML。
function infoHtml(item) {
  return `
    <div style="min-width:220px;color:#1f2937;font-size:13px;line-height:1.7">
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px">${escapeHtml(item.title)}</div>
      <div>${escapeHtml(item.layout || '暂无户型')} · ${item.area || '暂无'}㎡ · ${escapeHtml(item.district_name || '')}</div>
      <div>总价：<b style="color:#dc2626">${fmt(item.total_price)}</b> 万元</div>
      <div>单价：<b style="color:#2563eb">${fmt(item.unit_price)}</b> 元/㎡</div>
    </div>
  `
}

// 函数功能：打开指定房源的信息窗并同步选中状态。
function openInfo(item, point) {
  selectedId.value = item.id
  scrollToListItem(item.id)
  const info = new BMapApi.InfoWindow(infoHtml(item), {
    width: 260,
    title: '',
    enableMessage: false,
  })
  map.openInfoWindow(info, point)
}

// 函数功能：记录房源列表行 DOM，便于地图点击后滚动定位。
function setRowEl(id, el) {
  if (el) rowEls.set(id, el)
  else rowEls.delete(id)
}

// 函数功能：滚动列表到当前选中的房源行。
async function scrollToListItem(id) {
  await nextTick()
  const row = rowEls.get(id)
  if (!row || !listScrollEl.value) return
  row.scrollIntoView({ block: 'center', behavior: 'smooth' })
}

// 函数功能：清理百度地图覆盖物和信息窗状态。
function clearMap() {
  if (map) map.clearOverlays()
  markers.clear()
}

// 函数功能：触发百度地图重新计算视口尺寸。
function resizeMap() {
  if (!map) return
  requestAnimationFrame(() => {
    map?.checkResize?.()
  })
  setTimeout(() => {
    map?.checkResize?.()
  }, 120)
}

// 函数功能：在缺少坐标时根据城市区域地址定位地图中心。
function centerByAddress() {
  if (!map || !props.address) return
  const geocoder = new BMapApi.Geocoder()
  geocoder.getPoint(props.address, (point) => {
    if (point) map.centerAndZoom(point, 12)
  })
}

// 函数功能：根据房源点位重建百度地图标记和范围。
function renderMarkers() {
  if (!map || !BMapApi) return
  clearMap()
  selectedId.value = null

  // 只绘制经纬度完整的房源；前 30 个点附加单价标签，避免标签过多遮挡地图。
  const points = []
  items.value.forEach((item, index) => {
    if (!item.lng || !item.lat) return
    const point = new BMapApi.Point(item.lng, item.lat)
    points.push(point)

    const marker = new BMapApi.Marker(point)
    marker.addEventListener('click', () => openInfo(item, point))
    if (index < 30 && item.unit_price) {
      const label = new BMapApi.Label(`${fmt(item.unit_price)}元/㎡`, {
        offset: new BMapApi.Size(16, -18),
      })
      label.setStyle({
        color: '#0f172a',
        border: '1px solid rgba(37, 99, 235, .35)',
        borderRadius: '3px',
        padding: '1px 4px',
        background: 'rgba(255, 255, 255, .9)',
        fontSize: '11px',
      })
      marker.setLabel(label)
    }
    map.addOverlay(marker)
    markers.set(item.id, { marker, point, item })
  })

  // 视野优先覆盖全部真实点位；没有点位时回退到后端中心点或地址地理编码。
  if (points.length > 1) {
    map.setViewport(points, { margins: [50, 50, 50, 50] })
  } else if (points.length === 1) {
    map.centerAndZoom(points[0], 14)
  } else if (summary.value?.center?.lng && summary.value?.center?.lat) {
    map.centerAndZoom(new BMapApi.Point(summary.value.center.lng, summary.value.center.lat), 12)
  } else {
    centerByAddress()
  }
  resizeMap()
}

// 函数功能：初始化百度地图实例并渲染当前房源标记。
async function initMap() {
  if (!props.visible || !mapEl.value) return
  mapError.value = ''
  try {
    BMapApi = await loadBaiduMap()
    if (!mapEl.value) return
    if (!map) {
      map = new BMapApi.Map(mapEl.value, { enableMapClick: false })
      map.enableScrollWheelZoom(true)
      map.addControl(new BMapApi.NavigationControl())
      map.addControl(new BMapApi.ScaleControl())
    }
    resizeMap()
    renderMarkers()
  } catch (err) {
    mapError.value = err.message || '百度地图加载失败'
  }
}

// 函数功能：从列表聚焦房源并打开对应地图信息窗。
function focusItem(item) {
  const target = markers.get(item.id)
  if (!target || !map) return
  map.panTo(target.point)
  openInfo(target.item, target.point)
}

// 函数功能：跳转到房源详情页面。
function openDetail(item) {
  if (!item?.id) return
  router.push({ name: 'property-detail', params: { id: item.id } })
}

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      await nextTick()
      initMap()
    } else {
      selectedId.value = null
    }
  },
)

watch(
  () => props.payload,
  async () => {
    // 同一个弹窗内切换行政区或刷新 payload 时，只重绘点位，不重新创建地图实例。
    if (!props.visible) return
    await nextTick()
    if (map) renderMarkers()
    else initMap()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  clearMap()
  map = null
})
</script>

<template>
  <div v-show="visible" class="baidu-layer">
    <div class="baidu-panel">
      <header class="baidu-head">
        <div>
          <div class="baidu-title">{{ title }}</div>
          <div class="baidu-sub">
            {{ address }} · 坐标房源 {{ fmt(summary.coordinate_count) }} 套
            <span v-if="summary.returned_count < summary.coordinate_count">
              · 当前展示 {{ fmt(summary.returned_count) }} 套
            </span>
          </div>
        </div>
        <button class="close-btn" @click="emit('close')">关闭</button>
      </header>

      <div class="baidu-summary">
        <div>
          <b>{{ fmt(summary.property_count) }}</b>
          <span>区域房源</span>
        </div>
        <div>
          <b>{{ fmt(summary.avg_price) }}</b>
          <span>均价 元/㎡</span>
        </div>
        <div>
          <b>{{ fmt(summary.coordinate_count) }}</b>
          <span>可定位房源</span>
        </div>
      </div>

      <div class="baidu-body">
        <div class="map-box">
          <div ref="mapEl" class="baidu-map"></div>
          <div v-if="loading" class="map-state">房源点位加载中...</div>
          <div v-else-if="mapError" class="map-state">
            {{ mapError }}
            <small>在 frontend/.env.local 中配置 VITE_BAIDU_MAP_AK 后重启前端服务</small>
          </div>
          <div v-else-if="!items.length" class="map-state">该区域暂无可定位房源</div>
        </div>

        <aside class="property-list">
          <div class="list-head">地图房源</div>
          <div ref="listScrollEl" class="list-scroll">
            <div
              v-for="item in items"
              :key="item.id"
              :ref="(el) => setRowEl(item.id, el)"
              class="prop-row"
              :class="{ active: selectedId === item.id }"
            >
              <button class="prop-main" @click="focusItem(item)">
                <span class="prop-title">{{ item.title }}</span>
                <span class="prop-meta">{{ item.layout }} · {{ item.area }}㎡ · {{ item.district_name }}</span>
                <span class="prop-price">
                  <b>{{ fmt(item.total_price) }}</b> 万 · {{ fmt(item.unit_price) }} 元/㎡
                </span>
              </button>
              <button class="detail-btn" @click="openDetail(item)">详情</button>
            </div>
            <div v-if="!items.length && !loading" class="list-empty">暂无可展示房源</div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<style scoped>
.baidu-layer {
  position: absolute;
  inset: 86px 24px 22px;
  z-index: 20;
  display: flex;
  background: rgba(1, 10, 25, 0.72);
  backdrop-filter: blur(4px);
}
.baidu-panel {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
  border: 1px solid rgba(63, 224, 255, 0.45);
  background: rgba(4, 19, 43, 0.96);
  box-shadow: 0 0 40px rgba(63, 224, 255, 0.2);
}
.baidu-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(63, 224, 255, 0.18);
}
.baidu-title {
  color: #eaf6ff;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 1px;
}
.baidu-sub {
  margin-top: 5px;
  color: #7fb0d8;
  font-size: 13px;
}
.close-btn {
  cursor: pointer;
  border: 1px solid rgba(63, 224, 255, 0.45);
  border-radius: 4px;
  background: rgba(63, 224, 255, 0.1);
  color: #d6f1ff;
  padding: 6px 16px;
}
.close-btn:hover {
  background: rgba(63, 224, 255, 0.22);
}
.baidu-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 12px 18px;
}
.baidu-summary div {
  border: 1px solid rgba(63, 224, 255, 0.15);
  background: rgba(63, 224, 255, 0.06);
  padding: 8px 12px;
}
.baidu-summary b {
  margin-right: 8px;
  color: #5fe9ff;
  font-size: 22px;
  font-variant-numeric: tabular-nums;
}
.baidu-summary span {
  color: #9fc4e4;
  font-size: 13px;
}
.baidu-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 14px;
  min-height: 0;
  flex: 1;
  padding: 0 18px 18px;
}
.map-box {
  position: relative;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(63, 224, 255, 0.22);
}
.baidu-map {
  width: 100%;
  height: 100%;
  background: #071932;
}
.map-state {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  background: rgba(4, 19, 43, 0.72);
  color: #d6f1ff;
  font-size: 15px;
}
.map-state small {
  color: #7fb0d8;
}
.property-list {
  display: flex;
  min-height: 0;
  flex-direction: column;
  border: 1px solid rgba(63, 224, 255, 0.18);
  background: rgba(7, 25, 50, 0.56);
}
.list-head {
  padding: 10px 12px;
  color: #eaf6ff;
  font-weight: 700;
  border-bottom: 1px solid rgba(63, 224, 255, 0.16);
}
.list-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 8px;
}
.prop-row {
  width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 54px;
  align-items: center;
  gap: 8px;
  border: 1px solid transparent;
  border-bottom-color: rgba(63, 224, 255, 0.08);
  background: transparent;
  color: #cfe8ff;
  padding: 8px;
}
.prop-row:hover,
.prop-row.active {
  border-color: rgba(63, 224, 255, 0.36);
  background: rgba(63, 224, 255, 0.08);
}
.prop-main {
  min-width: 0;
  cursor: pointer;
  display: block;
  text-align: left;
  border: 0;
  background: transparent;
  color: inherit;
  padding: 0;
}
.prop-title {
  display: block;
  color: #eaf6ff;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.prop-meta,
.prop-price {
  display: block;
  margin-top: 4px;
  color: #8fb9dc;
  font-size: 12px;
}
.prop-price b {
  color: #ffd166;
}
.detail-btn {
  width: 54px;
  height: 30px;
  cursor: pointer;
  border: 1px solid rgba(63, 224, 255, 0.42);
  border-radius: 4px;
  background: rgba(63, 224, 255, 0.12);
  color: #dff8ff;
  font-size: 12px;
  font-weight: 700;
}
.detail-btn:hover {
  border-color: rgba(95, 233, 255, 0.75);
  background: rgba(63, 224, 255, 0.24);
}
.list-empty {
  padding-top: 40px;
  text-align: center;
  color: #7fb0d8;
}
.list-scroll::-webkit-scrollbar {
  width: 5px;
}
.list-scroll::-webkit-scrollbar-thumb {
  background: rgba(63, 224, 255, 0.3);
  border-radius: 3px;
}
</style>
