<script setup>
import { computed, onMounted, ref, watch } from 'vue'

import { getCityDistricts, getInvestmentRanking, getListingProfile, getPriceDistribution } from '@/api'
import PredictionForm from '@/components/PredictionForm.vue'
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue'
import InvestmentChart from '@/components/charts/InvestmentChart.vue'
import ListingProfileChart from '@/components/charts/ListingProfileChart.vue'
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const cityId = ref(null)
const districts = ref([])
const distribution = ref([])
const investment = ref([])
const profileDistrictId = ref(null)
const profile = ref(null)

const profileStats = computed(() => {
  const p = profile.value || {}
  return [
    { label: '样本套数', value: `${Number(p.property_count || 0).toLocaleString()} 套` },
    {
      label: '当前均价',
      value: p.avg_unit_price ? `${Number(p.avg_unit_price).toLocaleString()} 元/㎡` : '暂无',
    },
    {
      label: '中位单价',
      value: p.median_unit_price ? `${Number(p.median_unit_price).toLocaleString()} 元/㎡` : '暂无',
    },
    {
      label: '挂牌时间样本',
      value: p.date_count ? `${Number(p.date_count).toLocaleString()} 套` : '暂无',
    },
  ]
})

const profileGroups = computed(() => {
  const p = profile.value || {}
  return [
    { label: '交易权属', items: p.ownership_distribution || [] },
    { label: '产权情况', items: p.property_right_distribution || [] },
    { label: '抵押情况', items: p.mortgage_distribution || [] },
    { label: '税费关键词', items: p.tax_tags || [] },
  ]
})

const hasMonthlyListings = computed(() =>
  Boolean(profile.value?.monthly_listings?.some((item) => item.count)),
)

async function loadProfile() {
  profile.value = profileDistrictId.value ? await getListingProfile(profileDistrictId.value) : null
}

async function loadCity() {
  const [d, dist, inv] = await Promise.all([
    getCityDistricts(cityId.value),
    getPriceDistribution(cityId.value),
    getInvestmentRanking(cityId.value),
  ])
  districts.value = d
  distribution.value = dist
  investment.value = inv
  profileDistrictId.value = d.length ? d[0].id : null
  await loadProfile()
}

onMounted(async () => {
  await store.loadCities()
  cityId.value = store.currentCityId
  await loadCity()
})

watch(cityId, loadCity)
</script>

<template>
  <div class="page">
    <div class="hero">
      <div>
        <h1 class="title">数据分析与房价预测</h1>
        <p class="muted">多维度剖析区域房价水平、分布与挂牌画像，并基于机器学习模型预测房源价格</p>
      </div>
      <el-select v-model="cityId" size="large" style="width: 160px">
        <el-option v-for="c in store.cities" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
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
            <el-select v-model="profileDistrictId" size="small" style="width: 130px" @change="loadProfile">
              <el-option v-for="d in districts" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
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
.hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}
.title {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 800;
}
.hero p {
  margin: 0;
}
.trend-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.profile-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.profile-stat {
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}
.profile-label {
  margin-bottom: 4px;
  color: #64748b;
  font-size: 12px;
}
.profile-value {
  color: #0f172a;
  font-size: 15px;
  font-weight: 700;
  word-break: break-word;
}
.profile-groups {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}
.profile-group {
  min-width: 0;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}
.profile-group-title {
  margin-bottom: 8px;
  color: #334155;
  font-size: 13px;
  font-weight: 700;
}
.profile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.empty-text {
  font-size: 13px;
}
.hint {
  margin: -6px 0 12px;
  font-size: 13px;
  line-height: 1.6;
}
@media (max-width: 768px) {
  .profile-stats,
  .profile-groups {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 520px) {
  .hero,
  .trend-head {
    flex-direction: column;
    align-items: stretch;
  }
  .profile-stats,
  .profile-groups {
    grid-template-columns: 1fr;
  }
}
</style>
