<!-- 文件功能：实现全国二手房数据大屏，联动地图、排行、表格和统计面板。 -->
<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
  getRealAreaProperties, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  getRealCities, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  getRealDistricts, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  getRealProvinces, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  getRealSummary, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} from '@/api' // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
import BaiduPropertyMap from '@/components/screen/BaiduPropertyMap.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import Donut from '@/components/screen/Donut.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import GeoMap3D from '@/components/screen/GeoMap3D.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import RankBar from '@/components/screen/RankBar.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import ScreenPanel from '@/components/screen/ScreenPanel.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAutoFit } from '@/composables/useAutoFit' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { normalizeName } from '@/utils/geo' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const MUNICIPALITIES = new Set(['北京', '北京市', '上海', '上海市', '天津', '天津市', '重庆', '重庆市']) // 保存MUNICIPALITIES相关业务数据，作为后续计算、渲染或请求的输入。
const { scale, designW, designH } = useAutoFit() // 保存{相关业务数据，作为后续计算、渲染或请求的输入。

const mapRef = ref(null) // 创建mapRef响应式状态，用于驱动页面渲染、表单输入或接口参数。
const summary = ref({}) // 创建概览统计数据，用于驱动页面渲染、表单输入或接口参数。
const rankData = ref([]) // 当前层级行：省份列表 / 某省城市列表
const path = ref([{ adcode: 100000, name: '全国' }]) // 创建地图钻取路径，用于驱动页面渲染、表单输入或接口参数。
const clock = ref('') // 创建clock响应式状态，用于驱动页面渲染、表单输入或接口参数。
const baiduVisible = ref(false) // 创建baiduVisible响应式状态，用于驱动页面渲染、表单输入或接口参数。
const baiduLoading = ref(false) // 创建baiduLoading响应式状态，用于驱动页面渲染、表单输入或接口参数。
const baiduPayload = ref({}) // 创建百度地图弹窗房源点位数据，用于驱动页面渲染、表单输入或接口参数。
const baiduTitle = ref('') // 创建baiduTitle响应式状态，用于驱动页面渲染、表单输入或接口参数。
const baiduAddress = ref('') // 创建baiduAddress响应式状态，用于驱动页面渲染、表单输入或接口参数。

