<!-- 文件功能：实现房源总览仪表盘，展示统计卡片、3D 地图和多类分析图表。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 导入 { computed, onMounted, ref, watch }，供当前前端模块渲染或交互逻辑使用。
import { useRouter } from 'vue-router' // 导入 { useRouter }，供当前前端模块渲染或交互逻辑使用。

import { getCityDistricts, getOverview, getPriceDistribution } from '@/api' // 导入 { getCityDistricts, getOverview, getPriceDistribution }，供当前前端模块渲染或交互逻辑使用。
import CityMap3D from '@/components/CityMap3D.vue' // 导入 CityMap3D，供当前前端模块渲染或交互逻辑使用。
import RegionSelector from '@/components/RegionSelector.vue' // 导入 RegionSelector，供当前前端模块渲染或交互逻辑使用。
import StatCard from '@/components/StatCard.vue' // 导入 StatCard，供当前前端模块渲染或交互逻辑使用。
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue' // 导入 DistrictRankingChart，供当前前端模块渲染或交互逻辑使用。
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue' // 导入 PriceDistributionChart，供当前前端模块渲染或交互逻辑使用。
import { useAppStore } from '@/store/app' // 导入 { useAppStore }，供当前前端模块渲染或交互逻辑使用。

const store = useAppStore() // 创建 store，用于保存页面状态、计算结果或接口参数。
const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。

const overview = ref({}) // 创建 overview，用于保存页面状态、计算结果或接口参数。
const districts = ref([]) // 创建 districts，用于保存页面状态、计算结果或接口参数。
const distribution = ref([]) // 创建 distribution，用于保存页面状态、计算结果或接口参数。
const selectedProvince = ref('') // 创建 selectedProvince，用于保存页面状态、计算结果或接口参数。
const selectedDistrictId = ref(null) // 创建 selectedDistrictId，用于保存页面状态、计算结果或接口参数。

