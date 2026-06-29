<!-- 文件功能：实现房源总览仪表盘，展示统计卡片、3D 地图和多类分析图表。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。
import { useRouter } from 'vue-router' // 逐行注释：导入本行所需的依赖。

import { getCityDistricts, getOverview, getPriceDistribution } from '@/api' // 逐行注释：导入本行所需的依赖。
import CityMap3D from '@/components/CityMap3D.vue' // 逐行注释：导入本行所需的依赖。
import RegionSelector from '@/components/RegionSelector.vue' // 逐行注释：导入本行所需的依赖。
import StatCard from '@/components/StatCard.vue' // 逐行注释：导入本行所需的依赖。
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue' // 逐行注释：导入本行所需的依赖。
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue' // 逐行注释：导入本行所需的依赖。
import { useAppStore } from '@/store/app' // 逐行注释：导入本行所需的依赖。

const store = useAppStore() // 逐行注释：声明并初始化当前变量。
const router = useRouter() // 逐行注释：声明并初始化当前变量。

const overview = ref({}) // 逐行注释：声明并初始化当前变量。
const districts = ref([]) // 逐行注释：声明并初始化当前变量。
const distribution = ref([]) // 逐行注释：声明并初始化当前变量。
const selectedProvince = ref('') // 逐行注释：声明并初始化当前变量。
const selectedDistrictId = ref(null) // 逐行注释：声明并初始化当前变量。

// 函数功能：计算当前选中城市对象。
const currentCity = computed(() => store.cities.find((c) => c.id === store.currentCityId)) // 逐行注释：声明并初始化当前变量。
// 函数功能：计算当前选中区域对象。
const currentDistrict = computed(() => districts.value.find((d) => d.id === selectedDistrictId.value)) // 逐行注释：声明并初始化当前变量。
// 函数功能：计算当前图表和地图要展示的区域列表。
const visibleDistricts = computed(() => // 逐行注释：声明并初始化当前变量。
  selectedDistrictId.value // 逐行注释：执行本行前端逻辑。
    ? districts.value.filter((d) => d.id === selectedDistrictId.value) // 逐行注释：执行本行前端逻辑。
    : districts.value, // 逐行注释：配置当前对象字段。
) // 逐行注释：结束当前代码块或数据结构。
// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString() // 逐行注释：声明并初始化当前变量。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) { // 逐行注释：声明当前函数入口。
  if (!cityId) return // 逐行注释：根据条件判断是否执行分支。
  const city = store.cities.find((c) => c.id === cityId) // 逐行注释：声明并初始化当前变量。
  selectedProvince.value = city?.province || '' // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：执行 loadCityData 对应的前端交互或数据处理逻辑。
async function loadCityData() { // 逐行注释：声明当前函数入口。
  const id = store.currentCityId // 逐行注释：声明并初始化当前变量。
  if (!id) { // 逐行注释：根据条件判断是否执行分支。
    districts.value = [] // 逐行注释：赋值或更新当前变量/状态。
    distribution.value = [] // 逐行注释：赋值或更新当前变量/状态。
    return // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。
  const [d, dist] = await Promise.all([getCityDistricts(id), getPriceDistribution(id)]) // 逐行注释：声明并初始化当前变量。
  districts.value = d // 逐行注释：赋值或更新当前变量/状态。
  distribution.value = dist // 逐行注释：赋值或更新当前变量/状态。
  if (selectedDistrictId.value && !d.find((item) => item.id === selectedDistrictId.value)) { // 逐行注释：根据条件判断是否执行分支。
    selectedDistrictId.value = null // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

onMounted(async () => { // 逐行注释：注册 Vue 生命周期回调。
  await store.loadCities() // 逐行注释：等待异步操作完成。
  syncProvinceByCity(store.currentCityId) // 逐行注释：执行本行前端逻辑。
  overview.value = await getOverview() // 逐行注释：赋值或更新当前变量/状态。
  await loadCityData() // 逐行注释：等待异步操作完成。
}) // 逐行注释：执行本行前端逻辑。

watch( // 逐行注释：监听响应式数据变化。
  () => store.currentCityId, // 逐行注释：继续声明当前列表项或参数项。
  async (cityId) => { // 逐行注释：执行本行前端逻辑。
    syncProvinceByCity(cityId) // 逐行注释：执行本行前端逻辑。
    await loadCityData() // 逐行注释：等待异步操作完成。
  }, // 逐行注释：结束当前代码块或数据结构。
) // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理 3D 地图区域选择并加载对应趋势数据。
function onSelectDistrict(d) { // 逐行注释：声明当前函数入口。
  router.push({ name: 'explore', query: { city_id: store.currentCityId, district_id: d.id } }) // 逐行注释：执行路由跳转或路由操作。
} // 逐行注释：结束当前代码块或数据结构。
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
.hero { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: flex-start; /* 逐行注释：设置当前样式属性。 */
  justify-content: space-between; /* 逐行注释：设置当前样式属性。 */
  gap: 16px; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 24px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hero h1 { /* 逐行注释：开始当前样式规则块。 */
  margin: 0 0 8px; /* 逐行注释：设置当前样式属性。 */
  font-size: 28px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  background: linear-gradient(90deg, #1e3a8a, #2563eb); /* 逐行注释：设置当前样式属性。 */
  -webkit-background-clip: text; /* 逐行注释：设置当前样式属性。 */
  background-clip: text; /* 逐行注释：设置当前样式属性。 */
  -webkit-text-fill-color: transparent; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hero p { /* 逐行注释：开始当前样式规则块。 */
  margin: 0; /* 逐行注释：设置当前样式属性。 */
  max-width: 640px; /* 逐行注释：设置当前样式属性。 */
  line-height: 1.6; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hero-region { /* 逐行注释：开始当前样式规则块。 */
  flex-shrink: 0; /* 逐行注释：设置当前样式属性。 */
  justify-content: flex-end; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.stats { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.stats .el-col { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.map-card { /* 逐行注释：开始当前样式规则块。 */
  padding-bottom: 20px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
