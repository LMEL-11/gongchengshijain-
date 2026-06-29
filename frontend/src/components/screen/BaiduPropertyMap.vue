<!-- 文件功能：在百度地图上展示真实房源点位、列表联动和信息窗详情。 -->
<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。
import { useRouter } from 'vue-router' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  visible: { type: Boolean, default: false }, // 逐行注释：配置当前对象字段。
  title: { type: String, default: '' }, // 逐行注释：配置当前对象字段。
  address: { type: String, default: '' }, // 逐行注释：配置当前对象字段。
  payload: { type: Object, default: () => ({}) }, // 逐行注释：配置当前对象字段。
  loading: { type: Boolean, default: false }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。
const emit = defineEmits(['close']) // 逐行注释：声明并初始化当前变量。
const router = useRouter() // 逐行注释：声明并初始化当前变量。

const mapEl = ref(null) // 逐行注释：声明并初始化当前变量。
const listScrollEl = ref(null) // 逐行注释：声明并初始化当前变量。
const mapError = ref('') // 逐行注释：声明并初始化当前变量。
const selectedId = ref(null) // 逐行注释：声明并初始化当前变量。

const ak = import.meta.env.VITE_BAIDU_MAP_AK || '' // 逐行注释：声明并初始化当前变量。
// 函数功能：规范化地图房源列表输入，补齐展示字段。
const items = computed(() => props.payload?.items || []) // 逐行注释：声明并初始化当前变量。
// 函数功能：计算地图列表的数量、均价和总价摘要。
const summary = computed(() => props.payload || {}) // 逐行注释：声明并初始化当前变量。

let map = null // 逐行注释：声明并初始化当前变量。
let BMapApi = null // 逐行注释：声明并初始化当前变量。
let markers = new Map() // 逐行注释：声明并初始化当前变量。
let rowEls = new Map() // 逐行注释：声明并初始化当前变量。
let scriptPromise = null // 逐行注释：声明并初始化当前变量。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(value) { // 逐行注释：声明当前函数入口。
  return Number(value || 0).toLocaleString() // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：转义信息窗 HTML 文本，避免特殊字符破坏结构。
