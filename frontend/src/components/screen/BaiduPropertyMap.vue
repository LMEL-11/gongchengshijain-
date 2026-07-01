<!-- 文件功能：在百度地图上展示真实房源点位、列表联动和信息窗详情。 -->
<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue' // 导入 { computed, nextTick, onBeforeUnmount, ref, watch }，供当前前端模块渲染或交互逻辑使用。
import { useRouter } from 'vue-router' // 导入 { useRouter }，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  visible: { type: Boolean, default: false }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  title: { type: String, default: '' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  address: { type: String, default: '' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  payload: { type: Object, default: () => ({}) }, // 设置 payload: { type: Object, default:  的值，作为后续渲染、计算或请求的输入。
  loading: { type: Boolean, default: false }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。
const emit = defineEmits(['close']) // 创建 emit，用于保存页面状态、计算结果或接口参数。
const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。

const mapEl = ref(null) // 创建 mapEl，用于保存页面状态、计算结果或接口参数。
const listScrollEl = ref(null) // 创建 listScrollEl，用于保存页面状态、计算结果或接口参数。
const mapError = ref('') // 创建 mapError，用于保存页面状态、计算结果或接口参数。
const selectedId = ref(null) // 创建 selectedId，用于保存页面状态、计算结果或接口参数。

const ak = import.meta.env.VITE_BAIDU_MAP_AK || '' // 创建 ak，用于保存页面状态、计算结果或接口参数。
// payload.items 已由后端限制为有坐标的房源，组件只负责把点位和列表联动展示。
// 函数功能：规范化地图房源列表输入，补齐展示字段。
const items = computed(() => props.payload?.items || []) // 创建 items，用于保存页面状态、计算结果或接口参数。
// 函数功能：计算地图列表的数量、均价和总价摘要。
const summary = computed(() => props.payload || {}) // 创建 summary，用于保存页面状态、计算结果或接口参数。

let map = null // 创建 map，用于保存页面状态、计算结果或接口参数。
let BMapApi = null // 创建 BMapApi，用于保存页面状态、计算结果或接口参数。
let markers = new Map() // 创建 markers，用于保存页面状态、计算结果或接口参数。
let rowEls = new Map() // 创建 rowEls，用于保存页面状态、计算结果或接口参数。
let scriptPromise = null // 创建 scriptPromise，用于保存页面状态、计算结果或接口参数。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(value) { // 定义 fmt 函数，处理页面交互、数据加载或状态同步。
  return Number(value || 0).toLocaleString() // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：转义信息窗 HTML 文本，避免特殊字符破坏结构。
