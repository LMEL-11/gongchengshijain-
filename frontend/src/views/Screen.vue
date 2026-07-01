<!-- 文件功能：实现全国二手房数据大屏，联动地图、排行、表格和统计面板。 -->
<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue' // 导入 { computed, onBeforeUnmount, onMounted, ref }，供当前前端模块渲染或交互逻辑使用。

import { // 导入 {，供当前前端模块渲染或交互逻辑使用。
  getRealAreaProperties, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  getRealCities, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  getRealDistricts, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  getRealProvinces, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  getRealSummary, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} from '@/api' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
import BaiduPropertyMap from '@/components/screen/BaiduPropertyMap.vue' // 导入 BaiduPropertyMap，供当前前端模块渲染或交互逻辑使用。
import Donut from '@/components/screen/Donut.vue' // 导入 Donut，供当前前端模块渲染或交互逻辑使用。
import GeoMap3D from '@/components/screen/GeoMap3D.vue' // 导入 GeoMap3D，供当前前端模块渲染或交互逻辑使用。
import RankBar from '@/components/screen/RankBar.vue' // 导入 RankBar，供当前前端模块渲染或交互逻辑使用。
import ScreenPanel from '@/components/screen/ScreenPanel.vue' // 导入 ScreenPanel，供当前前端模块渲染或交互逻辑使用。
import { useAutoFit } from '@/composables/useAutoFit' // 导入 { useAutoFit }，供当前前端模块渲染或交互逻辑使用。
import { normalizeName } from '@/utils/geo' // 导入 { normalizeName }，供当前前端模块渲染或交互逻辑使用。

const MUNICIPALITIES = new Set(['北京', '北京市', '上海', '上海市', '天津', '天津市', '重庆', '重庆市']) // 创建 MUNICIPALITIES，用于保存页面状态、计算结果或接口参数。
const { scale, designW, designH } = useAutoFit() // 创建 { scale, designW, designH }，用于保存页面状态、计算结果或接口参数。

const mapRef = ref(null) // 创建 mapRef，用于保存页面状态、计算结果或接口参数。
const summary = ref({}) // 创建 summary，用于保存页面状态、计算结果或接口参数。
const rankData = ref([]) // 创建 rankData，用于保存页面状态、计算结果或接口参数。
const path = ref([{ adcode: 100000, name: '全国' }]) // 创建 path，用于保存页面状态、计算结果或接口参数。
const clock = ref('') // 创建 clock，用于保存页面状态、计算结果或接口参数。
const baiduVisible = ref(false) // 创建 baiduVisible，用于保存页面状态、计算结果或接口参数。
const baiduLoading = ref(false) // 创建 baiduLoading，用于保存页面状态、计算结果或接口参数。
const baiduPayload = ref({}) // 创建 baiduPayload，用于保存页面状态、计算结果或接口参数。
const baiduTitle = ref('') // 创建 baiduTitle，用于保存页面状态、计算结果或接口参数。
const baiduAddress = ref('') // 创建 baiduAddress，用于保存页面状态、计算结果或接口参数。