// path 保存地图钻取路径：全国 -> 省/直辖市 -> 城市；其长度决定当前接口口径。
// 函数功能：计算当前大屏地图层级。
const level = computed(() => path.value.length) // 1 全国 / 2 省 / 3 市
// 函数功能：判断当前是否处于直辖市层级。
const isMunicipalityLevel = computed( // 基于响应式数据派生isMunicipalityLevel，用于保持界面展示与数据状态同步。
  () => level.value === 2 && MUNICIPALITIES.has(path.value[1]?.name), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：判断当前是否展示区县级地图。
const isDistrictMapLevel = computed(() => level.value >= 3 || isMunicipalityLevel.value) // 基于响应式数据派生isDistrictMapLevel，用于保持界面展示与数据状态同步。
// 函数功能：根据设计稿尺寸计算大屏缩放样式。
const stageStyle = computed(() => ({ // 基于响应式数据派生stageStyle，用于保持界面展示与数据状态同步。
  width: designW + 'px', // 声明width字段，作为组件配置、请求参数或图表数据的一部分。
  height: designH + 'px', // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
  transform: `translate(-50%, -50%) scale(${scale.value})`, // 声明transform字段，作为组件配置、请求参数或图表数据的一部分。
})) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

// 地图着色数据：全国按省、省级按市的「真实房源数」；市级（商圈）无地图边界 -> 自然不匹配走中性色
// 函数功能：将当前层级统计数据整理为地图查找表。
const dataMap = computed(() => { // 基于响应式数据派生dataMap，用于保持界面展示与数据状态同步。
  const m = {} // 保存m相关业务数据，作为后续计算、渲染或请求的输入。
  for (const r of rankData.value) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    m[r.name] = r.count // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    m[normalizeName(r.name)] = r.count // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return m // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：计算当前排行面板标题。
const rankTitle = computed(() => { // 基于响应式数据派生rankTitle，用于保持界面展示与数据状态同步。
  if (level.value === 1) return '省份房源数 TOP' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (isMunicipalityLevel.value) return `${path.value[1]?.name} · 行政区房源数 TOP` // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (level.value === 2) return `${path.value[1]?.name} · 城市房源数 TOP` // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return `${path.value[2]?.name} · 行政区房源数 TOP` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：计算当前价格面板标题。
const priceTitle = computed( // 基于响应式数据派生priceTitle，用于保持界面展示与数据状态同步。
  () => // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    (level.value === 1 ? '省份' : level.value === 2 && !isMunicipalityLevel.value ? '城市' : '行政区') + // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    '均价 TOP（元/㎡）', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：整理户型分布数据。
const roomItems = computed(() => summary.value.room_dist || []) // 基于响应式数据派生roomItems，用于保持界面展示与数据状态同步。
// 函数功能：整理房源数量排行条形图数据。
const countBars = computed(() => rankData.value.map((r) => ({ name: r.name, value: r.count }))) // 基于响应式数据派生countBars，用于保持界面展示与数据状态同步。
// 函数功能：整理均价排行条形图数据。
const priceBars = computed(() => // 基于响应式数据派生priceBars，用于保持界面展示与数据状态同步。
  [...rankData.value] // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .sort((a, b) => (b.avg_price || 0) - (a.avg_price || 0)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .map((r) => ({ name: r.name, value: r.avg_price || 0 })), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：整理城市 Top 列表数据。
const cityTop = computed(() => summary.value.top_cities || []) // 基于响应式数据派生cityTop，用于保持界面展示与数据状态同步。
// 函数功能：整理大屏表格展示行数据。
const tableRows = computed(() => rankData.value.slice(0, 14)) // 基于响应式数据派生tableRows，用于保持界面展示与数据状态同步。
// 函数功能：计算地图操作提示文案。
const mapHint = computed(() => // 基于响应式数据派生mapHint，用于保持界面展示与数据状态同步。
  isDistrictMapLevel.value // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    ? '拖拽旋转 · 滚轮缩放 · 点击区县查看百度地图房源点' // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    : '拖拽旋转 · 滚轮缩放 · 点击高亮区域下钻（省 → 市）', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：计算地图叶子节点点击按钮文案。
const leafClickLabel = computed(() => (isDistrictMapLevel.value ? '查看百度地图房源点' : '')) // 基于响应式数据派生leafClickLabel，用于保持界面展示与数据状态同步。

// 函数功能：处理大屏数据层级切换。
async function onLevelChange(ctx) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  path.value = ctx.path // 更新path.value对应的页面状态，使界面展示与最新业务数据一致。
  // 地图每下钻一层，排行数据也切换到同一层级，保证地图颜色和侧栏排行同源。
  if (ctx.path.length === 1) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    rankData.value = await getRealProvinces() // 等待异步接口或资源加载完成，再继续更新页面状态。
  } else if (ctx.path.length === 2) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    rankData.value = await getRealCities(ctx.path[1].name) // 等待异步接口或资源加载完成，再继续更新页面状态。
  } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    // 市级下钻：按行政区汇总该市商圈房源数，匹配城市地图边界
    rankData.value = await getRealDistricts(ctx.path[2].name) // 等待异步接口或资源加载完成，再继续更新页面状态。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据面包屑切换到对应地图层级。
function crumbTo(i) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (i < path.value.length - 1) mapRef.value?.goToLevel(i) // 根据当前状态、接口结果或用户输入选择对应交互路径。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理地图区域点击并触发下钻或房源加载。
async function onRegionClick(region) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!isDistrictMapLevel.value || !region?.name) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const cityName = isMunicipalityLevel.value ? path.value[1]?.name : path.value[2]?.name // 保存cityName相关业务数据，作为后续计算、渲染或请求的输入。
  const areaPath = path.value.slice(1).map((item) => item.name) // 保存areaPath相关业务数据，作为后续计算、渲染或请求的输入。
  // 点击行政区后先给弹窗一个空结构，随后用真实房源点位数据替换，避免界面闪烁。
  baiduTitle.value = `${region.name} · 百度地图房源分布` // 更新baiduTitle.value对应的页面状态，使界面展示与最新业务数据一致。
  baiduAddress.value = `${areaPath.join('')}${region.name}` // 更新baiduAddress.value对应的页面状态，使界面展示与最新业务数据一致。
  baiduVisible.value = true // 更新baiduVisible.value对应的页面状态，使界面展示与最新业务数据一致。
  baiduLoading.value = true // 更新baiduLoading.value对应的页面状态，使界面展示与最新业务数据一致。
  baiduPayload.value = { // 更新baiduPayload.value对应的页面状态，使界面展示与最新业务数据一致。
    area: region.name, // 声明area字段，作为组件配置、请求参数或图表数据的一部分。
    property_count: region.value || 0, // 声明property_count字段，作为组件配置、请求参数或图表数据的一部分。
    coordinate_count: 0, // 声明coordinate_count字段，作为组件配置、请求参数或图表数据的一部分。
    returned_count: 0, // 声明returned_count字段，作为组件配置、请求参数或图表数据的一部分。
    avg_price: 0, // 声明avg_price字段，作为组件配置、请求参数或图表数据的一部分。
    items: [], // 声明items字段，作为组件配置、请求参数或图表数据的一部分。
  } // 完成当前参数、配置或响应式数据结构的组装。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    // 后端按“城市 + 行政区”反查商圈房源，并只返回有坐标的点位用于百度地图。
    baiduPayload.value = await getRealAreaProperties({ // 等待异步接口或资源加载完成，再继续更新页面状态。
      city: cityName, // 声明city字段，作为组件配置、请求参数或图表数据的一部分。
      area: region.name, // 声明area字段，作为组件配置、请求参数或图表数据的一部分。
      limit: 800, // 声明limit字段，作为组件配置、请求参数或图表数据的一部分。
    }) // 完成当前参数、配置或响应式数据结构的组装。
  } catch (e) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    console.error('加载百度地图房源点失败', e) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    baiduLoading.value = false // 更新baiduLoading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString() // 保存fmt相关业务数据，作为后续计算、渲染或请求的输入。

let timer // 保存timer相关业务数据，作为后续计算、渲染或请求的输入。
// 函数功能：更新时间文本。
function tick() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const d = new Date() // 保存d相关业务数据，作为后续计算、渲染或请求的输入。
  // 函数功能：生成百分比展示文本。
  const p = (n) => String(n).padStart(2, '0') // 保存p相关业务数据，作为后续计算、渲染或请求的输入。
  clock.value = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}` // 更新clock.value对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(async () => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  tick() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  timer = setInterval(tick, 1000) // 更新timer对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    // 首屏只加载全国概览；省/市排行由 GeoMap3D 初始化后通过 levelchange 拉取。
    summary.value = await getRealSummary() // 等待异步接口或资源加载完成，再继续更新页面状态。
  } catch (e) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    console.error('加载概览失败', e) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。
onBeforeUnmount(() => clearInterval(timer)) // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
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
.screen-root { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: fixed; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  inset: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  overflow: hidden; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
    radial-gradient(1200px 700px at 50% 18%, #0a2249 0%, #061634 55%, #030c1e 100%); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #cfe8ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.stage { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  top: 50%; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  left: 50%; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  transform-origin: center center; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

/* 顶栏 */
.s-header { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: relative; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  height: 70px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  background: linear-gradient(180deg, rgba(13, 44, 88, 0.6), rgba(6, 18, 40, 0)); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.15); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 32px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  letter-spacing: 6px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: linear-gradient(180deg, #e8f7ff, #5fd0ff); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  -webkit-background-clip: text; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background-clip: text; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: transparent; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  text-shadow: 0 2px 16px rgba(63, 224, 255, 0.35); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-meta { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  right: 24px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  top: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  align-items: flex-end; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-clock { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 14px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #8fc0e8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-variant-numeric: tabular-nums; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-nav { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-nav a { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #9fd0f0; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  text-decoration: none; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  padding: 3px 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border: 1px solid rgba(63, 224, 255, 0.25); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 4px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  transition: all 0.2s; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-nav a:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: rgba(63, 224, 255, 0.15); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

/* 主体三列 */
.s-body { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  padding: 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-col { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 470px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  gap: 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.s-center { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

/* 面包屑 */
.bar { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 40px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.crumbs { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 16px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.crumb.link { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  cursor: pointer; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #8fc0e8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.crumb.link:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #5fe9ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.crumb.active { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.sep { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #4a6f92; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.back { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  cursor: pointer; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(63, 224, 255, 0.12); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border: 1px solid rgba(63, 224, 255, 0.4); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #bfeaff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 4px 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-radius: 4px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  transition: all 0.2s; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.back:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: rgba(63, 224, 255, 0.25); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.map-wrap { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  position: relative; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hint { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  height: 22px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #5e84a8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

/* KPI */
.kpis { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: 1fr 1fr; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.kpi { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  background: rgba(63, 224, 255, 0.05); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border: 1px solid rgba(63, 224, 255, 0.12); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 4px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.kpi-val { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 30px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #5fe9ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-variant-numeric: tabular-nums; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  text-shadow: 0 0 14px rgba(63, 224, 255, 0.4); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.kpi-val i { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-style: normal; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #7fb0d8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  margin-left: 3px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.kpi-label { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-top: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #9fc4e4; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

/* 明细表 */
.dtable { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-head, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
.dt-row { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: 1.4fr 1fr 1fr 1fr; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 4px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  text-align: right; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #7fb0d8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 4px 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-body { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  min-height: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  overflow-y: auto; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-row { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  padding: 5px 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-bottom: 1px dashed rgba(63, 224, 255, 0.08); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #cfe8ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-variant-numeric: tabular-nums; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-row:nth-child(odd) { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: rgba(63, 224, 255, 0.03); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.c-name { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  text-align: left; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #eaf6ff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-empty { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #5e84a8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding-top: 20px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-body::-webkit-scrollbar { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 5px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.dt-body::-webkit-scrollbar-thumb { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: rgba(63, 224, 255, 0.3); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 3px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
