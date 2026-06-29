<!-- 文件功能：实现房源总览仪表盘，展示统计卡片、3D 地图和多类分析图表。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { getCityDistricts, getOverview, getPriceDistribution } from '@/api'
import CityMap3D from '@/components/CityMap3D.vue'
import RegionSelector from '@/components/RegionSelector.vue'
import StatCard from '@/components/StatCard.vue'
import DistrictRankingChart from '@/components/charts/DistrictRankingChart.vue'
import PriceDistributionChart from '@/components/charts/PriceDistributionChart.vue'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const router = useRouter()

const overview = ref({})
const districts = ref([])
const distribution = ref([])
const selectedProvince = ref('')
const selectedDistrictId = ref(null)

// 函数功能：计算当前选中城市对象。
const currentCity = computed(() => store.cities.find((c) => c.id === store.currentCityId))
// 函数功能：计算当前选中区域对象。
const currentDistrict = computed(() => districts.value.find((d) => d.id === selectedDistrictId.value))
// 函数功能：计算当前图表和地图要展示的区域列表。
const visibleDistricts = computed(() =>
  selectedDistrictId.value
    ? districts.value.filter((d) => d.id === selectedDistrictId.value)
    : districts.value,
)
// 函数功能：格式化数值展示，处理空值和单位。
const fmt = (n) => Number(n || 0).toLocaleString()

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) {
  if (!cityId) return
  const city = store.cities.find((c) => c.id === cityId)
  selectedProvince.value = city?.province || ''
}

// 函数功能：执行 loadCityData 对应的前端交互或数据处理逻辑。
async function loadCityData() {
  const id = store.currentCityId
  if (!id) {
    districts.value = []
    distribution.value = []
    return
  }
  const [d, dist] = await Promise.all([getCityDistricts(id), getPriceDistribution(id)])
  districts.value = d
  distribution.value = dist
  if (selectedDistrictId.value && !d.find((item) => item.id === selectedDistrictId.value)) {
    selectedDistrictId.value = null
  }
}

onMounted(async () => {
  await store.loadCities()
  syncProvinceByCity(store.currentCityId)
  overview.value = await getOverview()
  await loadCityData()
})

watch(
  () => store.currentCityId,
  async (cityId) => {
    syncProvinceByCity(cityId)
    await loadCityData()
  },
)

// 函数功能：处理 3D 地图区域选择并加载对应趋势数据。
function onSelectDistrict(d) {
  router.push({ name: 'explore', query: { city_id: store.currentCityId, district_id: d.id } })
}
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
.hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
.hero h1 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(90deg, #1e3a8a, #2563eb);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero p {
  margin: 0;
  max-width: 640px;
  line-height: 1.6;
}
.hero-region {
  flex-shrink: 0;
  justify-content: flex-end;
}
.stats {
  margin-bottom: 16px;
}
.stats .el-col {
  margin-bottom: 16px;
}
.map-card {
  padding-bottom: 20px;
}
</style>