// path 保存地图钻取路径：全国 -> 省/直辖市 -> 城市；其长度决定当前接口口径。
// 函数功能：计算当前大屏地图层级。
const level = computed(() => path.value.length) // 创建 level，用于保存页面状态、计算结果或接口参数。
// 函数功能：判断当前是否处于直辖市层级。
const isMunicipalityLevel = computed( // 创建 isMunicipalityLevel，用于保存页面状态、计算结果或接口参数。
  () => level.value === 2 && MUNICIPALITIES.has(path.value[1]?.name), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。
// 函数功能：判断当前是否展示区县级地图。
const isDistrictMapLevel = computed(() => level.value >= 3 || isMunicipalityLevel.value) // 创建 isDistrictMapLevel，用于保存页面状态、计算结果或接口参数。
// 函数功能：根据设计稿尺寸计算大屏缩放样式。
const stageStyle = computed(() => ({ // 创建 stageStyle，用于保存页面状态、计算结果或接口参数。
  width: designW + 'px', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  height: designH + 'px', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  transform: `translate(-50%, -50%) scale(${scale.value})`, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
})) // 结束当前函数、对象、数组或组件配置块。

// 地图着色数据：全国按省、省级按市的「真实房源数」；市级（商圈）无地图边界 -> 自然不匹配走中性色
// 函数功能：将当前层级统计数据整理为地图查找表。
const dataMap = computed(() => { // 创建 dataMap，用于保存页面状态、计算结果或接口参数。
  const m = {} // 创建 m，用于保存页面状态、计算结果或接口参数。
  for (const r of rankData.value) { // 遍历当前数据集合，逐项生成页面需要的数据。
    m[r.name] = r.count // 设置 m[r.name 的值，作为后续渲染、计算或请求的输入。
    m[normalizeName(r.name)] = r.count // 设置 m[normalizeName(r.name 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
  return m // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：计算当前排行面板标题。
const rankTitle = computed(() => { // 创建 rankTitle，用于保存页面状态、计算结果或接口参数。
  if (level.value === 1) return '省份房源数 TOP' // 根据当前页面状态或接口结果决定是否进入该分支。
  if (isMunicipalityLevel.value) return `${path.value[1]?.name} · 行政区房源数 TOP` // 根据当前页面状态或接口结果决定是否进入该分支。
  if (level.value === 2) return `${path.value[1]?.name} · 城市房源数 TOP` // 根据当前页面状态或接口结果决定是否进入该分支。
  return `${path.value[2]?.name} · 行政区房源数 TOP` // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。
// 函数功能：计算当前价格面板标题。
const priceTitle = computed( // 创建 priceTitle，用于保存页面状态、计算结果或接口参数。
  () => // 设置  的值，作为后续渲染、计算或请求的输入。
    (level.value === 1 ? '省份' : level.value === 2 && !isMunicipalityLevel.value ? '城市' : '行政区') + // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    '均价 TOP（元/㎡）', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：整理户型分布数据。
const roomItems = computed(() => summary.value.room_dist || []) // 创建 roomItems，用于保存页面状态、计算结果或接口参数。
// 函数功能：整理房源数量排行条形图数据。
const countBars = computed(() => rankData.value.map((r) => ({ name: r.name, value: r.count }))) // 创建 countBars，用于保存页面状态、计算结果或接口参数。
// 函数功能：整理均价排行条形图数据。
const priceBars = computed(() => // 创建 priceBars，用于保存页面状态、计算结果或接口参数。
  [...rankData.value] // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    .sort((a, b) => (b.avg_price || 0) - (a.avg_price || 0)) // 设置 .sort((a, b 的值，作为后续渲染、计算或请求的输入。
    .map((r) => ({ name: r.name, value: r.avg_price || 0 })), // 设置 .map((r 的值，作为后续渲染、计算或请求的输入。
) // 结束当前函数、对象、数组或组件配置块。
// 函数功能：整理城市 Top 列表数据。
const cityTop = computed(() => summary.value.top_cities || []) // 创建 cityTop，用于保存页面状态、计算结果或接口参数。
// 函数功能：整理大屏表格展示行数据。
const tableRows = computed(() => rankData.value.slice(0, 14)) // 创建 tableRows，用于保存页面状态、计算结果或接口参数。
// 函数功能：计算地图操作提示文案。
const mapHint = computed(() => // 创建 mapHint，用于保存页面状态、计算结果或接口参数。
  isDistrictMapLevel.value // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ? '拖拽旋转 · 滚轮缩放 · 点击区县查看百度地图房源点' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    : '拖拽旋转 · 滚轮缩放 · 点击高亮区域下钻（省 → 市）', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。
// 函数功能：计算地图叶子节点点击按钮文案。
const leafClickLabel = computed(() => (isDistrictMapLevel.value ? '查看百度地图房源点' : '')) // 创建 leafClickLabel，用于保存页面状态、计算结果或接口参数。

// 函数功能：处理大屏数据层级切换。
async function onLevelChange(ctx) { // 定义 onLevelChange 函数，处理页面交互、数据加载或状态同步。
  path.value = ctx.path // 更新 path.value 响应式状态，让页面展示与最新数据保持一致。
  // 地图每下钻一层，排行数据也切换到同一层级，保证地图颜色和侧栏排行同源。
  if (ctx.path.length === 1) { // 根据当前页面状态或接口结果决定是否进入该分支。
    rankData.value = await getRealProvinces() // 更新 rankData.value 响应式状态，让页面展示与最新数据保持一致。
  } else if (ctx.path.length === 2) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    rankData.value = await getRealCities(ctx.path[1].name) // 更新 rankData.value 响应式状态，让页面展示与最新数据保持一致。
  } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // 市级下钻：按行政区汇总该市商圈房源数，匹配城市地图边界
    rankData.value = await getRealDistricts(ctx.path[2].name) // 更新 rankData.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据面包屑切换到对应地图层级。
function crumbTo(i) { // 定义 crumbTo 函数，处理页面交互、数据加载或状态同步。
  if (i < path.value.length - 1) mapRef.value?.goToLevel(i) // 根据当前页面状态或接口结果决定是否进入该分支。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理地图区域点击并触发下钻或房源加载。
async function onRegionClick(region) { // 定义 onRegionClick 函数，处理页面交互、数据加载或状态同步。
  if (!isDistrictMapLevel.value || !region?.name) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const cityName = isMunicipalityLevel.value ? path.value[1]?.name : path.value[2]?.name // 创建 cityName，用于保存页面状态、计算结果或接口参数。
  const areaPath = path.value.slice(1).map((item) => item.name) // 创建 areaPath，用于保存页面状态、计算结果或接口参数。
  // 点击行政区后先给弹窗一个空结构，随后用真实房源点位数据替换，避免界面闪烁。
  baiduTitle.value = `${region.name} · 百度地图房源分布` // 更新 baiduTitle.value 响应式状态，让页面展示与最新数据保持一致。
  baiduAddress.value = `${areaPath.join('')}${region.name}` // 更新 baiduAddress.value 响应式状态，让页面展示与最新数据保持一致。
  baiduVisible.value = true // 更新 baiduVisible.value 响应式状态，让页面展示与最新数据保持一致。
  baiduLoading.value = true // 更新 baiduLoading.value 响应式状态，让页面展示与最新数据保持一致。
  baiduPayload.value = { // 更新 baiduPayload.value 响应式状态，让页面展示与最新数据保持一致。
    area: region.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    property_count: region.value || 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    coordinate_count: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    returned_count: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    avg_price: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    items: [], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // 后端按“城市 + 行政区”反查商圈房源，并只返回有坐标的点位用于百度地图。
    baiduPayload.value = await getRealAreaProperties({ // 更新 baiduPayload.value 响应式状态，让页面展示与最新数据保持一致。
      city: cityName, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      area: region.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      limit: 800, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }) // 结束当前函数、对象、数组或组件配置块。
  } catch (e) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    console.error('加载百度地图房源点失败', e) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    baiduLoading.value = false // 更新 baiduLoading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString() // 创建 fmt，用于保存页面状态、计算结果或接口参数。

let timer // 创建 timer，用于保存页面状态、计算结果或接口参数。
// 函数功能：更新时间文本。
function tick() { // 定义 tick 函数，处理页面交互、数据加载或状态同步。
  const d = new Date() // 创建 d，用于保存页面状态、计算结果或接口参数。
  // 函数功能：生成百分比展示文本。
  const p = (n) => String(n).padStart(2, '0') // 创建 p，用于保存页面状态、计算结果或接口参数。
  clock.value = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}` // 更新 clock.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(async () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  tick() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  timer = setInterval(tick, 1000) // 设置 timer 的值，作为后续渲染、计算或请求的输入。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // 首屏只加载全国概览；省/市排行由 GeoMap3D 初始化后通过 levelchange 拉取。
    summary.value = await getRealSummary() // 更新 summary.value 响应式状态，让页面展示与最新数据保持一致。
  } catch (e) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    console.error('加载概览失败', e) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。
onBeforeUnmount(() => clearInterval(timer)) // 设置 onBeforeUnmount 的值，作为后续渲染、计算或请求的输入。
</script>

<template>
  <div class="screen-root">
    <div class="stage" :style="stageStyle">
      <!-- 顶栏 -->
      <header class="s-header">
        <div class="s-title">全国二手房数据可视化平台</div>
        <div class="s-meta">
          <span class="s-clock">{{ clock }}</span>
          <nav class="s-nav">
            <RouterLink to="/dashboard">房源总览</RouterLink>
            <RouterLink to="/explore">房源探索</RouterLink>
            <RouterLink to="/analysis">数据分析</RouterLink>
          </nav>
        </div>
      </header>

      <div class="s-body">
        <!-- 左列 -->
        <div class="s-col">
          <ScreenPanel title="全国概览">
            <div class="kpis">
              <div class="kpi">
                <div class="kpi-val">{{ fmt(summary.count) }}<i>套</i></div>
                <div class="kpi-label">真实房源</div>
              </div>
              <div class="kpi">
                <div class="kpi-val">{{ summary.province_count || 0 }}<i>/{{ summary.city_count || 0 }}</i></div>
                <div class="kpi-label">覆盖省 / 城市</div>
              </div>
              <div class="kpi">
                <div class="kpi-val">{{ fmt(summary.district_count) }}<i>个</i></div>
                <div class="kpi-label">覆盖商圈</div>
              </div>
              <div class="kpi">
                <div class="kpi-val">{{ fmt(summary.avg_price) }}<i>元/㎡</i></div>
                <div class="kpi-label">平均单价</div>
              </div>
            </div>
          </ScreenPanel>
          <ScreenPanel title="户型结构">
            <Donut :items="roomItems" />
          </ScreenPanel>
          <ScreenPanel :title="rankTitle">
            <RankBar :data="countBars" :max="8" color="#3fe0ff" />
          </ScreenPanel>
        </div>

        <!-- 中央地图 -->
        <div class="s-center">
          <div class="bar">
            <div class="crumbs">
              <template v-for="(p, i) in path" :key="p.adcode">
                <span
                  class="crumb"
                  :class="{ active: i === path.length - 1, link: i < path.length - 1 }"
                  @click="crumbTo(i)"
                  >{{ p.name }}</span
                >
                <span v-if="i < path.length - 1" class="sep">›</span>
              </template>
            </div>
            <button v-if="path.length > 1" class="back" @click="mapRef?.back()">‹ 返回上级</button>
          </div>
          <div class="map-wrap">
            <GeoMap3D
              ref="mapRef"
              :data-map="dataMap"
              value-label="真实房源数"
              :leaf-click-label="leafClickLabel"
              @levelchange="onLevelChange"
              @regionclick="onRegionClick"
            />
          </div>
          <div class="hint">{{ mapHint }}</div>
        </div>

        <!-- 右列 -->
        <div class="s-col">
          <ScreenPanel title="城市房源数 TOP10（全国）">
            <RankBar :data="cityTop" :max="10" color="#ffd166" />
          </ScreenPanel>
          <ScreenPanel :title="priceTitle">
            <RankBar :data="priceBars" :max="8" color="#7c8cff" />
          </ScreenPanel>
          <ScreenPanel title="数据明细">
            <div class="dtable">
              <div class="dt-head">
                <span class="c-name">名称</span>
                <span>房源</span>
                <span>均价</span>
                <span>商圈</span>
              </div>
              <div class="dt-body">
                <div v-for="r in tableRows" :key="r.name" class="dt-row">
                  <span class="c-name">{{ r.name }}</span>
                  <span>{{ fmt(r.count) }}</span>
                  <span>{{ fmt(r.avg_price) }}</span>
                  <span>{{ r.district_count ? fmt(r.district_count) : '—' }}</span>
                </div>
                <div v-if="!tableRows.length" class="dt-empty">暂无数据</div>
              </div>
            </div>
          </ScreenPanel>
        </div>
      </div>
      <BaiduPropertyMap
        :visible="baiduVisible"
        :title="baiduTitle"
        :address="baiduAddress"
        :payload="baiduPayload"
        :loading="baiduLoading"
        @close="baiduVisible = false"
      />
    </div>
  </div>
</template>

<style scoped>
.screen-root { /* 定义当前选择器的样式作用域。 */
  position: fixed; /* 设置元素定位方式。 */
  inset: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  overflow: hidden; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: /* 设置背景样式。 */
    radial-gradient(1200px 700px at 50% 18%, #0a2249 0%, #061634 55%, #030c1e 100%); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #cfe8ff; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.stage { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  top: 50%; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: 50%; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  transform-origin: center center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

/* 顶栏 */
.s-header { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  height: 70px; /* 设置元素高度。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  background: linear-gradient(180deg, rgba(13, 44, 88, 0.6), rgba(6, 18, 40, 0)); /* 设置背景样式。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.15); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.s-title { /* 定义当前选择器的样式作用域。 */
  font-size: 32px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
  letter-spacing: 6px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: linear-gradient(180deg, #e8f7ff, #5fd0ff); /* 设置背景样式。 */
  -webkit-background-clip: text; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background-clip: text; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: transparent; /* 设置文字颜色。 */
  text-shadow: 0 2px 16px rgba(63, 224, 255, 0.35); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.s-meta { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  right: 24px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  top: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  height: 100%; /* 设置元素高度。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  align-items: flex-end; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  gap: 6px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.s-clock { /* 定义当前选择器的样式作用域。 */
  font-size: 14px; /* 设置文字大小。 */
  color: #8fc0e8; /* 设置文字颜色。 */
  font-variant-numeric: tabular-nums; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.s-nav { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  gap: 14px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.s-nav a { /* 定义当前选择器的样式作用域。 */
  font-size: 13px; /* 设置文字大小。 */
  color: #9fd0f0; /* 设置文字颜色。 */
  text-decoration: none; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding: 3px 10px; /* 设置元素内边距。 */
  border: 1px solid rgba(63, 224, 255, 0.25); /* 设置边框样式。 */
  border-radius: 4px; /* 设置圆角半径。 */
  transition: all 0.2s; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.s-nav a:hover { /* 定义当前选择器的样式作用域。 */
  color: #fff; /* 设置文字颜色。 */
  background: rgba(63, 224, 255, 0.15); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */

/* 主体三列 */
.s-body { /* 定义当前选择器的样式作用域。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-height: 0; /* 设置元素最小高度。 */
  display: flex; /* 设置元素布局模式。 */
  gap: 16px; /* 设置子元素之间的间距。 */
  padding: 16px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.s-col { /* 定义当前选择器的样式作用域。 */
  width: 470px; /* 设置元素宽度。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  gap: 16px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.s-center { /* 定义当前选择器的样式作用域。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

/* 面包屑 */
.bar { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 12px; /* 设置子元素之间的间距。 */
  height: 40px; /* 设置元素高度。 */
} /* 结束当前样式规则块。 */
.crumbs { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 8px; /* 设置子元素之间的间距。 */
  font-size: 16px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.crumb.link { /* 定义当前选择器的样式作用域。 */
  cursor: pointer; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #8fc0e8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.crumb.link:hover { /* 定义当前选择器的样式作用域。 */
  color: #5fe9ff; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.crumb.active { /* 定义当前选择器的样式作用域。 */
  color: #fff; /* 设置文字颜色。 */
  font-weight: 700; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */
.sep { /* 定义当前选择器的样式作用域。 */
  color: #4a6f92; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.back { /* 定义当前选择器的样式作用域。 */
  cursor: pointer; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(63, 224, 255, 0.12); /* 设置背景样式。 */
  border: 1px solid rgba(63, 224, 255, 0.4); /* 设置边框样式。 */
  color: #bfeaff; /* 设置文字颜色。 */
  padding: 4px 14px; /* 设置元素内边距。 */
  border-radius: 4px; /* 设置圆角半径。 */
  font-size: 13px; /* 设置文字大小。 */
  transition: all 0.2s; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.back:hover { /* 定义当前选择器的样式作用域。 */
  background: rgba(63, 224, 255, 0.25); /* 设置背景样式。 */
  color: #fff; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.map-wrap { /* 定义当前选择器的样式作用域。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-height: 0; /* 设置元素最小高度。 */
  position: relative; /* 设置元素定位方式。 */
} /* 结束当前样式规则块。 */
.hint { /* 定义当前选择器的样式作用域。 */
  height: 22px; /* 设置元素高度。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  font-size: 12px; /* 设置文字大小。 */
  color: #5e84a8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */

/* KPI */
.kpis { /* 定义当前选择器的样式作用域。 */
  height: 100%; /* 设置元素高度。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: 1fr 1fr; /* 设置网格列布局。 */
  gap: 10px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.kpi { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  background: rgba(63, 224, 255, 0.05); /* 设置背景样式。 */
  border: 1px solid rgba(63, 224, 255, 0.12); /* 设置边框样式。 */
  border-radius: 4px; /* 设置圆角半径。 */
} /* 结束当前样式规则块。 */
.kpi-val { /* 定义当前选择器的样式作用域。 */
  font-size: 30px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
  color: #5fe9ff; /* 设置文字颜色。 */
  font-variant-numeric: tabular-nums; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  text-shadow: 0 0 14px rgba(63, 224, 255, 0.4); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.kpi-val i { /* 定义当前选择器的样式作用域。 */
  font-size: 13px; /* 设置文字大小。 */
  font-style: normal; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #7fb0d8; /* 设置文字颜色。 */
  margin-left: 3px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.kpi-label { /* 定义当前选择器的样式作用域。 */
  margin-top: 4px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  font-size: 13px; /* 设置文字大小。 */
  color: #9fc4e4; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */

/* 明细表 */
.dtable { /* 定义当前选择器的样式作用域。 */
  height: 100%; /* 设置元素高度。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  font-size: 13px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.dt-head, /* 设置当前样式属性，控制页面布局或视觉展示。 */
.dt-row { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: 1.4fr 1fr 1fr 1fr; /* 设置网格列布局。 */
  gap: 4px; /* 设置子元素之间的间距。 */
  text-align: right; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.dt-head { /* 定义当前选择器的样式作用域。 */
  color: #7fb0d8; /* 设置文字颜色。 */
  padding: 4px 6px; /* 设置元素内边距。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.dt-body { /* 定义当前选择器的样式作用域。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-height: 0; /* 设置元素最小高度。 */
  overflow-y: auto; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.dt-row { /* 定义当前选择器的样式作用域。 */
  padding: 5px 6px; /* 设置元素内边距。 */
  border-bottom: 1px dashed rgba(63, 224, 255, 0.08); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #cfe8ff; /* 设置文字颜色。 */
  font-variant-numeric: tabular-nums; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.dt-row:nth-child(odd) { /* 定义当前选择器的样式作用域。 */
  background: rgba(63, 224, 255, 0.03); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.c-name { /* 定义当前选择器的样式作用域。 */
  text-align: left; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #eaf6ff; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.dt-empty { /* 定义当前选择器的样式作用域。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #5e84a8; /* 设置文字颜色。 */
  padding-top: 20px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.dt-body::-webkit-scrollbar { /* 定义当前选择器的样式作用域。 */
  width: 5px; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */
.dt-body::-webkit-scrollbar-thumb { /* 定义当前选择器的样式作用域。 */
  background: rgba(63, 224, 255, 0.3); /* 设置背景样式。 */
  border-radius: 3px; /* 设置圆角半径。 */
} /* 结束当前样式规则块。 */
</style>
