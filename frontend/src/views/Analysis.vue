<script setup>
import { onMounted, ref, watch } from 'vue'

import { getCityDistricts, getInvestmentRanking, getPriceDistribution, getPriceTrend } from '@/api'
import PredictionForm from '@/components/PredictionForm.vue'
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue'
import InvestmentChart from '@/components/charts/InvestmentChart.vue'
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue'
import PriceTrendChart from '@/components/charts/PriceTrendChart.vue'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const cityId = ref(null)
const districts = ref([])
const distribution = ref([])
const investment = ref([])
const trendDistrictId = ref(null)
const trend = ref([])

async function loadTrend() {
  trend.value = trendDistrictId.value ? await getPriceTrend(trendDistrictId.value) : []
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
  trendDistrictId.value = d.length ? d[0].id : null
  await loadTrend()
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
        <p class="muted">多维度剖析区域房价水平、分布与走势，并基于机器学习模型预测房源价格</p>
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
            <div class="section-title" style="margin: 0">房价走势（近 24 个月）</div>
            <el-select v-model="trendDistrictId" size="small" style="width: 130px" @change="loadTrend">
              <el-option v-for="d in districts" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
          </div>
          <PriceTrendChart v-if="trend.length" :data="trend" height="320px" />
          <el-empty
            v-else
            description="真实房源为当前快照，暂无历史月度走势数据"
            :image-size="72"
            style="height: 320px"
          />
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
.hint {
  margin: -6px 0 12px;
  font-size: 13px;
  line-height: 1.6;
}
</style>