// 函数功能：计算当前选中城市对象。
const currentCity = computed(() => store.cities.find((c) => c.id === store.currentCityId)) // 创建 currentCity，用于保存页面状态、计算结果或接口参数。
// 函数功能：计算当前选中区域对象。
const currentDistrict = computed(() => districts.value.find((d) => d.id === selectedDistrictId.value)) // 创建 currentDistrict，用于保存页面状态、计算结果或接口参数。
// 函数功能：计算当前图表和地图要展示的区域列表。
const visibleDistricts = computed(() => // 创建 visibleDistricts，用于保存页面状态、计算结果或接口参数。
  selectedDistrictId.value // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ? districts.value.filter((d) => d.id === selectedDistrictId.value) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    : districts.value, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。
// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString() // 创建 fmt，用于保存页面状态、计算结果或接口参数。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) { // 定义 syncProvinceByCity 函数，处理页面交互、数据加载或状态同步。
  if (!cityId) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const city = store.cities.find((c) => c.id === cityId) // 创建 city，用于保存页面状态、计算结果或接口参数。
  selectedProvince.value = city?.province || '' // 更新 selectedProvince.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：执行 loadCityData 对应的前端交互或数据处理逻辑。
async function loadCityData() { // 定义 loadCityData 函数，处理页面交互、数据加载或状态同步。
  const id = store.currentCityId // 创建 id，用于保存页面状态、计算结果或接口参数。
  if (!id) { // 根据当前页面状态或接口结果决定是否进入该分支。
    districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
    distribution.value = [] // 更新 distribution.value 响应式状态，让页面展示与最新数据保持一致。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  const [d, dist] = await Promise.all([getCityDistricts(id), getPriceDistribution(id)]) // 创建 [d, dist]，用于保存页面状态、计算结果或接口参数。
  districts.value = d // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
  distribution.value = dist // 更新 distribution.value 响应式状态，让页面展示与最新数据保持一致。
  if (selectedDistrictId.value && !d.find((item) => item.id === selectedDistrictId.value)) { // 根据当前页面状态或接口结果决定是否进入该分支。
    selectedDistrictId.value = null // 更新 selectedDistrictId.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(async () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  syncProvinceByCity(store.currentCityId) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  overview.value = await getOverview() // 更新 overview.value 响应式状态，让页面展示与最新数据保持一致。
  await loadCityData() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => store.currentCityId, // 设置  的值，作为后续渲染、计算或请求的输入。
  async (cityId) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    syncProvinceByCity(cityId) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    await loadCityData() // 等待异步接口或资源加载完成，再继续更新页面状态。
  }, // 结束当前函数、对象、数组或组件配置块。
) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理 3D 地图区域选择并加载对应趋势数据。
function onSelectDistrict(d) { // 定义 onSelectDistrict 函数，处理页面交互、数据加载或状态同步。
  router.push({ name: 'explore', query: { city_id: store.currentCityId, district_id: d.id } }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <div class="page">
    <div class="hero">
      <div>
        <h1>智慧房源探索平台</h1>
        <p class="muted">
          采集二手房数据 · 3D 可视化房价分布 · 智能分析与价格预测，助你做出更明智的购房决策
        </p>
      </div>
      <RegionSelector
        v-model:province="selectedProvince"
        v-model:city-id="store.currentCityId"
        v-model:district-id="selectedDistrictId"
        :cities="store.cities"
        :districts="districts"
        size="large"
        class="hero-region"
      />
    </div>

    <el-row :gutter="16" class="stats">
      <el-col :xs="12" :sm="6">
        <StatCard label="覆盖城市" :value="overview.city_count" suffix="座" icon="MapLocation" color="#2563eb" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard label="在售房源" :value="fmt(overview.property_count)" suffix="套" icon="House" color="#059669" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard label="平均单价" :value="fmt(overview.avg_unit_price)" suffix="元/㎡" icon="Money" color="#d97706" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <StatCard label="最高单价" :value="fmt(overview.max_unit_price)" suffix="元/㎡" icon="TopRight" color="#dc2626" />
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="15">
        <div class="card map-card">
          <div class="section-title">{{ currentCity?.name }}{{ currentDistrict ? ` · ${currentDistrict.name}` : '' }} · 3D 房价地图</div>
          <CityMap3D :districts="visibleDistricts" height="480px" @select="onSelectDistrict" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="9">
        <div class="card">
          <div class="section-title">各区均价排行（元/㎡）</div>
          <DistrictRankingChart :data="visibleDistricts" height="480px" />
        </div>
      </el-col>
    </el-row>

    <div class="card" style="margin-top: 16px">
      <div class="section-title">{{ currentCity?.name }} · 单价分布</div>
      <PriceDistributionChart :data="distribution" height="320px" />
    </div>
  </div>
</template>

<style scoped>
.hero { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: flex-start; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
  gap: 16px; /* 设置子元素之间的间距。 */
  margin-bottom: 24px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.hero h1 { /* 定义当前选择器的样式作用域。 */
  margin: 0 0 8px; /* 设置元素外边距。 */
  font-size: 28px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
  background: linear-gradient(90deg, #1e3a8a, #2563eb); /* 设置背景样式。 */
  -webkit-background-clip: text; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background-clip: text; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  -webkit-text-fill-color: transparent; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.hero p { /* 定义当前选择器的样式作用域。 */
  margin: 0; /* 设置元素外边距。 */
  max-width: 640px; /* 设置元素最大宽度。 */
  line-height: 1.6; /* 设置文本行高。 */
} /* 结束当前样式规则块。 */
.hero-region { /* 定义当前选择器的样式作用域。 */
  flex-shrink: 0; /* 控制弹性布局中元素是否收缩。 */
  justify-content: flex-end; /* 设置主轴内容分布方式。 */
} /* 结束当前样式规则块。 */
.stats { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.stats .el-col { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.map-card { /* 定义当前选择器的样式作用域。 */
  padding-bottom: 20px; /* 设置元素底部内边距。 */
} /* 结束当前样式规则块。 */
</style>
