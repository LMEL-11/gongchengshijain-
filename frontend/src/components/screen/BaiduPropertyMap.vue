<!-- 文件功能：在百度地图上展示真实房源点位、列表联动和信息窗详情。 -->
<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  visible: { type: Boolean, default: false }, // 声明visible字段，作为组件配置、请求参数或图表数据的一部分。
  title: { type: String, default: '' }, // 声明title字段，作为组件配置、请求参数或图表数据的一部分。
  address: { type: String, default: '' }, // 声明address字段，作为组件配置、请求参数或图表数据的一部分。
  payload: { type: Object, default: () => ({}) }, // 声明payload字段，作为组件配置、请求参数或图表数据的一部分。
  loading: { type: Boolean, default: false }, // 声明loading字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。
const emit = defineEmits(['close']) // 保存emit相关业务数据，作为后续计算、渲染或请求的输入。
const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。

const mapEl = ref(null) // 创建mapEl响应式状态，用于驱动页面渲染、表单输入或接口参数。
const listScrollEl = ref(null) // 创建listScrollEl响应式状态，用于驱动页面渲染、表单输入或接口参数。
const mapError = ref('') // 创建mapError响应式状态，用于驱动页面渲染、表单输入或接口参数。
const selectedId = ref(null) // 创建selectedId响应式状态，用于驱动页面渲染、表单输入或接口参数。

const ak = import.meta.env.VITE_BAIDU_MAP_AK || '' // 保存ak相关业务数据，作为后续计算、渲染或请求的输入。
// payload.items 已由后端限制为有坐标的房源，组件只负责把点位和列表联动展示。
// 函数功能：规范化地图房源列表输入，补齐展示字段。
const items = computed(() => props.payload?.items || []) // 基于响应式数据派生items，用于保持界面展示与数据状态同步。
// 函数功能：计算地图列表的数量、均价和总价摘要。
const summary = computed(() => props.payload || {}) // 基于响应式数据派生summary，用于保持界面展示与数据状态同步。

