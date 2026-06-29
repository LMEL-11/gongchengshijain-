<!-- 文件功能：实现数据分析与预测页面，加载城市分析、挂牌画像和预测表单。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { getCityDistricts, getInvestmentRanking, getListingProfile, getPriceDistribution } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import PredictionForm from '@/components/PredictionForm.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import RegionSelector from '@/components/RegionSelector.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import InvestmentChart from '@/components/charts/InvestmentChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import ListingProfileChart from '@/components/charts/ListingProfileChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAppStore } from '@/store/app' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const store = useAppStore() // 保存store相关业务数据，作为后续计算、渲染或请求的输入。
const cityId = ref(null) // 创建cityId响应式状态，用于驱动页面渲染、表单输入或接口参数。
const districts = ref([]) // 创建行政区集合，用于驱动页面渲染、表单输入或接口参数。
const distribution = ref([]) // 创建distribution响应式状态，用于驱动页面渲染、表单输入或接口参数。
const investment = ref([]) // 创建investment响应式状态，用于驱动页面渲染、表单输入或接口参数。
const selectedProvince = ref('') // 创建selectedProvince响应式状态，用于驱动页面渲染、表单输入或接口参数。
const profileDistrictId = ref(null) // 创建profileDistrictId响应式状态，用于驱动页面渲染、表单输入或接口参数。
const profile = ref(null) // 创建profile响应式状态，用于驱动页面渲染、表单输入或接口参数。
let loadingCity = false // 保存loadingCity相关业务数据，作为后续计算、渲染或请求的输入。

// 函数功能：计算当前挂牌画像对应的区域对象。
const profileDistrict = computed(() => // 基于响应式数据派生profileDistrict，用于保持界面展示与数据状态同步。
  districts.value.find((d) => d.id === profileDistrictId.value), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：从挂牌画像中整理核心统计指标。
const profileStats = computed(() => { // 基于响应式数据派生profileStats，用于保持界面展示与数据状态同步。
  const p = profile.value || {} // 保存p相关业务数据，作为后续计算、渲染或请求的输入。
  return [ // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    { label: '样本套数', value: `${Number(p.property_count || 0).toLocaleString()} 套` }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      label: '当前均价', // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
      value: p.avg_unit_price ? `${Number(p.avg_unit_price).toLocaleString()} 元/㎡` : '暂无', // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      label: '中位单价', // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
      value: p.median_unit_price ? `${Number(p.median_unit_price).toLocaleString()} 元/㎡` : '暂无', // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      label: '挂牌时间样本', // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
      value: p.date_count ? `${Number(p.date_count).toLocaleString()} 套` : '暂无', // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  ] // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：整理挂牌画像中的交易属性分布分组。
const profileGroups = computed(() => { // 基于响应式数据派生profileGroups，用于保持界面展示与数据状态同步。
  const p = profile.value || {} // 保存p相关业务数据，作为后续计算、渲染或请求的输入。
  return [ // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    { label: '交易权属', items: p.ownership_distribution || [] }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '产权情况', items: p.property_right_distribution || [] }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '抵押情况', items: p.mortgage_distribution || [] }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '税费关键词', items: p.tax_tags || [] }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ] // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：判断挂牌画像是否包含月度挂牌趋势数据。
const hasMonthlyListings = computed(() => // 基于响应式数据派生hasMonthlyListings，用于保持界面展示与数据状态同步。
  Boolean(profile.value?.monthly_listings?.some((item) => item.count)), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：加载当前区域的挂牌画像数据。
async function loadProfile() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  profile.value = profileDistrictId.value ? await getListingProfile(profileDistrictId.value) : null // 等待异步接口或资源加载完成，再继续更新页面状态。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：加载当前城市的区域排行、价格分布和投资排行数据。
async function loadCity() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!cityId.value) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
    distribution.value = [] // 更新distribution.value对应的页面状态，使界面展示与最新业务数据一致。
    investment.value = [] // 更新investment.value对应的页面状态，使界面展示与最新业务数据一致。
    profileDistrictId.value = null // 更新profileDistrictId.value对应的页面状态，使界面展示与最新业务数据一致。
    profile.value = null // 更新profile.value对应的页面状态，使界面展示与最新业务数据一致。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  loadingCity = true // 更新loadingCity对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    const [d, dist, inv] = await Promise.all([ // 保存[d相关业务数据，作为后续计算、渲染或请求的输入。
      getCityDistricts(cityId.value), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      getPriceDistribution(cityId.value), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      getInvestmentRanking(cityId.value), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    ]) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    districts.value = d // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
    distribution.value = dist // 更新distribution.value对应的页面状态，使界面展示与最新业务数据一致。
    investment.value = inv // 更新investment.value对应的页面状态，使界面展示与最新业务数据一致。
    profileDistrictId.value = d.find((item) => item.id === profileDistrictId.value)?.id || (d.length ? d[0].id : null) // 更新profileDistrictId.value对应的页面状态，使界面展示与最新业务数据一致。
    await loadProfile() // 等待异步接口或资源加载完成，再继续更新页面状态。
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loadingCity = false // 更新loadingCity对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(id) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!id) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const city = store.cities.find((c) => c.id === id) // 保存city相关业务数据，作为后续计算、渲染或请求的输入。
  selectedProvince.value = city?.province || '' // 更新selectedProvince.value对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(async () => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  cityId.value = store.currentCityId // 更新cityId.value对应的页面状态，使界面展示与最新业务数据一致。
  syncProvinceByCity(cityId.value) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  await loadCity() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch(cityId, async (id) => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  syncProvinceByCity(id) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  if (id) store.setCity(id) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  await loadCity() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch(profileDistrictId, () => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  if (!loadingCity) loadProfile() // 根据当前状态、接口结果或用户输入选择对应交互路径。
}) // 完成当前参数、配置或响应式数据结构的组装。
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
.hero { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: flex-start; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin-bottom: 20px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0 0 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 26px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hero p { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hero-region { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex-shrink: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  justify-content: flex-end; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.trend-head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-stats { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: repeat(4, minmax(0, 1fr)); /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin-bottom: 12px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-stat { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  padding: 10px 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border: 1px solid #e2e8f0; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: 8px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: #f8fafc; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-label { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #64748b; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-value { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #0f172a; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  word-break: break-word; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-groups { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin-top: 12px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-group { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  padding-top: 12px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  border-top: 1px solid #e2e8f0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-group-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 8px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #334155; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.profile-tags { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-wrap: wrap; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.empty-text { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.hint { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: -6px 0 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  line-height: 1.6; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
@media (max-width: 768px) { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  .profile-stats, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  .profile-groups { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    grid-template-columns: repeat(2, minmax(0, 1fr)); /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
} /* 收束该样式块，使后续选择器保持独立。 */
@media (max-width: 520px) { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  .hero, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  .trend-head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
    align-items: stretch; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
  .profile-stats, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  .profile-groups { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    grid-template-columns: 1fr; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
