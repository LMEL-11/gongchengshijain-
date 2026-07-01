<!-- 文件功能：实现数据分析与预测页面，加载城市分析、挂牌画像和预测表单。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 导入 { computed, onMounted, ref, watch }，供当前前端模块渲染或交互逻辑使用。

import { getCityDistricts, getInvestmentRanking, getListingProfile, getPriceDistribution } from '@/api' // 导入 { getCityDistricts, getInvestmentRanking, getListingProfile, getPriceDistribution }，供当前前端模块渲染或交互逻辑使用。
import PredictionForm from '@/components/PredictionForm.vue' // 导入 PredictionForm，供当前前端模块渲染或交互逻辑使用。
import RegionSelector from '@/components/RegionSelector.vue' // 导入 RegionSelector，供当前前端模块渲染或交互逻辑使用。
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue' // 导入 DistrictRankingChart，供当前前端模块渲染或交互逻辑使用。
import InvestmentChart from '@/components/charts/InvestmentChart.vue' // 导入 InvestmentChart，供当前前端模块渲染或交互逻辑使用。
import ListingProfileChart from '@/components/charts/ListingProfileChart.vue' // 导入 ListingProfileChart，供当前前端模块渲染或交互逻辑使用。
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue' // 导入 PriceDistributionChart，供当前前端模块渲染或交互逻辑使用。
import { useAppStore } from '@/store/app' // 导入 { useAppStore }，供当前前端模块渲染或交互逻辑使用。

const store = useAppStore() // 创建 store，用于保存页面状态、计算结果或接口参数。
const cityId = ref(null) // 创建 cityId，用于保存页面状态、计算结果或接口参数。
const districts = ref([]) // 创建 districts，用于保存页面状态、计算结果或接口参数。
const distribution = ref([]) // 创建 distribution，用于保存页面状态、计算结果或接口参数。
const investment = ref([]) // 创建 investment，用于保存页面状态、计算结果或接口参数。
const selectedProvince = ref('') // 创建 selectedProvince，用于保存页面状态、计算结果或接口参数。
const profileDistrictId = ref(null) // 创建 profileDistrictId，用于保存页面状态、计算结果或接口参数。
const profile = ref(null) // 创建 profile，用于保存页面状态、计算结果或接口参数。
let loadingCity = false // 创建 loadingCity，用于保存页面状态、计算结果或接口参数。