let map = null // 保存map相关业务数据，作为后续计算、渲染或请求的输入。
let BMapApi = null // 保存BMapApi相关业务数据，作为后续计算、渲染或请求的输入。
let markers = new Map() // 保存markers相关业务数据，作为后续计算、渲染或请求的输入。
let rowEls = new Map() // 保存rowEls相关业务数据，作为后续计算、渲染或请求的输入。
let scriptPromise = null // 保存scriptPromise相关业务数据，作为后续计算、渲染或请求的输入。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return Number(value || 0).toLocaleString() // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：转义信息窗 HTML 文本，避免特殊字符破坏结构。
function escapeHtml(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return String(value ?? '') // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    .replace(/&/g, '&amp;') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .replace(/</g, '&lt;') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .replace(/>/g, '&gt;') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .replace(/"/g, '&quot;') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .replace(/'/g, '&#39;') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：加载百度地图脚本并复用已创建的加载任务。
function loadBaiduMap() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (window.BMap) return Promise.resolve(window.BMap) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (!ak) return Promise.reject(new Error('请先配置 VITE_BAIDU_MAP_AK')) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (scriptPromise) return scriptPromise // 根据当前状态、接口结果或用户输入选择对应交互路径。

  scriptPromise = new Promise((resolve, reject) => { // 更新scriptPromise对应的页面状态，使界面展示与最新业务数据一致。
    const callback = `__baiduMapReady_${Date.now()}` // 保存callback相关业务数据，作为后续计算、渲染或请求的输入。
    window[callback] = () => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      resolve(window.BMap) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      delete window[callback] // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。

    const script = document.createElement('script') // 保存script相关业务数据，作为后续计算、渲染或请求的输入。
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${encodeURIComponent(ak)}&callback=${callback}` // 更新script.src对应的页面状态，使界面展示与最新业务数据一致。
    script.onerror = () => { // 更新script.onerror对应的页面状态，使界面展示与最新业务数据一致。
      delete window[callback] // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      reject(new Error('百度地图脚本加载失败')) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
    document.head.appendChild(script) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  return scriptPromise // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：生成百度地图信息窗展示 HTML。
function infoHtml(item) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return ` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    <div style="min-width:220px;color:#1f2937;font-size:13px;line-height:1.7"> // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px">${escapeHtml(item.title)}</div> // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      <div>${escapeHtml(item.layout || '暂无户型')} · ${item.area || '暂无'}㎡ · ${escapeHtml(item.district_name || '')}</div> // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      <div>总价：<b style="color:#dc2626">${fmt(item.total_price)}</b> 万元</div> // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      <div>单价：<b style="color:#2563eb">${fmt(item.unit_price)}</b> 元/㎡</div> // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    </div> // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ` // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：打开指定房源的信息窗并同步选中状态。
function openInfo(item, point) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  selectedId.value = item.id // 更新selectedId.value对应的页面状态，使界面展示与最新业务数据一致。
  scrollToListItem(item.id) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  const info = new BMapApi.InfoWindow(infoHtml(item), { // 保存info相关业务数据，作为后续计算、渲染或请求的输入。
    width: 260, // 声明width字段，作为组件配置、请求参数或图表数据的一部分。
    title: '', // 声明title字段，作为组件配置、请求参数或图表数据的一部分。
    enableMessage: false, // 声明enableMessage字段，作为组件配置、请求参数或图表数据的一部分。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  map.openInfoWindow(info, point) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：记录房源列表行 DOM，便于地图点击后滚动定位。
function setRowEl(id, el) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (el) rowEls.set(id, el) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  else rowEls.delete(id) // 处理前面条件未命中的界面或数据场景。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：滚动列表到当前选中的房源行。
async function scrollToListItem(id) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
  const row = rowEls.get(id) // 保存row相关业务数据，作为后续计算、渲染或请求的输入。
  if (!row || !listScrollEl.value) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  row.scrollIntoView({ block: 'center', behavior: 'smooth' }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：清理百度地图覆盖物和信息窗状态。
function clearMap() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (map) map.clearOverlays() // 根据当前状态、接口结果或用户输入选择对应交互路径。
  markers.clear() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：触发百度地图重新计算视口尺寸。
function resizeMap() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!map) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  requestAnimationFrame(() => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    map?.checkResize?.() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  setTimeout(() => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    map?.checkResize?.() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }, 120) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：在缺少坐标时根据城市区域地址定位地图中心。
function centerByAddress() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!map || !props.address) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const geocoder = new BMapApi.Geocoder() // 保存geocoder相关业务数据，作为后续计算、渲染或请求的输入。
  geocoder.getPoint(props.address, (point) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    if (point) map.centerAndZoom(point, 12) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  }) // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据房源点位重建百度地图标记和范围。
function renderMarkers() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!map || !BMapApi) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  clearMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  selectedId.value = null // 更新selectedId.value对应的页面状态，使界面展示与最新业务数据一致。

  // 只绘制经纬度完整的房源；前 30 个点附加单价标签，避免标签过多遮挡地图。
  const points = [] // 保存points相关业务数据，作为后续计算、渲染或请求的输入。
  items.value.forEach((item, index) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    if (!item.lng || !item.lat) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
    const point = new BMapApi.Point(item.lng, item.lat) // 保存point相关业务数据，作为后续计算、渲染或请求的输入。
    points.push(point) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

    const marker = new BMapApi.Marker(point) // 保存marker相关业务数据，作为后续计算、渲染或请求的输入。
    marker.addEventListener('click', () => openInfo(item, point)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    if (index < 30 && item.unit_price) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      const label = new BMapApi.Label(`${fmt(item.unit_price)}元/㎡`, { // 保存label相关业务数据，作为后续计算、渲染或请求的输入。
        offset: new BMapApi.Size(16, -18), // 声明offset字段，作为组件配置、请求参数或图表数据的一部分。
      }) // 完成当前参数、配置或响应式数据结构的组装。
      label.setStyle({ // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
        color: '#0f172a', // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
        border: '1px solid rgba(37, 99, 235, .35)', // 声明border字段，作为组件配置、请求参数或图表数据的一部分。
        borderRadius: '3px', // 声明borderRadius字段，作为组件配置、请求参数或图表数据的一部分。
        padding: '1px 4px', // 声明padding字段，作为组件配置、请求参数或图表数据的一部分。
        background: 'rgba(255, 255, 255, .9)', // 声明background字段，作为组件配置、请求参数或图表数据的一部分。
        fontSize: '11px', // 声明fontSize字段，作为组件配置、请求参数或图表数据的一部分。
      }) // 完成当前参数、配置或响应式数据结构的组装。
      marker.setLabel(label) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
    map.addOverlay(marker) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    markers.set(item.id, { marker, point, item }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }) // 完成当前参数、配置或响应式数据结构的组装。

  // 视野优先覆盖全部真实点位；没有点位时回退到后端中心点或地址地理编码。
  if (points.length > 1) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    map.setViewport(points, { margins: [50, 50, 50, 50] }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } else if (points.length === 1) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    map.centerAndZoom(points[0], 14) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } else if (summary.value?.center?.lng && summary.value?.center?.lat) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    map.centerAndZoom(new BMapApi.Point(summary.value.center.lng, summary.value.center.lat), 12) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    centerByAddress() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  resizeMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：初始化百度地图实例并渲染当前房源标记。
async function initMap() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!props.visible || !mapEl.value) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  mapError.value = '' // 更新mapError.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    BMapApi = await loadBaiduMap() // 等待异步接口或资源加载完成，再继续更新页面状态。
    if (!mapEl.value) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
    if (!map) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      map = new BMapApi.Map(mapEl.value, { enableMapClick: false }) // 更新map对应的页面状态，使界面展示与最新业务数据一致。
      map.enableScrollWheelZoom(true) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      map.addControl(new BMapApi.NavigationControl()) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      map.addControl(new BMapApi.ScaleControl()) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
    resizeMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    renderMarkers() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } catch (err) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    mapError.value = err.message || '百度地图加载失败' // 更新mapError.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：从列表聚焦房源并打开对应地图信息窗。