function escapeHtml(value) { // 逐行注释：声明当前函数入口。
  return String(value ?? '') // 逐行注释：返回当前表达式结果。
    .replace(/&/g, '&amp;') // 逐行注释：执行本行前端逻辑。
    .replace(/</g, '&lt;') // 逐行注释：执行本行前端逻辑。
    .replace(/>/g, '&gt;') // 逐行注释：执行本行前端逻辑。
    .replace(/"/g, '&quot;') // 逐行注释：执行本行前端逻辑。
    .replace(/'/g, '&#39;') // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：加载百度地图脚本并复用已创建的加载任务。
function loadBaiduMap() { // 逐行注释：声明当前函数入口。
  if (window.BMap) return Promise.resolve(window.BMap) // 逐行注释：根据条件判断是否执行分支。
  if (!ak) return Promise.reject(new Error('请先配置 VITE_BAIDU_MAP_AK')) // 逐行注释：根据条件判断是否执行分支。
  if (scriptPromise) return scriptPromise // 逐行注释：根据条件判断是否执行分支。

  scriptPromise = new Promise((resolve, reject) => { // 逐行注释：执行本行前端逻辑。
    const callback = `__baiduMapReady_${Date.now()}` // 逐行注释：声明并初始化当前变量。
    window[callback] = () => { // 逐行注释：执行本行前端逻辑。
      resolve(window.BMap) // 逐行注释：执行本行前端逻辑。
      delete window[callback] // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。

    const script = document.createElement('script') // 逐行注释：声明并初始化当前变量。
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${encodeURIComponent(ak)}&callback=${callback}` // 逐行注释：赋值或更新当前变量/状态。
    script.onerror = () => { // 逐行注释：执行本行前端逻辑。
      delete window[callback] // 逐行注释：执行本行前端逻辑。
      reject(new Error('百度地图脚本加载失败')) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
    document.head.appendChild(script) // 逐行注释：执行本行前端逻辑。
  }) // 逐行注释：执行本行前端逻辑。
  return scriptPromise // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：生成百度地图信息窗展示 HTML。
function infoHtml(item) { // 逐行注释：声明当前函数入口。
  return ` // 逐行注释：返回当前表达式结果。
    <div style="min-width:220px;color:#1f2937;font-size:13px;line-height:1.7">
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px">${escapeHtml(item.title)}</div>
      <div>${escapeHtml(item.layout || '暂无户型')} · ${item.area || '暂无'}㎡ · ${escapeHtml(item.district_name || '')}</div>
      <div>总价：<b style="color:#dc2626">${fmt(item.total_price)}</b> 万元</div>
      <div>单价：<b style="color:#2563eb">${fmt(item.unit_price)}</b> 元/㎡</div>
    </div>
  `
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：打开指定房源的信息窗并同步选中状态。
function openInfo(item, point) { // 逐行注释：声明当前函数入口。
  selectedId.value = item.id // 逐行注释：赋值或更新当前变量/状态。
  scrollToListItem(item.id) // 逐行注释：执行本行前端逻辑。
  const info = new BMapApi.InfoWindow(infoHtml(item), { // 逐行注释：声明并初始化当前变量。
    width: 260, // 逐行注释：配置当前对象字段。
    title: '', // 逐行注释：配置当前对象字段。
    enableMessage: false, // 逐行注释：配置当前对象字段。
  }) // 逐行注释：执行本行前端逻辑。
  map.openInfoWindow(info, point) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：记录房源列表行 DOM，便于地图点击后滚动定位。
function setRowEl(id, el) { // 逐行注释：声明当前函数入口。
  if (el) rowEls.set(id, el) // 逐行注释：根据条件判断是否执行分支。
  else rowEls.delete(id) // 逐行注释：处理条件不满足时的分支。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：滚动列表到当前选中的房源行。
async function scrollToListItem(id) { // 逐行注释：声明当前函数入口。
  await nextTick() // 逐行注释：等待异步操作完成。
  const row = rowEls.get(id) // 逐行注释：声明并初始化当前变量。
  if (!row || !listScrollEl.value) return // 逐行注释：根据条件判断是否执行分支。
  row.scrollIntoView({ block: 'center', behavior: 'smooth' }) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：清理百度地图覆盖物和信息窗状态。
function clearMap() { // 逐行注释：声明当前函数入口。
  if (map) map.clearOverlays() // 逐行注释：根据条件判断是否执行分支。
  markers.clear() // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：触发百度地图重新计算视口尺寸。
function resizeMap() { // 逐行注释：声明当前函数入口。
  if (!map) return // 逐行注释：根据条件判断是否执行分支。
  requestAnimationFrame(() => { // 逐行注释：执行本行前端逻辑。
    map?.checkResize?.() // 逐行注释：执行本行前端逻辑。
  }) // 逐行注释：执行本行前端逻辑。
  setTimeout(() => { // 逐行注释：执行本行前端逻辑。
    map?.checkResize?.() // 逐行注释：执行本行前端逻辑。
  }, 120) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：在缺少坐标时根据城市区域地址定位地图中心。
function centerByAddress() { // 逐行注释：声明当前函数入口。
  if (!map || !props.address) return // 逐行注释：根据条件判断是否执行分支。
  const geocoder = new BMapApi.Geocoder() // 逐行注释：声明并初始化当前变量。
  geocoder.getPoint(props.address, (point) => { // 逐行注释：执行本行前端逻辑。
    if (point) map.centerAndZoom(point, 12) // 逐行注释：根据条件判断是否执行分支。
  }) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据房源点位重建百度地图标记和范围。
function renderMarkers() { // 逐行注释：声明当前函数入口。
  if (!map || !BMapApi) return // 逐行注释：根据条件判断是否执行分支。
  clearMap() // 逐行注释：执行本行前端逻辑。
  selectedId.value = null // 逐行注释：赋值或更新当前变量/状态。

  const points = [] // 逐行注释：声明并初始化当前变量。
  items.value.forEach((item, index) => { // 逐行注释：执行本行前端逻辑。
    if (!item.lng || !item.lat) return // 逐行注释：根据条件判断是否执行分支。
    const point = new BMapApi.Point(item.lng, item.lat) // 逐行注释：声明并初始化当前变量。
    points.push(point) // 逐行注释：执行本行前端逻辑。

    const marker = new BMapApi.Marker(point) // 逐行注释：声明并初始化当前变量。
    marker.addEventListener('click', () => openInfo(item, point)) // 逐行注释：执行本行前端逻辑。
    if (index < 30 && item.unit_price) { // 逐行注释：根据条件判断是否执行分支。
      const label = new BMapApi.Label(`${fmt(item.unit_price)}元/㎡`, { // 逐行注释：声明并初始化当前变量。
        offset: new BMapApi.Size(16, -18), // 逐行注释：配置当前对象字段。
      }) // 逐行注释：执行本行前端逻辑。
      label.setStyle({ // 逐行注释：执行本行前端逻辑。
        color: '#0f172a', // 逐行注释：配置当前对象字段。
        border: '1px solid rgba(37, 99, 235, .35)', // 逐行注释：配置当前对象字段。
        borderRadius: '3px', // 逐行注释：配置当前对象字段。
        padding: '1px 4px', // 逐行注释：配置当前对象字段。
        background: 'rgba(255, 255, 255, .9)', // 逐行注释：配置当前对象字段。
        fontSize: '11px', // 逐行注释：配置当前对象字段。
      }) // 逐行注释：执行本行前端逻辑。
      marker.setLabel(label) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
    map.addOverlay(marker) // 逐行注释：执行本行前端逻辑。
    markers.set(item.id, { marker, point, item }) // 逐行注释：执行本行前端逻辑。
  }) // 逐行注释：执行本行前端逻辑。

  if (points.length > 1) { // 逐行注释：根据条件判断是否执行分支。
    map.setViewport(points, { margins: [50, 50, 50, 50] }) // 逐行注释：执行本行前端逻辑。
  } else if (points.length === 1) { // 逐行注释：执行本行前端逻辑。
    map.centerAndZoom(points[0], 14) // 逐行注释：执行本行前端逻辑。
  } else if (summary.value?.center?.lng && summary.value?.center?.lat) { // 逐行注释：执行本行前端逻辑。
    map.centerAndZoom(new BMapApi.Point(summary.value.center.lng, summary.value.center.lat), 12) // 逐行注释：执行本行前端逻辑。
  } else { // 逐行注释：执行本行前端逻辑。
    centerByAddress() // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。
  resizeMap() // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：初始化百度地图实例并渲染当前房源标记。
async function initMap() { // 逐行注释：声明当前函数入口。
  if (!props.visible || !mapEl.value) return // 逐行注释：根据条件判断是否执行分支。
  mapError.value = '' // 逐行注释：赋值或更新当前变量/状态。
  try { // 逐行注释：开始执行可能失败的逻辑。
    BMapApi = await loadBaiduMap() // 逐行注释：赋值或更新当前变量/状态。
    if (!mapEl.value) return // 逐行注释：根据条件判断是否执行分支。
    if (!map) { // 逐行注释：根据条件判断是否执行分支。
      map = new BMapApi.Map(mapEl.value, { enableMapClick: false }) // 逐行注释：赋值或更新当前变量/状态。
      map.enableScrollWheelZoom(true) // 逐行注释：执行本行前端逻辑。
      map.addControl(new BMapApi.NavigationControl()) // 逐行注释：执行本行前端逻辑。
      map.addControl(new BMapApi.ScaleControl()) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
    resizeMap() // 逐行注释：执行本行前端逻辑。
    renderMarkers() // 逐行注释：执行本行前端逻辑。
  } catch (err) { // 逐行注释：执行本行前端逻辑。
    mapError.value = err.message || '百度地图加载失败' // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：从列表聚焦房源并打开对应地图信息窗。
function focusItem(item) { // 逐行注释：声明当前函数入口。
  const target = markers.get(item.id) // 逐行注释：声明并初始化当前变量。
  if (!target || !map) return // 逐行注释：根据条件判断是否执行分支。
  map.panTo(target.point) // 逐行注释：执行本行前端逻辑。
  openInfo(target.item, target.point) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：跳转到房源详情页面。
function openDetail(item) { // 逐行注释：声明当前函数入口。
  if (!item?.id) return // 逐行注释：根据条件判断是否执行分支。
  router.push({ name: 'property-detail', params: { id: item.id } }) // 逐行注释：执行路由跳转或路由操作。
} // 逐行注释：结束当前代码块或数据结构。

watch( // 逐行注释：监听响应式数据变化。
  () => props.visible, // 逐行注释：继续声明当前列表项或参数项。
  async (visible) => { // 逐行注释：执行本行前端逻辑。
    if (visible) { // 逐行注释：根据条件判断是否执行分支。
      await nextTick() // 逐行注释：等待异步操作完成。
      initMap() // 逐行注释：执行本行前端逻辑。
    } else { // 逐行注释：执行本行前端逻辑。
      selectedId.value = null // 逐行注释：赋值或更新当前变量/状态。
    } // 逐行注释：结束当前代码块或数据结构。
  }, // 逐行注释：结束当前代码块或数据结构。
) // 逐行注释：结束当前代码块或数据结构。

watch( // 逐行注释：监听响应式数据变化。
  () => props.payload, // 逐行注释：继续声明当前列表项或参数项。
  async () => { // 逐行注释：执行本行前端逻辑。
    if (!props.visible) return // 逐行注释：根据条件判断是否执行分支。
    await nextTick() // 逐行注释：等待异步操作完成。
    if (map) renderMarkers() // 逐行注释：根据条件判断是否执行分支。
    else initMap() // 逐行注释：处理条件不满足时的分支。
  }, // 逐行注释：结束当前代码块或数据结构。
  { deep: true }, // 逐行注释：配置当前对象字段。
) // 逐行注释：结束当前代码块或数据结构。

onBeforeUnmount(() => { // 逐行注释：注册 Vue 生命周期回调。
  clearMap() // 逐行注释：执行本行前端逻辑。
  map = null // 逐行注释：赋值或更新当前变量/状态。
}) // 逐行注释：执行本行前端逻辑。
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
.baidu-layer { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  inset: 86px 24px 22px; /* 逐行注释：设置当前样式属性。 */
  z-index: 20; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  background: rgba(1, 10, 25, 0.72); /* 逐行注释：设置当前样式属性。 */
  backdrop-filter: blur(4px); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-panel { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 逐行注释：设置当前样式属性。 */
  background: rgba(4, 19, 43, 0.96); /* 逐行注释：设置当前样式属性。 */
  box-shadow: 0 0 40px rgba(63, 224, 255, 0.2); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-head { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: space-between; /* 逐行注释：设置当前样式属性。 */
  padding: 14px 18px; /* 逐行注释：设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-title { /* 逐行注释：开始当前样式规则块。 */
  color: #eaf6ff; /* 逐行注释：设置当前样式属性。 */
  font-size: 20px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  letter-spacing: 1px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-sub { /* 逐行注释：开始当前样式规则块。 */
  margin-top: 5px; /* 逐行注释：设置当前样式属性。 */
  color: #7fb0d8; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.close-btn { /* 逐行注释：开始当前样式规则块。 */
  cursor: pointer; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 逐行注释：设置当前样式属性。 */
  border-radius: 4px; /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.1); /* 逐行注释：设置当前样式属性。 */
  color: #d6f1ff; /* 逐行注释：设置当前样式属性。 */
  padding: 6px 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.close-btn:hover { /* 逐行注释：开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.22); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-summary { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: repeat(3, 1fr); /* 逐行注释：设置当前样式属性。 */
  gap: 10px; /* 逐行注释：设置当前样式属性。 */
  padding: 12px 18px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-summary div { /* 逐行注释：开始当前样式规则块。 */
  border: 1px solid rgba(63, 224, 255, 0.15); /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.06); /* 逐行注释：设置当前样式属性。 */
  padding: 8px 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-summary b { /* 逐行注释：开始当前样式规则块。 */
  margin-right: 8px; /* 逐行注释：设置当前样式属性。 */
  color: #5fe9ff; /* 逐行注释：设置当前样式属性。 */
  font-size: 22px; /* 逐行注释：设置当前样式属性。 */
  font-variant-numeric: tabular-nums; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-summary span { /* 逐行注释：开始当前样式规则块。 */
  color: #9fc4e4; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-body { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: minmax(0, 1fr) 360px; /* 逐行注释：设置当前样式属性。 */
  gap: 14px; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  padding: 0 18px 18px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.map-box { /* 逐行注释：开始当前样式规则块。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  overflow: hidden; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.22); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.baidu-map { /* 逐行注释：开始当前样式规则块。 */
  width: 100%; /* 逐行注释：设置当前样式属性。 */
  height: 100%; /* 逐行注释：设置当前样式属性。 */
  background: #071932; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.map-state { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  inset: 0; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  gap: 8px; /* 逐行注释：设置当前样式属性。 */
  background: rgba(4, 19, 43, 0.72); /* 逐行注释：设置当前样式属性。 */
  color: #d6f1ff; /* 逐行注释：设置当前样式属性。 */
  font-size: 15px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.map-state small { /* 逐行注释：开始当前样式规则块。 */
  color: #7fb0d8; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.property-list { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.18); /* 逐行注释：设置当前样式属性。 */
  background: rgba(7, 25, 50, 0.56); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.list-head { /* 逐行注释：开始当前样式规则块。 */
  padding: 10px 12px; /* 逐行注释：设置当前样式属性。 */
  color: #eaf6ff; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.16); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.list-scroll { /* 逐行注释：开始当前样式规则块。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  overflow-y: auto; /* 逐行注释：设置当前样式属性。 */
  padding: 8px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-row { /* 逐行注释：开始当前样式规则块。 */
  width: 100%; /* 逐行注释：设置当前样式属性。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: minmax(0, 1fr) 54px; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 8px; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid transparent; /* 逐行注释：设置当前样式属性。 */
  border-bottom-color: rgba(63, 224, 255, 0.08); /* 逐行注释：设置当前样式属性。 */
  background: transparent; /* 逐行注释：设置当前样式属性。 */
  color: #cfe8ff; /* 逐行注释：设置当前样式属性。 */
  padding: 8px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-row:hover, /* 逐行注释：设置当前样式属性。 */
.prop-row.active { /* 逐行注释：开始当前样式规则块。 */
  border-color: rgba(63, 224, 255, 0.36); /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.08); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-main { /* 逐行注释：开始当前样式规则块。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
  cursor: pointer; /* 逐行注释：设置当前样式属性。 */
  display: block; /* 逐行注释：设置当前样式属性。 */
  text-align: left; /* 逐行注释：设置当前样式属性。 */
  border: 0; /* 逐行注释：设置当前样式属性。 */
  background: transparent; /* 逐行注释：设置当前样式属性。 */
  color: inherit; /* 逐行注释：设置当前样式属性。 */
  padding: 0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-title { /* 逐行注释：开始当前样式规则块。 */
  display: block; /* 逐行注释：设置当前样式属性。 */
  color: #eaf6ff; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
  overflow: hidden; /* 逐行注释：设置当前样式属性。 */
  text-overflow: ellipsis; /* 逐行注释：设置当前样式属性。 */
  white-space: nowrap; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-meta, /* 逐行注释：声明当前样式规则。 */
.prop-price { /* 逐行注释：开始当前样式规则块。 */
  display: block; /* 逐行注释：设置当前样式属性。 */
  margin-top: 4px; /* 逐行注释：设置当前样式属性。 */
  color: #8fb9dc; /* 逐行注释：设置当前样式属性。 */
  font-size: 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-price b { /* 逐行注释：开始当前样式规则块。 */
  color: #ffd166; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.detail-btn { /* 逐行注释：开始当前样式规则块。 */
  width: 54px; /* 逐行注释：设置当前样式属性。 */
  height: 30px; /* 逐行注释：设置当前样式属性。 */
  cursor: pointer; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.42); /* 逐行注释：设置当前样式属性。 */
  border-radius: 4px; /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.12); /* 逐行注释：设置当前样式属性。 */
  color: #dff8ff; /* 逐行注释：设置当前样式属性。 */
  font-size: 12px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.detail-btn:hover { /* 逐行注释：开始当前样式规则块。 */
  border-color: rgba(95, 233, 255, 0.75); /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.24); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.list-empty { /* 逐行注释：开始当前样式规则块。 */
  padding-top: 40px; /* 逐行注释：设置当前样式属性。 */
  text-align: center; /* 逐行注释：设置当前样式属性。 */
  color: #7fb0d8; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.list-scroll::-webkit-scrollbar { /* 逐行注释：开始当前样式规则块。 */
  width: 5px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.list-scroll::-webkit-scrollbar-thumb { /* 逐行注释：开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.3); /* 逐行注释：设置当前样式属性。 */
  border-radius: 3px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
