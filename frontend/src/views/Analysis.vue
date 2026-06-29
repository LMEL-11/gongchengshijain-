<!-- 文件功能：实现数据分析与预测页面，加载城市分析、挂牌画像和预测表单。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。

import { getCityDistricts, getInvestmentRanking, getListingProfile, getPriceDistribution } from '@/api' // 逐行注释：导入本行所需的依赖。
import PredictionForm from '@/components/PredictionForm.vue' // 逐行注释：导入本行所需的依赖。
import RegionSelector from '@/components/RegionSelector.vue' // 逐行注释：导入本行所需的依赖。
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue' // 逐行注释：导入本行所需的依赖。
import InvestmentChart from '@/components/charts/InvestmentChart.vue' // 逐行注释：导入本行所需的依赖。
import ListingProfileChart from '@/components/charts/ListingProfileChart.vue' // 逐行注释：导入本行所需的依赖。
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue' // 逐行注释：导入本行所需的依赖。
import { useAppStore } from '@/store/app' // 逐行注释：导入本行所需的依赖。

const store = useAppStore() // 逐行注释：声明并初始化当前变量。
const cityId = ref(null) // 逐行注释：声明并初始化当前变量。
const districts = ref([]) // 逐行注释：声明并初始化当前变量。
const distribution = ref([]) // 逐行注释：声明并初始化当前变量。
const investment = ref([]) // 逐行注释：声明并初始化当前变量。
const selectedProvince = ref('') // 逐行注释：声明并初始化当前变量。
const profileDistrictId = ref(null) // 逐行注释：声明并初始化当前变量。
const profile = ref(null) // 逐行注释：声明并初始化当前变量。
let loadingCity = false // 逐行注释：声明并初始化当前变量。

// 函数功能：计算当前挂牌画像对应的区域对象。
const profileDistrict = computed(() => // 逐行注释：声明并初始化当前变量。
  districts.value.find((d) => d.id === profileDistrictId.value), // 逐行注释：继续声明当前列表项或参数项。
) // 逐行注释：结束当前代码块或数据结构。

