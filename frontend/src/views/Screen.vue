<!-- 文件功能：实现全国二手房数据大屏，联动地图、排行、表格和统计面板。 -->
<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue' // 逐行注释：导入本行所需的依赖。

import { // 逐行注释：导入本行所需的依赖。
  getRealAreaProperties, // 逐行注释：继续声明当前列表项或参数项。
  getRealCities, // 逐行注释：继续声明当前列表项或参数项。
  getRealDistricts, // 逐行注释：继续声明当前列表项或参数项。
  getRealProvinces, // 逐行注释：继续声明当前列表项或参数项。
  getRealSummary, // 逐行注释：继续声明当前列表项或参数项。
} from '@/api' // 逐行注释：执行本行前端逻辑。
import BaiduPropertyMap from '@/components/screen/BaiduPropertyMap.vue' // 逐行注释：导入本行所需的依赖。
import Donut from '@/components/screen/Donut.vue' // 逐行注释：导入本行所需的依赖。
import GeoMap3D from '@/components/screen/GeoMap3D.vue' // 逐行注释：导入本行所需的依赖。
import RankBar from '@/components/screen/RankBar.vue' // 逐行注释：导入本行所需的依赖。
import ScreenPanel from '@/components/screen/ScreenPanel.vue' // 逐行注释：导入本行所需的依赖。
import { useAutoFit } from '@/composables/useAutoFit' // 逐行注释：导入本行所需的依赖。
import { normalizeName } from '@/utils/geo' // 逐行注释：导入本行所需的依赖。

const MUNICIPALITIES = new Set(['北京', '北京市', '上海', '上海市', '天津', '天津市', '重庆', '重庆市']) // 逐行注释：声明并初始化当前变量。
const { scale, designW, designH } = useAutoFit() // 逐行注释：声明并初始化当前变量。

const mapRef = ref(null) // 逐行注释：声明并初始化当前变量。
const summary = ref({}) // 逐行注释：声明并初始化当前变量。
const rankData = ref([]) // 当前层级行：省份列表 / 某省城市列表
const path = ref([{ adcode: 100000, name: '全国' }]) // 逐行注释：声明并初始化当前变量。
const clock = ref('') // 逐行注释：声明并初始化当前变量。
const baiduVisible = ref(false) // 逐行注释：声明并初始化当前变量。
const baiduLoading = ref(false) // 逐行注释：声明并初始化当前变量。
const baiduPayload = ref({}) // 逐行注释：声明并初始化当前变量。
const baiduTitle = ref('') // 逐行注释：声明并初始化当前变量。
const baiduAddress = ref('') // 逐行注释：声明并初始化当前变量。

// 函数功能：计算当前大屏地图层级。
const level = computed(() => path.value.length) // 1 全国 / 2 省 / 3 市
// 函数功能：判断当前是否处于直辖市层级。
const isMunicipalityLevel = computed( // 逐行注释：声明并初始化当前变量。
  () => level.value === 2 && MUNICIPALITIES.has(path.value[1]?.name), // 逐行注释：继续声明当前列表项或参数项。
) // 逐行注释：结束当前代码块或数据结构。
// 函数功能：判断当前是否展示区县级地图。
const isDistrictMapLevel = computed(() => level.value >= 3 || isMunicipalityLevel.value) // 逐行注释：声明并初始化当前变量。
// 函数功能：根据设计稿尺寸计算大屏缩放样式。
const stageStyle = computed(() => ({ // 逐行注释：声明并初始化当前变量。
  width: designW + 'px', // 逐行注释：配置当前对象字段。
  height: designH + 'px', // 逐行注释：配置当前对象字段。
  transform: `translate(-50%, -50%) scale(${scale.value})`, // 逐行注释：配置当前对象字段。
})) // 逐行注释：执行本行前端逻辑。