function escapeHtml(value) { // 定义 escapeHtml 函数，处理页面交互、数据加载或状态同步。
  return String(value ?? '') // 返回整理后的数据、组件配置或渲染结果。
    .replace(/&/g, '&amp;') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    .replace(/</g, '&lt;') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    .replace(/>/g, '&gt;') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    .replace(/"/g, '&quot;') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    .replace(/'/g, '&#39;') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：加载百度地图脚本并复用已创建的加载任务。
function loadBaiduMap() { // 定义 loadBaiduMap 函数，处理页面交互、数据加载或状态同步。
  if (window.BMap) return Promise.resolve(window.BMap) // 根据当前页面状态或接口结果决定是否进入该分支。
  if (!ak) return Promise.reject(new Error('请先配置 VITE_BAIDU_MAP_AK')) // 根据当前页面状态或接口结果决定是否进入该分支。
  if (scriptPromise) return scriptPromise // 根据当前页面状态或接口结果决定是否进入该分支。

  scriptPromise = new Promise((resolve, reject) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    const callback = `__baiduMapReady_${Date.now()}` // 创建 callback，用于保存页面状态、计算结果或接口参数。
    window[callback] = () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
      resolve(window.BMap) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      delete window[callback] // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。

    const script = document.createElement('script') // 创建 script，用于保存页面状态、计算结果或接口参数。
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${encodeURIComponent(ak)}&callback=${callback}` // 设置百度地图脚本地址，并带上 AK 和回调函数名。
    script.onerror = () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
      delete window[callback] // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      reject(new Error('百度地图脚本加载失败')) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    document.head.appendChild(script) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。
  return scriptPromise // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：生成百度地图信息窗展示 HTML。
function infoHtml(item) { // 定义 infoHtml 函数，处理页面交互、数据加载或状态同步。
  // 拼接百度地图信息窗 HTML，展示房源标题、户型、面积、总价和单价。
  return `
    <div style="min-width:220px;color:#1f2937;font-size:13px;line-height:1.7">
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px">${escapeHtml(item.title)}</div>
      <div>${escapeHtml(item.layout || '暂无户型')} · ${item.area || '暂无'}㎡ · ${escapeHtml(item.district_name || '')}</div>
      <div>总价：<b style="color:#dc2626">${fmt(item.total_price)}</b> 万元</div>
      <div>单价：<b style="color:#2563eb">${fmt(item.unit_price)}</b> 元/㎡</div>
    </div>
  `
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：打开指定房源的信息窗并同步选中状态。
function openInfo(item, point) { // 定义 openInfo 函数，处理页面交互、数据加载或状态同步。
  selectedId.value = item.id // 更新 selectedId.value 响应式状态，让页面展示与最新数据保持一致。
  scrollToListItem(item.id) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  const info = new BMapApi.InfoWindow(infoHtml(item), { // 创建 info，用于保存页面状态、计算结果或接口参数。
    width: 260, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    title: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    enableMessage: false, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。
  map.openInfoWindow(info, point) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：记录房源列表行 DOM，便于地图点击后滚动定位。
function setRowEl(id, el) { // 定义 setRowEl 函数，处理页面交互、数据加载或状态同步。
  if (el) rowEls.set(id, el) // 根据当前页面状态或接口结果决定是否进入该分支。
  else rowEls.delete(id) // 处理前面条件未命中的前端交互分支。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：滚动列表到当前选中的房源行。
async function scrollToListItem(id) { // 定义 scrollToListItem 函数，处理页面交互、数据加载或状态同步。
  await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
  const row = rowEls.get(id) // 创建 row，用于保存页面状态、计算结果或接口参数。
  if (!row || !listScrollEl.value) return // 根据当前页面状态或接口结果决定是否进入该分支。
  row.scrollIntoView({ block: 'center', behavior: 'smooth' }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：清理百度地图覆盖物和信息窗状态。
function clearMap() { // 定义 clearMap 函数，处理页面交互、数据加载或状态同步。
  if (map) map.clearOverlays() // 根据当前页面状态或接口结果决定是否进入该分支。
  markers.clear() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：触发百度地图重新计算视口尺寸。
function resizeMap() { // 定义 resizeMap 函数，处理页面交互、数据加载或状态同步。
  if (!map) return // 根据当前页面状态或接口结果决定是否进入该分支。
  requestAnimationFrame(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    map?.checkResize?.() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。
  setTimeout(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    map?.checkResize?.() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, 120) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：在缺少坐标时根据城市区域地址定位地图中心。
function centerByAddress() { // 定义 centerByAddress 函数，处理页面交互、数据加载或状态同步。
  if (!map || !props.address) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const geocoder = new BMapApi.Geocoder() // 创建 geocoder，用于保存页面状态、计算结果或接口参数。
  geocoder.getPoint(props.address, (point) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    if (point) map.centerAndZoom(point, 12) // 根据当前页面状态或接口结果决定是否进入该分支。
  }) // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据房源点位重建百度地图标记和范围。
function renderMarkers() { // 定义 renderMarkers 函数，处理页面交互、数据加载或状态同步。
  if (!map || !BMapApi) return // 根据当前页面状态或接口结果决定是否进入该分支。
  clearMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  selectedId.value = null // 更新 selectedId.value 响应式状态，让页面展示与最新数据保持一致。

  // 只绘制经纬度完整的房源；前 30 个点附加单价标签，避免标签过多遮挡地图。
  const points = [] // 创建 points，用于保存页面状态、计算结果或接口参数。
  items.value.forEach((item, index) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    if (!item.lng || !item.lat) return // 根据当前页面状态或接口结果决定是否进入该分支。
    const point = new BMapApi.Point(item.lng, item.lat) // 创建 point，用于保存页面状态、计算结果或接口参数。
    points.push(point) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

    const marker = new BMapApi.Marker(point) // 创建 marker，用于保存页面状态、计算结果或接口参数。
    marker.addEventListener('click', () => openInfo(item, point)) // 设置 marker.addEventListener('click',  的值，作为后续渲染、计算或请求的输入。
    if (index < 30 && item.unit_price) { // 根据当前页面状态或接口结果决定是否进入该分支。
      const label = new BMapApi.Label(`${fmt(item.unit_price)}元/㎡`, { // 创建 label，用于保存页面状态、计算结果或接口参数。
        offset: new BMapApi.Size(16, -18), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      }) // 结束当前函数、对象、数组或组件配置块。
      label.setStyle({ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        color: '#0f172a', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        border: '1px solid rgba(37, 99, 235, .35)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        borderRadius: '3px', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        padding: '1px 4px', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        background: 'rgba(255, 255, 255, .9)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        fontSize: '11px', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      }) // 结束当前函数、对象、数组或组件配置块。
      marker.setLabel(label) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    map.addOverlay(marker) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    markers.set(item.id, { marker, point, item }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。

  // 视野优先覆盖全部真实点位；没有点位时回退到后端中心点或地址地理编码。
  if (points.length > 1) { // 根据当前页面状态或接口结果决定是否进入该分支。
    map.setViewport(points, { margins: [50, 50, 50, 50] }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } else if (points.length === 1) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    map.centerAndZoom(points[0], 14) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } else if (summary.value?.center?.lng && summary.value?.center?.lat) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    map.centerAndZoom(new BMapApi.Point(summary.value.center.lng, summary.value.center.lat), 12) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    centerByAddress() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  resizeMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：初始化百度地图实例并渲染当前房源标记。
async function initMap() { // 定义 initMap 函数，处理页面交互、数据加载或状态同步。
  if (!props.visible || !mapEl.value) return // 根据当前页面状态或接口结果决定是否进入该分支。
  mapError.value = '' // 更新 mapError.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    BMapApi = await loadBaiduMap() // 等待异步接口或资源加载完成，再继续更新页面状态。
    if (!mapEl.value) return // 根据当前页面状态或接口结果决定是否进入该分支。
    if (!map) { // 根据当前页面状态或接口结果决定是否进入该分支。
      map = new BMapApi.Map(mapEl.value, { enableMapClick: false }) // 更新 map 响应式状态，让页面展示与最新数据保持一致。
      map.enableScrollWheelZoom(true) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      map.addControl(new BMapApi.NavigationControl()) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      map.addControl(new BMapApi.ScaleControl()) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    resizeMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    renderMarkers() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } catch (err) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    mapError.value = err.message || '百度地图加载失败' // 更新 mapError.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：从列表聚焦房源并打开对应地图信息窗。
function focusItem(item) { // 定义 focusItem 函数，处理页面交互、数据加载或状态同步。
  const target = markers.get(item.id) // 创建 target，用于保存页面状态、计算结果或接口参数。
  if (!target || !map) return // 根据当前页面状态或接口结果决定是否进入该分支。
  map.panTo(target.point) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  openInfo(target.item, target.point) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：跳转到房源详情页面。
function openDetail(item) { // 定义 openDetail 函数，处理页面交互、数据加载或状态同步。
  if (!item?.id) return // 根据当前页面状态或接口结果决定是否进入该分支。
  router.push({ name: 'property-detail', params: { id: item.id } }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => props.visible, // 设置  的值，作为后续渲染、计算或请求的输入。
  async (visible) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    if (visible) { // 根据当前页面状态或接口结果决定是否进入该分支。
      await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
      initMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      selectedId.value = null // 更新 selectedId.value 响应式状态，让页面展示与最新数据保持一致。
    } // 结束当前函数、对象、数组或组件配置块。
  }, // 结束当前函数、对象、数组或组件配置块。
) // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => props.payload, // 设置  的值，作为后续渲染、计算或请求的输入。
  async () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    // 同一个弹窗内切换行政区或刷新 payload 时，只重绘点位，不重新创建地图实例。
    if (!props.visible) return // 根据当前页面状态或接口结果决定是否进入该分支。
    await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
    if (map) renderMarkers() // 根据当前页面状态或接口结果决定是否进入该分支。
    else initMap() // 处理前面条件未命中的前端交互分支。
  }, // 结束当前函数、对象、数组或组件配置块。
  { deep: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。

onBeforeUnmount(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  clearMap() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  map = null // 设置 map 的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。
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
.baidu-layer { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  inset: 86px 24px 22px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  z-index: 20; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: flex; /* 设置元素布局模式。 */
  background: rgba(1, 10, 25, 0.72); /* 设置背景样式。 */
  backdrop-filter: blur(4px); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.baidu-panel { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 设置边框样式。 */
  background: rgba(4, 19, 43, 0.96); /* 设置背景样式。 */
  box-shadow: 0 0 40px rgba(63, 224, 255, 0.2); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.baidu-head { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
  padding: 14px 18px; /* 设置元素内边距。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.baidu-title { /* 定义当前选择器的样式作用域。 */
  color: #eaf6ff; /* 设置文字颜色。 */
  font-size: 20px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
  letter-spacing: 1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.baidu-sub { /* 定义当前选择器的样式作用域。 */
  margin-top: 5px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #7fb0d8; /* 设置文字颜色。 */
  font-size: 13px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.close-btn { /* 定义当前选择器的样式作用域。 */
  cursor: pointer; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 设置边框样式。 */
  border-radius: 4px; /* 设置圆角半径。 */
  background: rgba(63, 224, 255, 0.1); /* 设置背景样式。 */
  color: #d6f1ff; /* 设置文字颜色。 */
  padding: 6px 16px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.close-btn:hover { /* 定义当前选择器的样式作用域。 */
  background: rgba(63, 224, 255, 0.22); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.baidu-summary { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: repeat(3, 1fr); /* 设置网格列布局。 */
  gap: 10px; /* 设置子元素之间的间距。 */
  padding: 12px 18px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.baidu-summary div { /* 定义当前选择器的样式作用域。 */
  border: 1px solid rgba(63, 224, 255, 0.15); /* 设置边框样式。 */
  background: rgba(63, 224, 255, 0.06); /* 设置背景样式。 */
  padding: 8px 12px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.baidu-summary b { /* 定义当前选择器的样式作用域。 */
  margin-right: 8px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #5fe9ff; /* 设置文字颜色。 */
  font-size: 22px; /* 设置文字大小。 */
  font-variant-numeric: tabular-nums; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.baidu-summary span { /* 定义当前选择器的样式作用域。 */
  color: #9fc4e4; /* 设置文字颜色。 */
  font-size: 13px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.baidu-body { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: minmax(0, 1fr) 360px; /* 设置网格列布局。 */
  gap: 14px; /* 设置子元素之间的间距。 */
  min-height: 0; /* 设置元素最小高度。 */
  flex: 1; /* 设置弹性布局占比。 */
  padding: 0 18px 18px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.map-box { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  min-height: 0; /* 设置元素最小高度。 */
  overflow: hidden; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border: 1px solid rgba(63, 224, 255, 0.22); /* 设置边框样式。 */
} /* 结束当前样式规则块。 */
.baidu-map { /* 定义当前选择器的样式作用域。 */
  width: 100%; /* 设置元素宽度。 */
  height: 100%; /* 设置元素高度。 */
  background: #071932; /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.map-state { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  inset: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  gap: 8px; /* 设置子元素之间的间距。 */
  background: rgba(4, 19, 43, 0.72); /* 设置背景样式。 */
  color: #d6f1ff; /* 设置文字颜色。 */
  font-size: 15px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.map-state small { /* 定义当前选择器的样式作用域。 */
  color: #7fb0d8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.property-list { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  min-height: 0; /* 设置元素最小高度。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border: 1px solid rgba(63, 224, 255, 0.18); /* 设置边框样式。 */
  background: rgba(7, 25, 50, 0.56); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.list-head { /* 定义当前选择器的样式作用域。 */
  padding: 10px 12px; /* 设置元素内边距。 */
  color: #eaf6ff; /* 设置文字颜色。 */
  font-weight: 700; /* 设置文字粗细。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.16); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.list-scroll { /* 定义当前选择器的样式作用域。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-height: 0; /* 设置元素最小高度。 */
  overflow-y: auto; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding: 8px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.prop-row { /* 定义当前选择器的样式作用域。 */
  width: 100%; /* 设置元素宽度。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: minmax(0, 1fr) 54px; /* 设置网格列布局。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 8px; /* 设置子元素之间的间距。 */
  border: 1px solid transparent; /* 设置边框样式。 */
  border-bottom-color: rgba(63, 224, 255, 0.08); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: transparent; /* 设置背景样式。 */
  color: #cfe8ff; /* 设置文字颜色。 */
  padding: 8px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.prop-row:hover, /* 设置当前样式属性，控制页面布局或视觉展示。 */
.prop-row.active { /* 定义当前选择器的样式作用域。 */
  border-color: rgba(63, 224, 255, 0.36); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(63, 224, 255, 0.08); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.prop-main { /* 定义当前选择器的样式作用域。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  cursor: pointer; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: block; /* 设置元素布局模式。 */
  text-align: left; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border: 0; /* 设置边框样式。 */
  background: transparent; /* 设置背景样式。 */
  color: inherit; /* 设置文字颜色。 */
  padding: 0; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.prop-title { /* 定义当前选择器的样式作用域。 */
  display: block; /* 设置元素布局模式。 */
  color: #eaf6ff; /* 设置文字颜色。 */
  font-weight: 700; /* 设置文字粗细。 */
  overflow: hidden; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  text-overflow: ellipsis; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  white-space: nowrap; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.prop-meta, /* 设置当前样式属性，控制页面布局或视觉展示。 */
.prop-price { /* 定义当前选择器的样式作用域。 */
  display: block; /* 设置元素布局模式。 */
  margin-top: 4px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #8fb9dc; /* 设置文字颜色。 */
  font-size: 12px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.prop-price b { /* 定义当前选择器的样式作用域。 */
  color: #ffd166; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.detail-btn { /* 定义当前选择器的样式作用域。 */
  width: 54px; /* 设置元素宽度。 */
  height: 30px; /* 设置元素高度。 */
  cursor: pointer; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border: 1px solid rgba(63, 224, 255, 0.42); /* 设置边框样式。 */
  border-radius: 4px; /* 设置圆角半径。 */
  background: rgba(63, 224, 255, 0.12); /* 设置背景样式。 */
  color: #dff8ff; /* 设置文字颜色。 */
  font-size: 12px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */
.detail-btn:hover { /* 定义当前选择器的样式作用域。 */
  border-color: rgba(95, 233, 255, 0.75); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(63, 224, 255, 0.24); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.list-empty { /* 定义当前选择器的样式作用域。 */
  padding-top: 40px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #7fb0d8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.list-scroll::-webkit-scrollbar { /* 定义当前选择器的样式作用域。 */
  width: 5px; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */
.list-scroll::-webkit-scrollbar-thumb { /* 定义当前选择器的样式作用域。 */
  background: rgba(63, 224, 255, 0.3); /* 设置背景样式。 */
  border-radius: 3px; /* 设置圆角半径。 */
} /* 结束当前样式规则块。 */
</style>
