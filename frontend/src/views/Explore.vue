<!-- 文件功能：实现房源探索页面，支持条件筛选、分页列表和详情跳转。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getCityDistricts, getProperties } from '@/api'
import RegionSelector from '@/components/RegionSelector.vue'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const route = useRoute()
const router = useRouter()

const districts = ref([])
const list = ref([])
const total = ref(0)
const loading = ref(false)
const selectedProvince = ref('')
let changingCity = false

const filters = reactive({
  city_id: Number(route.query.city_id) || null,
  district_id: Number(route.query.district_id) || null,
  rooms: null,
  keyword: '',
  sort: 'price_asc',
  min_total_price: null,
  max_total_price: null,
  page: 1,
  page_size: 12,
})

const roomOptions = [
  { label: '不限', value: null },
  { label: '1 室', value: 1 },
  { label: '2 室', value: 2 },
  { label: '3 室', value: 3 },
  { label: '4 室及以上', value: 4 },
]
const sortOptions = [
  { label: '总价从低到高', value: 'price_asc' },
  { label: '总价从高到低', value: 'price_desc' },
  { label: '面积优先', value: 'area_desc' },
  { label: '最新发布', value: 'newest' },
]

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts() {
  districts.value = filters.city_id ? await getCityDistricts(filters.city_id) : []
}

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() {
  if (!filters.city_id) {
    list.value = []
    total.value = 0
    return
  }
  loading.value = true
  try {
    const params = {}
    Object.keys(filters).forEach((k) => {
      const v = filters[k]
      if (v !== null && v !== '') params[k] = v
    })
    const res = await getProperties(params)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

// 函数功能：应用筛选条件并重新加载房源列表。
function applyFilters() {
  filters.page = 1
  fetchList()
}

// 函数功能：处理分页页码变化并重新加载房源列表。
function onPage(p) {
  filters.page = p
  fetchList()
}

// 函数功能：跳转到房源详情页面。
function openDetail(id) {
  router.push({ name: 'property-detail', params: { id } })
}

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) {
  if (!cityId) return
  const city = store.cities.find((c) => c.id === cityId)
  selectedProvince.value = city?.province || ''
}

onMounted(async () => {
  await store.loadCities()
  if (!filters.city_id) filters.city_id = store.currentCityId
  syncProvinceByCity(filters.city_id)
  await loadDistricts()
  await fetchList()
})

watch(
  () => filters.city_id,
  async (cityId) => {
    changingCity = true
    filters.page = 1
    filters.district_id = null
    syncProvinceByCity(cityId)
    if (cityId) {
      store.setCity(cityId)
      await loadDistricts()
      await fetchList()
    } else {
      districts.value = []
      list.value = []
      total.value = 0
    }
    changingCity = false
  },
)

watch(
  () => filters.district_id,
  () => {
    if (!changingCity) applyFilters()
  },
)
</script>

<template>
  <div class="page">
    <div class="card filter-bar">
      <el-form :inline="true" class="filters">
        <el-form-item label="区域">
          <RegionSelector
            v-model:province="selectedProvince"
            v-model:city-id="filters.city_id"
            v-model:district-id="filters.district_id"
            :cities="store.cities"
            :districts="districts"
          />
        </el-form-item>
        <el-form-item label="户型">
          <el-select v-model="filters.rooms" style="width: 120px" @change="applyFilters">
            <el-option v-for="o in roomOptions" :key="o.label" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="总价">
          <el-input-number v-model="filters.min_total_price" :min="0" :controls="false" placeholder="最低" style="width: 90px" @change="applyFilters" />
          <span style="margin: 0 6px">—</span>
          <el-input-number v-model="filters.max_total_price" :min="0" :controls="false" placeholder="最高" style="width: 90px" @change="applyFilters" />
          <span style="margin-left: 6px" class="muted">万元</span>
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="filters.sort" style="width: 140px" @change="applyFilters">
            <el-option v-for="o in sortOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input v-model="filters.keyword" placeholder="关键词，如 学区 / 地铁" clearable style="width: 200px" @keyup.enter="applyFilters">
            <template #append>
              <el-button :icon="'Search'" @click="applyFilters" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </div>

    <div class="result-meta muted">共找到 <b>{{ total }}</b> 套房源</div>

    <el-row v-loading="loading" :gutter="16">
      <el-col v-for="p in list" :key="p.id" :xs="24" :sm="12" :md="8" :lg="6">
        <div class="prop-card" @click="openDetail(p.id)">
          <div class="cover">
            <el-tag size="small" effect="dark" class="type-tag">{{ p.listing_type }}</el-tag>
            <el-icon :size="44"><House /></el-icon>
          </div>
          <div class="prop-body">
            <div class="prop-title">{{ p.title }}</div>
            <div class="prop-tags">
              <el-tag size="small" type="info">{{ p.city_name }}·{{ p.district_name }}</el-tag>
              <el-tag size="small" type="info">{{ p.layout }}</el-tag>
              <el-tag size="small" type="info">{{ p.area }}㎡</el-tag>
            </div>
            <div class="prop-price">
              <span class="total">{{ p.total_price }}<small>万</small></span>
              <span class="unit muted">{{ p.unit_price?.toLocaleString() }} 元/㎡</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && !list.length" description="没有符合条件的房源" />

    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next, total"
        :total="total"
        :page-size="filters.page_size"
        :current-page="filters.page"
        @current-change="onPage"
      />
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
}
.filters :deep(.el-form-item) {
  margin-bottom: 8px;
}
.result-meta {
  margin: 4px 4px 14px;
}
.prop-card {
  background: #fff;
  border-radius: var(--card-radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  cursor: pointer;
  margin-bottom: 16px;
  transition: transform 0.18s, box-shadow 0.18s;
}
.prop-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
}
.cover {
  position: relative;
  height: 132px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.9);
  background: linear-gradient(135deg, #60a5fa, #2563eb);
}
.type-tag {
  position: absolute;
  top: 10px;
  left: 10px;
}
.prop-body {
  padding: 14px;
}
.prop-title {
  font-weight: 600;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.prop-tags {
  display: flex;
  gap: 6px;
  margin: 10px 0;
  flex-wrap: wrap;
}
.prop-price {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.total {
  color: #f5222d;
  font-weight: 800;
  font-size: 22px;
}
.total small {
  font-size: 13px;
  margin-left: 2px;
}
.unit {
  font-size: 12px;
}
.pager {
  display: flex;
  justify-content: center;
  margin-top: 12px;
}
</style>