// 函数功能：计算当前挂牌画像对应的区域对象。
const profileDistrict = computed(() => // 创建 profileDistrict，用于保存页面状态、计算结果或接口参数。
  districts.value.find((d) => d.id === profileDistrictId.value), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：从挂牌画像中整理核心统计指标。
const profileStats = computed(() => { // 创建 profileStats，用于保存页面状态、计算结果或接口参数。
  const p = profile.value || {} // 创建 p，用于保存页面状态、计算结果或接口参数。
  return [ // 返回整理后的数据、组件配置或渲染结果。
    { label: '样本套数', value: `${Number(p.property_count || 0).toLocaleString()} 套` }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      label: '当前均价', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      value: p.avg_unit_price ? `${Number(p.avg_unit_price).toLocaleString()} 元/㎡` : '暂无', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      label: '中位单价', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      value: p.median_unit_price ? `${Number(p.median_unit_price).toLocaleString()} 元/㎡` : '暂无', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      label: '挂牌时间样本', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      value: p.date_count ? `${Number(p.date_count).toLocaleString()} 套` : '暂无', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
  ] // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：整理挂牌画像中的交易属性分布分组。
const profileGroups = computed(() => { // 创建 profileGroups，用于保存页面状态、计算结果或接口参数。
  const p = profile.value || {} // 创建 p，用于保存页面状态、计算结果或接口参数。
  return [ // 返回整理后的数据、组件配置或渲染结果。
    { label: '交易权属', items: p.ownership_distribution || [] }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '产权情况', items: p.property_right_distribution || [] }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '抵押情况', items: p.mortgage_distribution || [] }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '税费关键词', items: p.tax_tags || [] }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ] // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：判断挂牌画像是否包含月度挂牌趋势数据。
const hasMonthlyListings = computed(() => // 创建 hasMonthlyListings，用于保存页面状态、计算结果或接口参数。
  Boolean(profile.value?.monthly_listings?.some((item) => item.count)), // 更新 Boolean(profile.value?.monthly_listings?.some((item) 响应式状态，让页面展示与最新数据保持一致。
) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：加载当前区域的挂牌画像数据。
async function loadProfile() { // 定义 loadProfile 函数，处理页面交互、数据加载或状态同步。
  profile.value = profileDistrictId.value ? await getListingProfile(profileDistrictId.value) : null // 更新 profile.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：加载当前城市的区域排行、价格分布和投资排行数据。
async function loadCity() { // 定义 loadCity 函数，处理页面交互、数据加载或状态同步。
  if (!cityId.value) { // 根据当前页面状态或接口结果决定是否进入该分支。
    districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
    distribution.value = [] // 更新 distribution.value 响应式状态，让页面展示与最新数据保持一致。
    investment.value = [] // 更新 investment.value 响应式状态，让页面展示与最新数据保持一致。
    profileDistrictId.value = null // 更新 profileDistrictId.value 响应式状态，让页面展示与最新数据保持一致。
    profile.value = null // 更新 profile.value 响应式状态，让页面展示与最新数据保持一致。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  loadingCity = true // 设置 loadingCity 的值，作为后续渲染、计算或请求的输入。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    const [d, dist, inv] = await Promise.all([ // 创建 [d, dist, inv]，用于保存页面状态、计算结果或接口参数。
      getCityDistricts(cityId.value), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      getPriceDistribution(cityId.value), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      getInvestmentRanking(cityId.value), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ]) // 结束当前函数、对象、数组或组件配置块。
    districts.value = d // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
    distribution.value = dist // 更新 distribution.value 响应式状态，让页面展示与最新数据保持一致。
    investment.value = inv // 更新 investment.value 响应式状态，让页面展示与最新数据保持一致。
    profileDistrictId.value = d.find((item) => item.id === profileDistrictId.value)?.id || (d.length ? d[0].id : null) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    await loadProfile() // 等待异步接口或资源加载完成，再继续更新页面状态。
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loadingCity = false // 设置 loadingCity 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(id) { // 定义 syncProvinceByCity 函数，处理页面交互、数据加载或状态同步。
  if (!id) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const city = store.cities.find((c) => c.id === id) // 创建 city，用于保存页面状态、计算结果或接口参数。
  selectedProvince.value = city?.province || '' // 更新 selectedProvince.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(async () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  cityId.value = store.currentCityId // 更新 cityId.value 响应式状态，让页面展示与最新数据保持一致。
  syncProvinceByCity(cityId.value) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  await loadCity() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 结束当前函数、对象、数组或组件配置块。

watch(cityId, async (id) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  syncProvinceByCity(id) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  if (id) store.setCity(id) // 根据当前页面状态或接口结果决定是否进入该分支。
  await loadCity() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 结束当前函数、对象、数组或组件配置块。

watch(profileDistrictId, () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  if (!loadingCity) loadProfile() // 根据当前页面状态或接口结果决定是否进入该分支。
}) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <div class="page">
    <div class="hero">
      <div>
        <h1 class="title">数据分析与房价预测</h1>
        <p class="muted">多维度剖析区域房价水平、分布与挂牌画像，并基于机器学习模型预测房源价格</p>
      </div>
      <RegionSelector
        v-model:province="selectedProvince"
        v-model:city-id="cityId"
        v-model:district-id="profileDistrictId"
        :cities="store.cities"
        :districts="districts"
        :district-clearable="false"
        size="large"
        class="hero-region"
      />
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="section-title">各区均价排行</div>
          <DistrictRankingChart :data="districts" height="380px" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="card">
          <div class="section-title">单价分布直方图</div>
          <PriceDistributionChart :data="distribution" height="380px" />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="14">
        <div class="card">
          <div class="trend-head">
            <div class="section-title" style="margin: 0">区域挂牌画像</div>
            <el-tag v-if="profileDistrict" effect="plain">{{ profileDistrict.name }}</el-tag>
          </div>
          <div v-if="profile" class="profile-stats">
            <div v-for="item in profileStats" :key="item.label" class="profile-stat">
              <div class="profile-label">{{ item.label }}</div>
              <div class="profile-value">{{ item.value }}</div>
            </div>
          </div>
          <ListingProfileChart
            v-if="hasMonthlyListings"
            :data="profile.monthly_listings"
            height="250px"
          />
          <el-empty
            v-else
            description="当前行政区暂无可统计的挂牌时间数据"
            :image-size="72"
            style="height: 250px"
          />
          <div v-if="profile" class="profile-groups">
            <div v-for="group in profileGroups" :key="group.label" class="profile-group">
              <div class="profile-group-title">{{ group.label }}</div>
              <div v-if="group.items.length" class="profile-tags">
                <el-tag v-for="item in group.items" :key="item.name" effect="plain">
                  {{ item.name }} {{ item.ratio }}%
                </el-tag>
              </div>
              <span v-else class="muted empty-text">暂无</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="card">
          <div class="section-title">🔮 智能房价预测</div>
          <PredictionForm />
        </div>
      </el-col>
    </el-row>

    <div class="card" style="margin-top: 16px">
      <div class="section-title">投资热点分析</div>
      <template v-if="investment.length">
        <p class="muted hint">
          综合「价格洼地 × 市场热度 × 周边配套 × 交易安全 × 挂牌新鲜度」为各区打分：
          气泡越大代表房源样本越多，颜色越深代表投资评分越高；
          位于<strong>左上角（低价 · 高热度/强配套）</strong>的区域通常更具关注价值。
        </p>
        <InvestmentChart :data="investment" height="400px" />
      </template>
      <el-empty
        v-else
        description="当前城市暂无可用于投资评分的房源数据"
        :image-size="80"
        style="height: 400px"
      />
    </div>
  </div>
</template>

<style scoped>
.hero { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: flex-start; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
  gap: 16px; /* 设置子元素之间的间距。 */
  margin-bottom: 20px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.title { /* 定义当前选择器的样式作用域。 */
  margin: 0 0 8px; /* 设置元素外边距。 */
  font-size: 26px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */
.hero p { /* 定义当前选择器的样式作用域。 */
  margin: 0; /* 设置元素外边距。 */
} /* 结束当前样式规则块。 */
.hero-region { /* 定义当前选择器的样式作用域。 */
  flex-shrink: 0; /* 控制弹性布局中元素是否收缩。 */
  justify-content: flex-end; /* 设置主轴内容分布方式。 */
} /* 结束当前样式规则块。 */
.trend-head { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.profile-stats { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: repeat(4, minmax(0, 1fr)); /* 设置网格列布局。 */
  gap: 10px; /* 设置子元素之间的间距。 */
  margin-bottom: 12px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.profile-stat { /* 定义当前选择器的样式作用域。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding: 10px 12px; /* 设置元素内边距。 */
  border: 1px solid #e2e8f0; /* 设置边框样式。 */
  border-radius: 8px; /* 设置圆角半径。 */
  background: #f8fafc; /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.profile-label { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 4px; /* 设置元素底部外边距。 */
  color: #64748b; /* 设置文字颜色。 */
  font-size: 12px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.profile-value { /* 定义当前选择器的样式作用域。 */
  color: #0f172a; /* 设置文字颜色。 */
  font-size: 15px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
  word-break: break-word; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.profile-groups { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* 设置网格列布局。 */
  gap: 12px; /* 设置子元素之间的间距。 */
  margin-top: 12px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.profile-group { /* 定义当前选择器的样式作用域。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding-top: 12px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-top: 1px solid #e2e8f0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.profile-group-title { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 8px; /* 设置元素底部外边距。 */
  color: #334155; /* 设置文字颜色。 */
  font-size: 13px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */
.profile-tags { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  flex-wrap: wrap; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  gap: 6px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.empty-text { /* 定义当前选择器的样式作用域。 */
  font-size: 13px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.hint { /* 定义当前选择器的样式作用域。 */
  margin: -6px 0 12px; /* 设置元素外边距。 */
  font-size: 13px; /* 设置文字大小。 */
  line-height: 1.6; /* 设置文本行高。 */
} /* 结束当前样式规则块。 */
@media (max-width: 768px) { /* 定义当前选择器的样式作用域。 */
  .profile-stats, /* 设置当前样式属性，控制页面布局或视觉展示。 */
  .profile-groups { /* 定义当前选择器的样式作用域。 */
    grid-template-columns: repeat(2, minmax(0, 1fr)); /* 设置网格列布局。 */
  } /* 结束当前样式规则块。 */
} /* 结束当前样式规则块。 */
@media (max-width: 520px) { /* 定义当前选择器的样式作用域。 */
  .hero, /* 设置当前样式属性，控制页面布局或视觉展示。 */
  .trend-head { /* 定义当前选择器的样式作用域。 */
    flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
    align-items: stretch; /* 设置交叉轴对齐方式。 */
  } /* 结束当前样式规则块。 */
  .profile-stats, /* 设置当前样式属性，控制页面布局或视觉展示。 */
  .profile-groups { /* 定义当前选择器的样式作用域。 */
    grid-template-columns: 1fr; /* 设置网格列布局。 */
  } /* 结束当前样式规则块。 */
} /* 结束当前样式规则块。 */
</style>
