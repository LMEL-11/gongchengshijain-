<!-- 文件功能：在百度地图上展示真实房源点位、列表联动和信息窗详情。 -->
<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue' // 导入本行所需的依赖。
import { useRouter } from 'vue-router' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  visible: { type: Boolean, default: false }, // 配置当前对象字段。
  title: { type: String, default: '' }, // 配置当前对象字段。
  address: { type: String, default: '' }, // 配置当前对象字段。
  payload: { type: Object, default: () => ({}) }, // 配置当前对象字段。
  loading: { type: Boolean, default: false }, // 配置当前对象字段。
}) // 执行本行前端逻辑。
const emit = defineEmits(['close']) // 声明并初始化当前变量。
const router = useRouter() // 声明并初始化当前变量。

const mapEl = ref(null) // 声明并初始化当前变量。
const listScrollEl = ref(null) // 声明并初始化当前变量。
const mapError = ref('') // 声明并初始化当前变量。
const selectedId = ref(null) // 声明并初始化当前变量。

const ak = import.meta.env.VITE_BAIDU_MAP_AK || '' // 声明并初始化当前变量。
// 函数功能：规范化地图房源列表输入，补齐展示字段。
const items = computed(() => props.payload?.items || []) // 声明并初始化当前变量。
// 函数功能：计算地图列表的数量、均价和总价摘要。
const summary = computed(() => props.payload || {}) // 声明并初始化当前变量。

let map = null // 声明并初始化当前变量。
let BMapApi = null // 声明并初始化当前变量。
let markers = new Map() // 声明并初始化当前变量。
let rowEls = new Map() // 声明并初始化当前变量。
let scriptPromise = null // 声明并初始化当前变量。

// 函数功能：格式化数值展示，处理空值和单位。
function fmt(value) { // 声明当前函数入口。
  return Number(value || 0).toLocaleString() // 返回当前表达式结果。
} // 结束当前代码块或数据结构。