// 函数功能：从挂牌画像中整理核心统计指标。
const profileStats = computed(() => { // 逐行注释：声明并初始化当前变量。
  const p = profile.value || {} // 逐行注释：声明并初始化当前变量。
  return [ // 逐行注释：返回当前表达式结果。
    { label: '样本套数', value: `${Number(p.property_count || 0).toLocaleString()} 套` }, // 逐行注释：配置当前对象字段。
    { // 逐行注释：执行本行前端逻辑。
      label: '当前均价', // 逐行注释：配置当前对象字段。
      value: p.avg_unit_price ? `${Number(p.avg_unit_price).toLocaleString()} 元/㎡` : '暂无', // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
    { // 逐行注释：执行本行前端逻辑。
      label: '中位单价', // 逐行注释：配置当前对象字段。
      value: p.median_unit_price ? `${Number(p.median_unit_price).toLocaleString()} 元/㎡` : '暂无', // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
    { // 逐行注释：执行本行前端逻辑。
      label: '挂牌时间样本', // 逐行注释：配置当前对象字段。
      value: p.date_count ? `${Number(p.date_count).toLocaleString()} 套` : '暂无', // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
  ] // 逐行注释：结束当前代码块或数据结构。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：整理挂牌画像中的交易属性分布分组。
const profileGroups = computed(() => { // 逐行注释：声明并初始化当前变量。
  const p = profile.value || {} // 逐行注释：声明并初始化当前变量。
  return [ // 逐行注释：返回当前表达式结果。
    { label: '交易权属', items: p.ownership_distribution || [] }, // 逐行注释：配置当前对象字段。
    { label: '产权情况', items: p.property_right_distribution || [] }, // 逐行注释：配置当前对象字段。
    { label: '抵押情况', items: p.mortgage_distribution || [] }, // 逐行注释：配置当前对象字段。
    { label: '税费关键词', items: p.tax_tags || [] }, // 逐行注释：配置当前对象字段。
  ] // 逐行注释：结束当前代码块或数据结构。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：判断挂牌画像是否包含月度挂牌趋势数据。
const hasMonthlyListings = computed(() => // 逐行注释：声明并初始化当前变量。
  Boolean(profile.value?.monthly_listings?.some((item) => item.count)), // 逐行注释：继续声明当前列表项或参数项。
) // 逐行注释：结束当前代码块或数据结构。

// 函数功能：加载当前区域的挂牌画像数据。
async function loadProfile() { // 逐行注释：声明当前函数入口。
  profile.value = profileDistrictId.value ? await getListingProfile(profileDistrictId.value) : null // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：加载当前城市的区域排行、价格分布和投资排行数据。
async function loadCity() { // 逐行注释：声明当前函数入口。
  if (!cityId.value) { // 逐行注释：根据条件判断是否执行分支。
    districts.value = [] // 逐行注释：赋值或更新当前变量/状态。
    distribution.value = [] // 逐行注释：赋值或更新当前变量/状态。
    investment.value = [] // 逐行注释：赋值或更新当前变量/状态。
    profileDistrictId.value = null // 逐行注释：赋值或更新当前变量/状态。
    profile.value = null // 逐行注释：赋值或更新当前变量/状态。
    return // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。
  loadingCity = true // 逐行注释：赋值或更新当前变量/状态。
  try { // 逐行注释：开始执行可能失败的逻辑。
    const [d, dist, inv] = await Promise.all([ // 逐行注释：声明并初始化当前变量。
      getCityDistricts(cityId.value), // 逐行注释：继续声明当前列表项或参数项。
      getPriceDistribution(cityId.value), // 逐行注释：继续声明当前列表项或参数项。
      getInvestmentRanking(cityId.value), // 逐行注释：继续声明当前列表项或参数项。
    ]) // 逐行注释：执行本行前端逻辑。
    districts.value = d // 逐行注释：赋值或更新当前变量/状态。
    distribution.value = dist // 逐行注释：赋值或更新当前变量/状态。
    investment.value = inv // 逐行注释：赋值或更新当前变量/状态。
    profileDistrictId.value = d.find((item) => item.id === profileDistrictId.value)?.id || (d.length ? d[0].id : null) // 逐行注释：执行本行前端逻辑。
    await loadProfile() // 逐行注释：等待异步操作完成。
  } finally { // 逐行注释：执行本行前端逻辑。
    loadingCity = false // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(id) { // 逐行注释：声明当前函数入口。
  if (!id) return // 逐行注释：根据条件判断是否执行分支。
  const city = store.cities.find((c) => c.id === id) // 逐行注释：声明并初始化当前变量。
  selectedProvince.value = city?.province || '' // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

onMounted(async () => { // 逐行注释：注册 Vue 生命周期回调。
  await store.loadCities() // 逐行注释：等待异步操作完成。
  cityId.value = store.currentCityId // 逐行注释：赋值或更新当前变量/状态。
  syncProvinceByCity(cityId.value) // 逐行注释：执行本行前端逻辑。
  await loadCity() // 逐行注释：等待异步操作完成。
}) // 逐行注释：执行本行前端逻辑。

watch(cityId, async (id) => { // 逐行注释：监听响应式数据变化。
  syncProvinceByCity(id) // 逐行注释：执行本行前端逻辑。
  if (id) store.setCity(id) // 逐行注释：根据条件判断是否执行分支。
  await loadCity() // 逐行注释：等待异步操作完成。
}) // 逐行注释：执行本行前端逻辑。

watch(profileDistrictId, () => { // 逐行注释：监听响应式数据变化。
  if (!loadingCity) loadProfile() // 逐行注释：根据条件判断是否执行分支。
}) // 逐行注释：执行本行前端逻辑。
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
.hero { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: flex-start; /* 逐行注释：设置当前样式属性。 */
  justify-content: space-between; /* 逐行注释：设置当前样式属性。 */
  gap: 16px; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 20px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.title { /* 逐行注释：开始当前样式规则块。 */
  margin: 0 0 8px; /* 逐行注释：设置当前样式属性。 */
  font-size: 26px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hero p { /* 逐行注释：开始当前样式规则块。 */
  margin: 0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hero-region { /* 逐行注释：开始当前样式规则块。 */
  flex-shrink: 0; /* 逐行注释：设置当前样式属性。 */
  justify-content: flex-end; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.trend-head { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: space-between; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-stats { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: repeat(4, minmax(0, 1fr)); /* 逐行注释：设置当前样式属性。 */
  gap: 10px; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-stat { /* 逐行注释：开始当前样式规则块。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
  padding: 10px 12px; /* 逐行注释：设置当前样式属性。 */
  border: 1px solid #e2e8f0; /* 逐行注释：设置当前样式属性。 */
  border-radius: 8px; /* 逐行注释：设置当前样式属性。 */
  background: #f8fafc; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-label { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 4px; /* 逐行注释：设置当前样式属性。 */
  color: #64748b; /* 逐行注释：设置当前样式属性。 */
  font-size: 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-value { /* 逐行注释：开始当前样式规则块。 */
  color: #0f172a; /* 逐行注释：设置当前样式属性。 */
  font-size: 15px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
  word-break: break-word; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-groups { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* 逐行注释：设置当前样式属性。 */
  gap: 12px; /* 逐行注释：设置当前样式属性。 */
  margin-top: 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-group { /* 逐行注释：开始当前样式规则块。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
  padding-top: 12px; /* 逐行注释：设置当前样式属性。 */
  border-top: 1px solid #e2e8f0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-group-title { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 8px; /* 逐行注释：设置当前样式属性。 */
  color: #334155; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.profile-tags { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-wrap: wrap; /* 逐行注释：设置当前样式属性。 */
  gap: 6px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.empty-text { /* 逐行注释：开始当前样式规则块。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hint { /* 逐行注释：开始当前样式规则块。 */
  margin: -6px 0 12px; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  line-height: 1.6; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
@media (max-width: 768px) { /* 逐行注释：声明响应式媒体查询规则。 */
  .profile-stats, /* 逐行注释：声明当前样式规则。 */
  .profile-groups { /* 逐行注释：开始当前样式规则块。 */
    grid-template-columns: repeat(2, minmax(0, 1fr)); /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
} /* 逐行注释：结束当前样式规则块。 */
@media (max-width: 520px) { /* 逐行注释：声明响应式媒体查询规则。 */
  .hero, /* 逐行注释：声明当前样式规则。 */
  .trend-head { /* 逐行注释：开始当前样式规则块。 */
    flex-direction: column; /* 逐行注释：设置当前样式属性。 */
    align-items: stretch; /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
  .profile-stats, /* 逐行注释：声明当前样式规则。 */
  .profile-groups { /* 逐行注释：开始当前样式规则块。 */
    grid-template-columns: 1fr; /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
