<!-- 文件功能：实现房源总览仪表盘，展示统计卡片、3D 地图和多类分析图表。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { getCityDistricts, getOverview, getPriceDistribution } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import CityMap3D from '@/components/CityMap3D.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import RegionSelector from '@/components/RegionSelector.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import StatCard from '@/components/StatCard.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAppStore } from '@/store/app' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const store = useAppStore() // 保存store相关业务数据，作为后续计算、渲染或请求的输入。
const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。

const overview = ref({}) // 创建overview响应式状态，用于驱动页面渲染、表单输入或接口参数。
const districts = ref([]) // 创建行政区集合，用于驱动页面渲染、表单输入或接口参数。
const distribution = ref([]) // 创建distribution响应式状态，用于驱动页面渲染、表单输入或接口参数。
const selectedProvince = ref('') // 创建selectedProvince响应式状态，用于驱动页面渲染、表单输入或接口参数。
const selectedDistrictId = ref(null) // 创建selectedDistrictId响应式状态，用于驱动页面渲染、表单输入或接口参数。

// 函数功能：计算当前选中城市对象。
const currentCity = computed(() => store.cities.find((c) => c.id === store.currentCityId)) // 基于响应式数据派生currentCity，用于保持界面展示与数据状态同步。
// 函数功能：计算当前选中区域对象。
const currentDistrict = computed(() => districts.value.find((d) => d.id === selectedDistrictId.value)) // 基于响应式数据派生currentDistrict，用于保持界面展示与数据状态同步。
// 函数功能：计算当前图表和地图要展示的区域列表。
const visibleDistricts = computed(() => // 基于响应式数据派生visibleDistricts，用于保持界面展示与数据状态同步。
  selectedDistrictId.value // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    ? districts.value.filter((d) => d.id === selectedDistrictId.value) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    : districts.value, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString() // 保存fmt相关业务数据，作为后续计算、渲染或请求的输入。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!cityId) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const city = store.cities.find((c) => c.id === cityId) // 保存city相关业务数据，作为后续计算、渲染或请求的输入。
  selectedProvince.value = city?.province || '' // 更新selectedProvince.value对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：执行 loadCityData 对应的前端交互或数据处理逻辑。
async function loadCityData() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const id = store.currentCityId // 保存id相关业务数据，作为后续计算、渲染或请求的输入。
  if (!id) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
    distribution.value = [] // 更新distribution.value对应的页面状态，使界面展示与最新业务数据一致。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  const [d, dist] = await Promise.all([getCityDistricts(id), getPriceDistribution(id)]) // 保存[d相关业务数据，作为后续计算、渲染或请求的输入。
  districts.value = d // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
  distribution.value = dist // 更新distribution.value对应的页面状态，使界面展示与最新业务数据一致。
  if (selectedDistrictId.value && !d.find((item) => item.id === selectedDistrictId.value)) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    selectedDistrictId.value = null // 更新selectedDistrictId.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(async () => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  syncProvinceByCity(store.currentCityId) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  overview.value = await getOverview() // 等待异步接口或资源加载完成，再继续更新页面状态。
  await loadCityData() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => store.currentCityId, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  async (cityId) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    syncProvinceByCity(cityId) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    await loadCityData() // 等待异步接口或资源加载完成，再继续更新页面状态。
  }, // 完成当前参数、配置或响应式数据结构的组装。
) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理 3D 地图区域选择并加载对应趋势数据。
function onSelectDistrict(d) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  router.push({ name: 'explore', query: { city_id: store.currentCityId, district_id: d.id } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。
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
.hero { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: flex-start; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin-bottom: 24px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hero h1 { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0 0 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 28px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  background: linear-gradient(90deg, #1e3a8a, #2563eb); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  -webkit-background-clip: text; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background-clip: text; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  -webkit-text-fill-color: transparent; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hero p { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  max-width: 640px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  line-height: 1.6; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hero-region { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex-shrink: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  justify-content: flex-end; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.stats { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.stats .el-col { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.map-card { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  padding-bottom: 20px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