// 函数功能：转义信息窗 HTML 文本，避免特殊字符破坏结构。
function escapeHtml(value) { // 声明当前函数入口。
  return String(value ?? '') // 返回当前表达式结果。
    .replace(/&/g, '&amp;') // 执行本行前端逻辑。
    .replace(/</g, '&lt;') // 执行本行前端逻辑。
    .replace(/>/g, '&gt;') // 执行本行前端逻辑。
    .replace(/"/g, '&quot;') // 执行本行前端逻辑。
    .replace(/'/g, '&#39;') // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：加载百度地图脚本并复用已创建的加载任务。
function loadBaiduMap() { // 声明当前函数入口。
  if (window.BMap) return Promise.resolve(window.BMap) // 根据条件判断是否执行分支。
  if (!ak) return Promise.reject(new Error('请先配置 VITE_BAIDU_MAP_AK')) // 根据条件判断是否执行分支。
  if (scriptPromise) return scriptPromise // 根据条件判断是否执行分支。

  scriptPromise = new Promise((resolve, reject) => { // 执行本行前端逻辑。
    const callback = `__baiduMapReady_${Date.now()}` // 声明并初始化当前变量。
    window[callback] = () => { // 执行本行前端逻辑。
      resolve(window.BMap) // 执行本行前端逻辑。
      delete window[callback] // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。

    const script = document.createElement('script') // 声明并初始化当前变量。
    script.src = `https://api.map.baidu.com/api?v=2.0&ak=${encodeURIComponent(ak)}&callback=${callback}` // 赋值或更新当前变量/状态。
    script.onerror = () => { // 执行本行前端逻辑。
      delete window[callback] // 执行本行前端逻辑。
      reject(new Error('百度地图脚本加载失败')) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
    document.head.appendChild(script) // 执行本行前端逻辑。
  }) // 执行本行前端逻辑。
  return scriptPromise // 返回当前表达式结果。
} // 结束当前代码块或数据结构。

// 函数功能：生成百度地图信息窗展示 HTML。
function infoHtml(item) { // 声明当前函数入口。
  return ` // 返回当前表达式结果。
    <div style="min-width:220px;color:#1f2937;font-size:13px;line-height:1.7">
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px">${escapeHtml(item.title)}</div>
      <div>${escapeHtml(item.layout || '暂无户型')} · ${item.area || '暂无'}㎡ · ${escapeHtml(item.district_name || '')}</div>
      <div>总价：<b style="color:#dc2626">${fmt(item.total_price)}</b> 万元</div>
      <div>单价：<b style="color:#2563eb">${fmt(item.unit_price)}</b> 元/㎡</div>
    </div>
  `
} // 结束当前代码块或数据结构。

// 函数功能：打开指定房源的信息窗并同步选中状态。
function openInfo(item, point) { // 声明当前函数入口。
  selectedId.value = item.id // 赋值或更新当前变量/状态。
  scrollToListItem(item.id) // 执行本行前端逻辑。
  const info = new BMapApi.InfoWindow(infoHtml(item), { // 声明并初始化当前变量。
    width: 260, // 配置当前对象字段。
    title: '', // 配置当前对象字段。
    enableMessage: false, // 配置当前对象字段。
  }) // 执行本行前端逻辑。
  map.openInfoWindow(info, point) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：记录房源列表行 DOM，便于地图点击后滚动定位。
function setRowEl(id, el) { // 声明当前函数入口。
  if (el) rowEls.set(id, el) // 根据条件判断是否执行分支。
  else rowEls.delete(id) // 处理条件不满足时的分支。
} // 结束当前代码块或数据结构。

// 函数功能：滚动列表到当前选中的房源行。
async function scrollToListItem(id) { // 声明当前函数入口。
  await nextTick() // 等待异步操作完成。
  const row = rowEls.get(id) // 声明并初始化当前变量。
  if (!row || !listScrollEl.value) return // 根据条件判断是否执行分支。
  row.scrollIntoView({ block: 'center', behavior: 'smooth' }) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：清理百度地图覆盖物和信息窗状态。
function clearMap() { // 声明当前函数入口。
  if (map) map.clearOverlays() // 根据条件判断是否执行分支。
  markers.clear() // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：触发百度地图重新计算视口尺寸。
function resizeMap() { // 声明当前函数入口。
  if (!map) return // 根据条件判断是否执行分支。
  requestAnimationFrame(() => { // 执行本行前端逻辑。
    map?.checkResize?.() // 执行本行前端逻辑。
  }) // 执行本行前端逻辑。
  setTimeout(() => { // 执行本行前端逻辑。
    map?.checkResize?.() // 执行本行前端逻辑。
  }, 120) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：在缺少坐标时根据城市区域地址定位地图中心。
function centerByAddress() { // 声明当前函数入口。
  if (!map || !props.address) return // 根据条件判断是否执行分支。
  const geocoder = new BMapApi.Geocoder() // 声明并初始化当前变量。
  geocoder.getPoint(props.address, (point) => { // 执行本行前端逻辑。
    if (point) map.centerAndZoom(point, 12) // 根据条件判断是否执行分支。
  }) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：根据房源点位重建百度地图标记和范围。
function renderMarkers() { // 声明当前函数入口。
  if (!map || !BMapApi) return // 根据条件判断是否执行分支。
  clearMap() // 执行本行前端逻辑。
  selectedId.value = null // 赋值或更新当前变量/状态。

  const points = [] // 声明并初始化当前变量。
  items.value.forEach((item, index) => { // 执行本行前端逻辑。
    if (!item.lng || !item.lat) return // 根据条件判断是否执行分支。
    const point = new BMapApi.Point(item.lng, item.lat) // 声明并初始化当前变量。
    points.push(point) // 执行本行前端逻辑。

    const marker = new BMapApi.Marker(point) // 声明并初始化当前变量。
    marker.addEventListener('click', () => openInfo(item, point)) // 执行本行前端逻辑。
    if (index < 30 && item.unit_price) { // 根据条件判断是否执行分支。
      const label = new BMapApi.Label(`${fmt(item.unit_price)}元/㎡`, { // 声明并初始化当前变量。
        offset: new BMapApi.Size(16, -18), // 配置当前对象字段。
      }) // 执行本行前端逻辑。
      label.setStyle({ // 执行本行前端逻辑。
        color: '#0f172a', // 配置当前对象字段。
        border: '1px solid rgba(37, 99, 235, .35)', // 配置当前对象字段。
        borderRadius: '3px', // 配置当前对象字段。
        padding: '1px 4px', // 配置当前对象字段。
        background: 'rgba(255, 255, 255, .9)', // 配置当前对象字段。
        fontSize: '11px', // 配置当前对象字段。
      }) // 执行本行前端逻辑。
      marker.setLabel(label) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
    map.addOverlay(marker) // 执行本行前端逻辑。
    markers.set(item.id, { marker, point, item }) // 执行本行前端逻辑。
  }) // 执行本行前端逻辑。

  if (points.length > 1) { // 根据条件判断是否执行分支。
    map.setViewport(points, { margins: [50, 50, 50, 50] }) // 执行本行前端逻辑。
  } else if (points.length === 1) { // 执行本行前端逻辑。
    map.centerAndZoom(points[0], 14) // 执行本行前端逻辑。
  } else if (summary.value?.center?.lng && summary.value?.center?.lat) { // 执行本行前端逻辑。
    map.centerAndZoom(new BMapApi.Point(summary.value.center.lng, summary.value.center.lat), 12) // 执行本行前端逻辑。
  } else { // 执行本行前端逻辑。
    centerByAddress() // 执行本行前端逻辑。
  } // 结束当前代码块或数据结构。
  resizeMap() // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：初始化百度地图实例并渲染当前房源标记。
async function initMap() { // 声明当前函数入口。
  if (!props.visible || !mapEl.value) return // 根据条件判断是否执行分支。
  mapError.value = '' // 赋值或更新当前变量/状态。
  try { // 开始执行可能失败的逻辑。
    BMapApi = await loadBaiduMap() // 赋值或更新当前变量/状态。
    if (!mapEl.value) return // 根据条件判断是否执行分支。
    if (!map) { // 根据条件判断是否执行分支。
      map = new BMapApi.Map(mapEl.value, { enableMapClick: false }) // 赋值或更新当前变量/状态。
      map.enableScrollWheelZoom(true) // 执行本行前端逻辑。
      map.addControl(new BMapApi.NavigationControl()) // 执行本行前端逻辑。
      map.addControl(new BMapApi.ScaleControl()) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
    resizeMap() // 执行本行前端逻辑。
    renderMarkers() // 执行本行前端逻辑。
  } catch (err) { // 执行本行前端逻辑。
    mapError.value = err.message || '百度地图加载失败' // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// 函数功能：从列表聚焦房源并打开对应地图信息窗。
function focusItem(item) { // 声明当前函数入口。
  const target = markers.get(item.id) // 声明并初始化当前变量。
  if (!target || !map) return // 根据条件判断是否执行分支。
  map.panTo(target.point) // 执行本行前端逻辑。
  openInfo(target.item, target.point) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：跳转到房源详情页面。
function openDetail(item) { // 声明当前函数入口。
  if (!item?.id) return // 根据条件判断是否执行分支。
  router.push({ name: 'property-detail', params: { id: item.id } }) // 执行路由跳转或路由操作。
} // 结束当前代码块或数据结构。

watch( // 监听响应式数据变化。
  () => props.visible, // 继续声明当前列表项或参数项。
  async (visible) => { // 执行本行前端逻辑。
    if (visible) { // 根据条件判断是否执行分支。
      await nextTick() // 等待异步操作完成。
      initMap() // 执行本行前端逻辑。
    } else { // 执行本行前端逻辑。
      selectedId.value = null // 赋值或更新当前变量/状态。
    } // 结束当前代码块或数据结构。
  }, // 结束当前代码块或数据结构。
) // 结束当前代码块或数据结构。

watch( // 监听响应式数据变化。
  () => props.payload, // 继续声明当前列表项或参数项。
  async () => { // 执行本行前端逻辑。
    if (!props.visible) return // 根据条件判断是否执行分支。
    await nextTick() // 等待异步操作完成。
    if (map) renderMarkers() // 根据条件判断是否执行分支。
    else initMap() // 处理条件不满足时的分支。
  }, // 结束当前代码块或数据结构。
  { deep: true }, // 配置当前对象字段。
) // 结束当前代码块或数据结构。

onBeforeUnmount(() => { // 注册 Vue 生命周期回调。
  clearMap() // 执行本行前端逻辑。
  map = null // 赋值或更新当前变量/状态。
}) // 执行本行前端逻辑。
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
.baidu-layer { /* 开始当前样式规则块。 */
  position: absolute; /* 设置当前样式属性。 */
  inset: 86px 24px 22px; /* 设置当前样式属性。 */
  z-index: 20; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  background: rgba(1, 10, 25, 0.72); /* 设置当前样式属性。 */
  backdrop-filter: blur(4px); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-panel { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  flex: 1; /* 设置当前样式属性。 */
  min-width: 0; /* 设置当前样式属性。 */
  flex-direction: column; /* 设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 设置当前样式属性。 */
  background: rgba(4, 19, 43, 0.96); /* 设置当前样式属性。 */
  box-shadow: 0 0 40px rgba(63, 224, 255, 0.2); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-head { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: space-between; /* 设置当前样式属性。 */
  padding: 14px 18px; /* 设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-title { /* 开始当前样式规则块。 */
  color: #eaf6ff; /* 设置当前样式属性。 */
  font-size: 20px; /* 设置当前样式属性。 */
  font-weight: 800; /* 设置当前样式属性。 */
  letter-spacing: 1px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-sub { /* 开始当前样式规则块。 */
  margin-top: 5px; /* 设置当前样式属性。 */
  color: #7fb0d8; /* 设置当前样式属性。 */
  font-size: 13px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.close-btn { /* 开始当前样式规则块。 */
  cursor: pointer; /* 设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.45); /* 设置当前样式属性。 */
  border-radius: 4px; /* 设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.1); /* 设置当前样式属性。 */
  color: #d6f1ff; /* 设置当前样式属性。 */
  padding: 6px 16px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.close-btn:hover { /* 开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.22); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-summary { /* 开始当前样式规则块。 */
  display: grid; /* 设置当前样式属性。 */
  grid-template-columns: repeat(3, 1fr); /* 设置当前样式属性。 */
  gap: 10px; /* 设置当前样式属性。 */
  padding: 12px 18px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-summary div { /* 开始当前样式规则块。 */
  border: 1px solid rgba(63, 224, 255, 0.15); /* 设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.06); /* 设置当前样式属性。 */
  padding: 8px 12px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-summary b { /* 开始当前样式规则块。 */
  margin-right: 8px; /* 设置当前样式属性。 */
  color: #5fe9ff; /* 设置当前样式属性。 */
  font-size: 22px; /* 设置当前样式属性。 */
  font-variant-numeric: tabular-nums; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-summary span { /* 开始当前样式规则块。 */
  color: #9fc4e4; /* 设置当前样式属性。 */
  font-size: 13px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-body { /* 开始当前样式规则块。 */
  display: grid; /* 设置当前样式属性。 */
  grid-template-columns: minmax(0, 1fr) 360px; /* 设置当前样式属性。 */
  gap: 14px; /* 设置当前样式属性。 */
  min-height: 0; /* 设置当前样式属性。 */
  flex: 1; /* 设置当前样式属性。 */
  padding: 0 18px 18px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.map-box { /* 开始当前样式规则块。 */
  position: relative; /* 设置当前样式属性。 */
  min-width: 0; /* 设置当前样式属性。 */
  min-height: 0; /* 设置当前样式属性。 */
  overflow: hidden; /* 设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.22); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.baidu-map { /* 开始当前样式规则块。 */
  width: 100%; /* 设置当前样式属性。 */
  height: 100%; /* 设置当前样式属性。 */
  background: #071932; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.map-state { /* 开始当前样式规则块。 */
  position: absolute; /* 设置当前样式属性。 */
  inset: 0; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: center; /* 设置当前样式属性。 */
  flex-direction: column; /* 设置当前样式属性。 */
  gap: 8px; /* 设置当前样式属性。 */
  background: rgba(4, 19, 43, 0.72); /* 设置当前样式属性。 */
  color: #d6f1ff; /* 设置当前样式属性。 */
  font-size: 15px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.map-state small { /* 开始当前样式规则块。 */
  color: #7fb0d8; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.property-list { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  min-height: 0; /* 设置当前样式属性。 */
  flex-direction: column; /* 设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.18); /* 设置当前样式属性。 */
  background: rgba(7, 25, 50, 0.56); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.list-head { /* 开始当前样式规则块。 */
  padding: 10px 12px; /* 设置当前样式属性。 */
  color: #eaf6ff; /* 设置当前样式属性。 */
  font-weight: 700; /* 设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.16); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.list-scroll { /* 开始当前样式规则块。 */
  flex: 1; /* 设置当前样式属性。 */
  min-height: 0; /* 设置当前样式属性。 */
  overflow-y: auto; /* 设置当前样式属性。 */
  padding: 8px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.prop-row { /* 开始当前样式规则块。 */
  width: 100%; /* 设置当前样式属性。 */
  display: grid; /* 设置当前样式属性。 */
  grid-template-columns: minmax(0, 1fr) 54px; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 8px; /* 设置当前样式属性。 */
  border: 1px solid transparent; /* 设置当前样式属性。 */
  border-bottom-color: rgba(63, 224, 255, 0.08); /* 设置当前样式属性。 */
  background: transparent; /* 设置当前样式属性。 */
  color: #cfe8ff; /* 设置当前样式属性。 */
  padding: 8px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.prop-row:hover, /* 设置当前样式属性。 */
.prop-row.active { /* 开始当前样式规则块。 */
  border-color: rgba(63, 224, 255, 0.36); /* 设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.08); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.prop-main { /* 开始当前样式规则块。 */
  min-width: 0; /* 设置当前样式属性。 */
  cursor: pointer; /* 设置当前样式属性。 */
  display: block; /* 设置当前样式属性。 */
  text-align: left; /* 设置当前样式属性。 */
  border: 0; /* 设置当前样式属性。 */
  background: transparent; /* 设置当前样式属性。 */
  color: inherit; /* 设置当前样式属性。 */
  padding: 0; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.prop-title { /* 开始当前样式规则块。 */
  display: block; /* 设置当前样式属性。 */
  color: #eaf6ff; /* 设置当前样式属性。 */
  font-weight: 700; /* 设置当前样式属性。 */
  overflow: hidden; /* 设置当前样式属性。 */
  text-overflow: ellipsis; /* 设置当前样式属性。 */
  white-space: nowrap; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.prop-meta, /* 声明当前样式规则。 */
.prop-price { /* 开始当前样式规则块。 */
  display: block; /* 设置当前样式属性。 */
  margin-top: 4px; /* 设置当前样式属性。 */
  color: #8fb9dc; /* 设置当前样式属性。 */
  font-size: 12px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.prop-price b { /* 开始当前样式规则块。 */
  color: #ffd166; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.detail-btn { /* 开始当前样式规则块。 */
  width: 54px; /* 设置当前样式属性。 */
  height: 30px; /* 设置当前样式属性。 */
  cursor: pointer; /* 设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.42); /* 设置当前样式属性。 */
  border-radius: 4px; /* 设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.12); /* 设置当前样式属性。 */
  color: #dff8ff; /* 设置当前样式属性。 */
  font-size: 12px; /* 设置当前样式属性。 */
  font-weight: 700; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.detail-btn:hover { /* 开始当前样式规则块。 */
  border-color: rgba(95, 233, 255, 0.75); /* 设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.24); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.list-empty { /* 开始当前样式规则块。 */
  padding-top: 40px; /* 设置当前样式属性。 */
  text-align: center; /* 设置当前样式属性。 */
  color: #7fb0d8; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.list-scroll::-webkit-scrollbar { /* 开始当前样式规则块。 */
  width: 5px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.list-scroll::-webkit-scrollbar-thumb { /* 开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.3); /* 设置当前样式属性。 */
  border-radius: 3px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
</style>