// 地图着色数据：全国按省、省级按市的「真实房源数」；市级（商圈）无地图边界 -> 自然不匹配走中性色
// 函数功能：将当前层级统计数据整理为地图查找表。
const dataMap = computed(() => { // 逐行注释：声明并初始化当前变量。
  const m = {} // 逐行注释：声明并初始化当前变量。
  for (const r of rankData.value) { // 逐行注释：遍历集合或范围并逐项处理。
    m[r.name] = r.count // 逐行注释：赋值或更新当前变量/状态。
    m[normalizeName(r.name)] = r.count // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
  return m // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：计算当前排行面板标题。
const rankTitle = computed(() => { // 逐行注释：声明并初始化当前变量。
  if (level.value === 1) return '省份房源数 TOP' // 逐行注释：根据条件判断是否执行分支。
  if (isMunicipalityLevel.value) return `${path.value[1]?.name} · 行政区房源数 TOP` // 逐行注释：根据条件判断是否执行分支。
  if (level.value === 2) return `${path.value[1]?.name} · 城市房源数 TOP` // 逐行注释：根据条件判断是否执行分支。
  return `${path.value[2]?.name} · 行政区房源数 TOP` // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。
// 函数功能：计算当前价格面板标题。
const priceTitle = computed( // 逐行注释：声明并初始化当前变量。
  () => // 逐行注释：执行本行前端逻辑。
    (level.value === 1 ? '省份' : level.value === 2 && !isMunicipalityLevel.value ? '城市' : '行政区') + // 逐行注释：执行本行前端逻辑。
    '均价 TOP（元/㎡）', // 逐行注释：继续声明当前列表项或参数项。
) // 逐行注释：结束当前代码块或数据结构。

// 函数功能：整理户型分布数据。
const roomItems = computed(() => summary.value.room_dist || []) // 逐行注释：声明并初始化当前变量。
// 函数功能：整理房源数量排行条形图数据。
const countBars = computed(() => rankData.value.map((r) => ({ name: r.name, value: r.count }))) // 逐行注释：声明并初始化当前变量。
// 函数功能：整理均价排行条形图数据。
const priceBars = computed(() => // 逐行注释：声明并初始化当前变量。
  [...rankData.value] // 逐行注释：执行本行前端逻辑。
    .sort((a, b) => (b.avg_price || 0) - (a.avg_price || 0)) // 逐行注释：执行本行前端逻辑。
    .map((r) => ({ name: r.name, value: r.avg_price || 0 })), // 逐行注释：配置当前对象字段。
) // 逐行注释：结束当前代码块或数据结构。
// 函数功能：整理城市 Top 列表数据。
const cityTop = computed(() => summary.value.top_cities || []) // 逐行注释：声明并初始化当前变量。
// 函数功能：整理大屏表格展示行数据。
const tableRows = computed(() => rankData.value.slice(0, 14)) // 逐行注释：声明并初始化当前变量。
// 函数功能：计算地图操作提示文案。
const mapHint = computed(() => // 逐行注释：声明并初始化当前变量。
  isDistrictMapLevel.value // 逐行注释：执行本行前端逻辑。
    ? '拖拽旋转 · 滚轮缩放 · 点击区县查看百度地图房源点' // 逐行注释：执行本行前端逻辑。
    : '拖拽旋转 · 滚轮缩放 · 点击高亮区域下钻（省 → 市）', // 逐行注释：配置当前对象字段。
) // 逐行注释：结束当前代码块或数据结构。
// 函数功能：计算地图叶子节点点击按钮文案。
const leafClickLabel = computed(() => (isDistrictMapLevel.value ? '查看百度地图房源点' : '')) // 逐行注释：声明并初始化当前变量。

// 函数功能：处理大屏数据层级切换。
async function onLevelChange(ctx) { // 逐行注释：声明当前函数入口。
  path.value = ctx.path // 逐行注释：赋值或更新当前变量/状态。
  if (ctx.path.length === 1) { // 逐行注释：根据条件判断是否执行分支。
    rankData.value = await getRealProvinces() // 逐行注释：赋值或更新当前变量/状态。
  } else if (ctx.path.length === 2) { // 逐行注释：执行本行前端逻辑。
    rankData.value = await getRealCities(ctx.path[1].name) // 逐行注释：赋值或更新当前变量/状态。
  } else { // 逐行注释：执行本行前端逻辑。
    // 市级下钻：按行政区汇总该市商圈房源数，匹配城市地图边界
    rankData.value = await getRealDistricts(ctx.path[2].name) // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据面包屑切换到对应地图层级。
function crumbTo(i) { // 逐行注释：声明当前函数入口。
  if (i < path.value.length - 1) mapRef.value?.goToLevel(i) // 逐行注释：根据条件判断是否执行分支。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理地图区域点击并触发下钻或房源加载。
async function onRegionClick(region) { // 逐行注释：声明当前函数入口。
  if (!isDistrictMapLevel.value || !region?.name) return // 逐行注释：根据条件判断是否执行分支。
  const cityName = isMunicipalityLevel.value ? path.value[1]?.name : path.value[2]?.name // 逐行注释：声明并初始化当前变量。
  const areaPath = path.value.slice(1).map((item) => item.name) // 逐行注释：声明并初始化当前变量。
  baiduTitle.value = `${region.name} · 百度地图房源分布` // 逐行注释：赋值或更新当前变量/状态。
  baiduAddress.value = `${areaPath.join('')}${region.name}` // 逐行注释：赋值或更新当前变量/状态。
  baiduVisible.value = true // 逐行注释：赋值或更新当前变量/状态。
  baiduLoading.value = true // 逐行注释：赋值或更新当前变量/状态。
  baiduPayload.value = { // 逐行注释：赋值或更新当前变量/状态。
    area: region.name, // 逐行注释：配置当前对象字段。
    property_count: region.value || 0, // 逐行注释：配置当前对象字段。
    coordinate_count: 0, // 逐行注释：配置当前对象字段。
    returned_count: 0, // 逐行注释：返回当前表达式结果。
    avg_price: 0, // 逐行注释：配置当前对象字段。
    items: [], // 逐行注释：配置当前对象字段。
  } // 逐行注释：结束当前代码块或数据结构。
  try { // 逐行注释：开始执行可能失败的逻辑。
    baiduPayload.value = await getRealAreaProperties({ // 逐行注释：赋值或更新当前变量/状态。
      city: cityName, // 逐行注释：配置当前对象字段。
      area: region.name, // 逐行注释：配置当前对象字段。
      limit: 800, // 逐行注释：配置当前对象字段。
    }) // 逐行注释：执行本行前端逻辑。
  } catch (e) { // 逐行注释：执行本行前端逻辑。
    console.error('加载百度地图房源点失败', e) // 逐行注释：执行本行前端逻辑。
  } finally { // 逐行注释：执行本行前端逻辑。
    baiduLoading.value = false // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString() // 逐行注释：声明并初始化当前变量。

let timer // 逐行注释：声明并初始化当前变量。
// 函数功能：更新时间文本。
function tick() { // 逐行注释：声明当前函数入口。
  const d = new Date() // 逐行注释：声明并初始化当前变量。
  // 函数功能：生成百分比展示文本。
  const p = (n) => String(n).padStart(2, '0') // 逐行注释：声明并初始化当前变量。
  clock.value = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}` // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

onMounted(async () => { // 逐行注释：注册 Vue 生命周期回调。
  tick() // 逐行注释：执行本行前端逻辑。
  timer = setInterval(tick, 1000) // 逐行注释：赋值或更新当前变量/状态。
  try { // 逐行注释：开始执行可能失败的逻辑。
    summary.value = await getRealSummary() // 逐行注释：赋值或更新当前变量/状态。
  } catch (e) { // 逐行注释：执行本行前端逻辑。
    console.error('加载概览失败', e) // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。
}) // 逐行注释：执行本行前端逻辑。
onBeforeUnmount(() => clearInterval(timer)) // 逐行注释：注册 Vue 生命周期回调。
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
.screen-root { /* 逐行注释：开始当前样式规则块。 */
  position: fixed; /* 逐行注释：设置当前样式属性。 */
  inset: 0; /* 逐行注释：设置当前样式属性。 */
  overflow: hidden; /* 逐行注释：设置当前样式属性。 */
  background: /* 逐行注释：设置当前样式属性。 */
    radial-gradient(1200px 700px at 50% 18%, #0a2249 0%, #061634 55%, #030c1e 100%); /* 逐行注释：声明当前样式规则。 */
  color: #cfe8ff; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.stage { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  top: 50%; /* 逐行注释：设置当前样式属性。 */
  left: 50%; /* 逐行注释：设置当前样式属性。 */
  transform-origin: center center; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */

/* 顶栏 */
.s-header { /* 逐行注释：开始当前样式规则块。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
  height: 70px; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  background: linear-gradient(180deg, rgba(13, 44, 88, 0.6), rgba(6, 18, 40, 0)); /* 逐行注释：设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.15); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-title { /* 逐行注释：开始当前样式规则块。 */
  font-size: 32px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  letter-spacing: 6px; /* 逐行注释：设置当前样式属性。 */
  background: linear-gradient(180deg, #e8f7ff, #5fd0ff); /* 逐行注释：设置当前样式属性。 */
  -webkit-background-clip: text; /* 逐行注释：设置当前样式属性。 */
  background-clip: text; /* 逐行注释：设置当前样式属性。 */
  color: transparent; /* 逐行注释：设置当前样式属性。 */
  text-shadow: 0 2px 16px rgba(63, 224, 255, 0.35); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-meta { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  right: 24px; /* 逐行注释：设置当前样式属性。 */
  top: 0; /* 逐行注释：设置当前样式属性。 */
  height: 100%; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  align-items: flex-end; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  gap: 6px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-clock { /* 逐行注释：开始当前样式规则块。 */
  font-size: 14px; /* 逐行注释：设置当前样式属性。 */
  color: #8fc0e8; /* 逐行注释：设置当前样式属性。 */
  font-variant-numeric: tabular-nums; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-nav { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  gap: 14px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-nav a { /* 逐行注释：开始当前样式规则块。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  color: #9fd0f0; /* 逐行注释：设置当前样式属性。 */
  text-decoration: none; /* 逐行注释：设置当前样式属性。 */
  padding: 3px 10px; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.25); /* 逐行注释：设置当前样式属性。 */
  border-radius: 4px; /* 逐行注释：设置当前样式属性。 */
  transition: all 0.2s; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-nav a:hover { /* 逐行注释：开始当前样式规则块。 */
  color: #fff; /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.15); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */

/* 主体三列 */
.s-body { /* 逐行注释：开始当前样式规则块。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  gap: 16px; /* 逐行注释：设置当前样式属性。 */
  padding: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-col { /* 逐行注释：开始当前样式规则块。 */
  width: 470px; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  gap: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.s-center { /* 逐行注释：开始当前样式规则块。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */

/* 面包屑 */
.bar { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 12px; /* 逐行注释：设置当前样式属性。 */
  height: 40px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.crumbs { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 8px; /* 逐行注释：设置当前样式属性。 */
  font-size: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.crumb.link { /* 逐行注释：开始当前样式规则块。 */
  cursor: pointer; /* 逐行注释：设置当前样式属性。 */
  color: #8fc0e8; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.crumb.link:hover { /* 逐行注释：开始当前样式规则块。 */
  color: #5fe9ff; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.crumb.active { /* 逐行注释：开始当前样式规则块。 */
  color: #fff; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.sep { /* 逐行注释：开始当前样式规则块。 */
  color: #4a6f92; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.back { /* 逐行注释：开始当前样式规则块。 */
  cursor: pointer; /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.12); /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.4); /* 逐行注释：设置当前样式属性。 */
  color: #bfeaff; /* 逐行注释：设置当前样式属性。 */
  padding: 4px 14px; /* 逐行注释：设置当前样式属性。 */
  border-radius: 4px; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  transition: all 0.2s; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.back:hover { /* 逐行注释：开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.25); /* 逐行注释：设置当前样式属性。 */
  color: #fff; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.map-wrap { /* 逐行注释：开始当前样式规则块。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hint { /* 逐行注释：开始当前样式规则块。 */
  height: 22px; /* 逐行注释：设置当前样式属性。 */
  text-align: center; /* 逐行注释：设置当前样式属性。 */
  font-size: 12px; /* 逐行注释：设置当前样式属性。 */
  color: #5e84a8; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */

/* KPI */
.kpis { /* 逐行注释：开始当前样式规则块。 */
  height: 100%; /* 逐行注释：设置当前样式属性。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: 1fr 1fr; /* 逐行注释：设置当前样式属性。 */
  gap: 10px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.kpi { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  background: rgba(63, 224, 255, 0.05); /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.12); /* 逐行注释：设置当前样式属性。 */
  border-radius: 4px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.kpi-val { /* 逐行注释：开始当前样式规则块。 */
  font-size: 30px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  color: #5fe9ff; /* 逐行注释：设置当前样式属性。 */
  font-variant-numeric: tabular-nums; /* 逐行注释：设置当前样式属性。 */
  text-shadow: 0 0 14px rgba(63, 224, 255, 0.4); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.kpi-val i { /* 逐行注释：开始当前样式规则块。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  font-style: normal; /* 逐行注释：设置当前样式属性。 */
  color: #7fb0d8; /* 逐行注释：设置当前样式属性。 */
  margin-left: 3px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.kpi-label { /* 逐行注释：开始当前样式规则块。 */
  margin-top: 4px; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  color: #9fc4e4; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */

/* 明细表 */
.dtable { /* 逐行注释：开始当前样式规则块。 */
  height: 100%; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-head, /* 逐行注释：声明当前样式规则。 */
.dt-row { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: 1.4fr 1fr 1fr 1fr; /* 逐行注释：设置当前样式属性。 */
  gap: 4px; /* 逐行注释：设置当前样式属性。 */
  text-align: right; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-head { /* 逐行注释：开始当前样式规则块。 */
  color: #7fb0d8; /* 逐行注释：设置当前样式属性。 */
  padding: 4px 6px; /* 逐行注释：设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.18); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-body { /* 逐行注释：开始当前样式规则块。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  overflow-y: auto; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-row { /* 逐行注释：开始当前样式规则块。 */
  padding: 5px 6px; /* 逐行注释：设置当前样式属性。 */
  border-bottom: 1px dashed rgba(63, 224, 255, 0.08); /* 逐行注释：设置当前样式属性。 */
  color: #cfe8ff; /* 逐行注释：设置当前样式属性。 */
  font-variant-numeric: tabular-nums; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-row:nth-child(odd) { /* 逐行注释：开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.03); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.c-name { /* 逐行注释：开始当前样式规则块。 */
  text-align: left; /* 逐行注释：设置当前样式属性。 */
  color: #eaf6ff; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-empty { /* 逐行注释：开始当前样式规则块。 */
  text-align: center; /* 逐行注释：设置当前样式属性。 */
  color: #5e84a8; /* 逐行注释：设置当前样式属性。 */
  padding-top: 20px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-body::-webkit-scrollbar { /* 逐行注释：开始当前样式规则块。 */
  width: 5px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.dt-body::-webkit-scrollbar-thumb { /* 逐行注释：开始当前样式规则块。 */
  background: rgba(63, 224, 255, 0.3); /* 逐行注释：设置当前样式属性。 */
  border-radius: 3px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