function focusItem(item) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const target = markers.get(item.id) // 保存target相关业务数据，作为后续计算、渲染或请求的输入。
  if (!target || !map) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  map.panTo(target.point) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  openInfo(target.item, target.point) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：跳转到房源详情页面。
function openDetail(item) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!item?.id) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  router.push({ name: 'property-detail', params: { id: item.id } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => props.visible, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  async (visible) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    if (visible) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
      initMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      selectedId.value = null // 更新selectedId.value对应的页面状态，使界面展示与最新业务数据一致。
    } // 完成当前参数、配置或响应式数据结构的组装。
  }, // 完成当前参数、配置或响应式数据结构的组装。
) // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => props.payload, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  async () => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    // 同一个弹窗内切换行政区或刷新 payload 时，只重绘点位，不重新创建地图实例。
    if (!props.visible) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
    await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
    if (map) renderMarkers() // 根据当前状态、接口结果或用户输入选择对应交互路径。
    else initMap() // 处理前面条件未命中的界面或数据场景。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { deep: true }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

onBeforeUnmount(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  clearMap() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  map = null // 更新map对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。
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
.baidu-layer { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  inset: 86px 24px 22px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  z-index: 20; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  background: rgba(1, 10, 25, 0.72); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  backdrop-filter: blur(4px); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-panel { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: rgba(4, 19, 43, 0.96); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  box-shadow: 0 0 40px rgba(63, 224, 255, 0.2); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  padding: 14px 18px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #eaf6ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 20px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  letter-spacing: 1px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-sub { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-top: 5px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #7fb0d8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.close-btn { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  cursor: pointer; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 4px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: rgba(63, 224, 255, 0.1); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #d6f1ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 6px 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.close-btn:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: rgba(63, 224, 255, 0.22); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-summary { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: repeat(3, 1fr); /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  padding: 12px 18px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-summary div { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  border: 1px solid rgba(63, 224, 255, 0.15); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: rgba(63, 224, 255, 0.06); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 8px 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-summary b { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-right: 8px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #5fe9ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 22px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-variant-numeric: tabular-nums; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-summary span { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #9fc4e4; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-body { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: minmax(0, 1fr) 360px; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  padding: 0 18px 18px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.map-box { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: relative; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  overflow: hidden; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border: 1px solid rgba(63, 224, 255, 0.22); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.baidu-map { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  background: #071932; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.map-state { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  inset: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  gap: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  background: rgba(4, 19, 43, 0.72); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #d6f1ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.map-state small { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #7fb0d8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.property-list { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border: 1px solid rgba(63, 224, 255, 0.18); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: rgba(7, 25, 50, 0.56); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.list-head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  padding: 10px 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  color: #eaf6ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.16); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.list-scroll { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  overflow-y: auto; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  padding: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-row { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: minmax(0, 1fr) 54px; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border: 1px solid transparent; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-bottom-color: rgba(63, 224, 255, 0.08); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: transparent; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #cfe8ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-row:hover, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
.prop-row.active { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  border-color: rgba(63, 224, 255, 0.36); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(63, 224, 255, 0.08); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-main { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  cursor: pointer; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: block; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  text-align: left; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  border: 0; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: transparent; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: inherit; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: block; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  color: #eaf6ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  overflow: hidden; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  text-overflow: ellipsis; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  white-space: nowrap; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-meta, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
.prop-price { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: block; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  margin-top: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #8fb9dc; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-price b { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #ffd166; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.detail-btn { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 54px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 30px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  cursor: pointer; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border: 1px solid rgba(63, 224, 255, 0.42); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 4px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: rgba(63, 224, 255, 0.12); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #dff8ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.detail-btn:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  border-color: rgba(95, 233, 255, 0.75); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(63, 224, 255, 0.24); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.list-empty { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  padding-top: 40px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #7fb0d8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.list-scroll::-webkit-scrollbar { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 5px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.list-scroll::-webkit-scrollbar-thumb { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: rgba(63, 224, 255, 0.3); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 3px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
