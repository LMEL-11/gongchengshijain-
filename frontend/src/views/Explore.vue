<!-- 文件功能：实现房源探索页面，支持条件筛选、分页列表和详情跳转。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。
import { useRoute, useRouter } from 'vue-router' // 逐行注释：导入本行所需的依赖。

import { getCityDistricts, getProperties } from '@/api' // 逐行注释：导入本行所需的依赖。
import RegionSelector from '@/components/RegionSelector.vue' // 逐行注释：导入本行所需的依赖。
import { useAppStore } from '@/store/app' // 逐行注释：导入本行所需的依赖。

const store = useAppStore() // 逐行注释：声明并初始化当前变量。
const route = useRoute() // 逐行注释：声明并初始化当前变量。
const router = useRouter() // 逐行注释：声明并初始化当前变量。

const districts = ref([]) // 逐行注释：声明并初始化当前变量。
const list = ref([]) // 逐行注释：声明并初始化当前变量。
const total = ref(0) // 逐行注释：声明并初始化当前变量。
const loading = ref(false) // 逐行注释：声明并初始化当前变量。
const selectedProvince = ref('') // 逐行注释：声明并初始化当前变量。
let changingCity = false // 逐行注释：声明并初始化当前变量。

const filters = reactive({ // 逐行注释：声明并初始化当前变量。
  city_id: Number(route.query.city_id) || null, // 逐行注释：配置当前对象字段。
  district_id: Number(route.query.district_id) || null, // 逐行注释：配置当前对象字段。
  rooms: null, // 逐行注释：配置当前对象字段。
  keyword: '', // 逐行注释：配置当前对象字段。
  sort: 'price_asc', // 逐行注释：配置当前对象字段。
  min_total_price: null, // 逐行注释：配置当前对象字段。
  max_total_price: null, // 逐行注释：配置当前对象字段。
  page: 1, // 逐行注释：配置当前对象字段。
  page_size: 12, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。

const roomOptions = [ // 逐行注释：声明并初始化当前变量。
  { label: '不限', value: null }, // 逐行注释：配置当前对象字段。
  { label: '1 室', value: 1 }, // 逐行注释：配置当前对象字段。
  { label: '2 室', value: 2 }, // 逐行注释：配置当前对象字段。
  { label: '3 室', value: 3 }, // 逐行注释：配置当前对象字段。
  { label: '4 室及以上', value: 4 }, // 逐行注释：配置当前对象字段。
] // 逐行注释：结束当前代码块或数据结构。
const sortOptions = [ // 逐行注释：声明并初始化当前变量。
  { label: '总价从低到高', value: 'price_asc' }, // 逐行注释：配置当前对象字段。
  { label: '总价从高到低', value: 'price_desc' }, // 逐行注释：配置当前对象字段。
  { label: '面积优先', value: 'area_desc' }, // 逐行注释：配置当前对象字段。
  { label: '最新发布', value: 'newest' }, // 逐行注释：配置当前对象字段。
] // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts() { // 逐行注释：声明当前函数入口。
  districts.value = filters.city_id ? await getCityDistricts(filters.city_id) : [] // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() { // 逐行注释：声明当前函数入口。
  if (!filters.city_id) { // 逐行注释：根据条件判断是否执行分支。
    list.value = [] // 逐行注释：赋值或更新当前变量/状态。
    total.value = 0 // 逐行注释：赋值或更新当前变量/状态。
    return // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。
  loading.value = true // 逐行注释：赋值或更新当前变量/状态。
  try { // 逐行注释：开始执行可能失败的逻辑。
    const params = {} // 逐行注释：声明并初始化当前变量。
    Object.keys(filters).forEach((k) => { // 逐行注释：执行本行前端逻辑。
      const v = filters[k] // 逐行注释：声明并初始化当前变量。
      if (v !== null && v !== '') params[k] = v // 逐行注释：根据条件判断是否执行分支。
    }) // 逐行注释：执行本行前端逻辑。
    const res = await getProperties(params) // 逐行注释：声明并初始化当前变量。
    list.value = res.items // 逐行注释：赋值或更新当前变量/状态。
    total.value = res.total // 逐行注释：赋值或更新当前变量/状态。
  } finally { // 逐行注释：执行本行前端逻辑。
    loading.value = false // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：应用筛选条件并重新加载房源列表。
function applyFilters() { // 逐行注释：声明当前函数入口。
  filters.page = 1 // 逐行注释：赋值或更新当前变量/状态。
  fetchList() // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理分页页码变化并重新加载房源列表。
function onPage(p) { // 逐行注释：声明当前函数入口。
  filters.page = p // 逐行注释：赋值或更新当前变量/状态。
  fetchList() // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：跳转到房源详情页面。
function openDetail(id) { // 逐行注释：声明当前函数入口。
  router.push({ name: 'property-detail', params: { id } }) // 逐行注释：执行路由跳转或路由操作。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) { // 逐行注释：声明当前函数入口。
  if (!cityId) return // 逐行注释：根据条件判断是否执行分支。
  const city = store.cities.find((c) => c.id === cityId) // 逐行注释：声明并初始化当前变量。
  selectedProvince.value = city?.province || '' // 逐行注释：赋值或更新当前变量/状态。
} // 逐行注释：结束当前代码块或数据结构。

onMounted(async () => { // 逐行注释：注册 Vue 生命周期回调。
  await store.loadCities() // 逐行注释：等待异步操作完成。
  if (!filters.city_id) filters.city_id = store.currentCityId // 逐行注释：根据条件判断是否执行分支。
  syncProvinceByCity(filters.city_id) // 逐行注释：执行本行前端逻辑。
  await loadDistricts() // 逐行注释：等待异步操作完成。
  await fetchList() // 逐行注释：等待异步操作完成。
}) // 逐行注释：执行本行前端逻辑。

watch( // 逐行注释：监听响应式数据变化。
  () => filters.city_id, // 逐行注释：继续声明当前列表项或参数项。
  async (cityId) => { // 逐行注释：执行本行前端逻辑。
    changingCity = true // 逐行注释：赋值或更新当前变量/状态。
    filters.page = 1 // 逐行注释：赋值或更新当前变量/状态。
    filters.district_id = null // 逐行注释：赋值或更新当前变量/状态。
    syncProvinceByCity(cityId) // 逐行注释：执行本行前端逻辑。
    if (cityId) { // 逐行注释：根据条件判断是否执行分支。
      store.setCity(cityId) // 逐行注释：执行本行前端逻辑。
      await loadDistricts() // 逐行注释：等待异步操作完成。
      await fetchList() // 逐行注释：等待异步操作完成。
    } else { // 逐行注释：执行本行前端逻辑。
      districts.value = [] // 逐行注释：赋值或更新当前变量/状态。
      list.value = [] // 逐行注释：赋值或更新当前变量/状态。
      total.value = 0 // 逐行注释：赋值或更新当前变量/状态。
    } // 逐行注释：结束当前代码块或数据结构。
    changingCity = false // 逐行注释：赋值或更新当前变量/状态。
  }, // 逐行注释：结束当前代码块或数据结构。
) // 逐行注释：结束当前代码块或数据结构。

watch( // 逐行注释：监听响应式数据变化。
  () => filters.district_id, // 逐行注释：继续声明当前列表项或参数项。
  () => { // 逐行注释：执行本行前端逻辑。
    if (!changingCity) applyFilters() // 逐行注释：根据条件判断是否执行分支。
  }, // 逐行注释：结束当前代码块或数据结构。
) // 逐行注释：结束当前代码块或数据结构。
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
.filter-bar { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.filters :deep(.el-form-item) { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 8px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.result-meta { /* 逐行注释：开始当前样式规则块。 */
  margin: 4px 4px 14px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-card { /* 逐行注释：开始当前样式规则块。 */
  background: #fff; /* 逐行注释：设置当前样式属性。 */
  border-radius: var(--card-radius); /* 逐行注释：设置当前样式属性。 */
  box-shadow: var(--shadow); /* 逐行注释：设置当前样式属性。 */
  overflow: hidden; /* 逐行注释：设置当前样式属性。 */
  cursor: pointer; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
  transition: transform 0.18s, box-shadow 0.18s; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-card:hover { /* 逐行注释：开始当前样式规则块。 */
  transform: translateY(-4px); /* 逐行注释：设置当前样式属性。 */
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.cover { /* 逐行注释：开始当前样式规则块。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
  height: 132px; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  color: rgba(255, 255, 255, 0.9); /* 逐行注释：设置当前样式属性。 */
  background: linear-gradient(135deg, #60a5fa, #2563eb); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.type-tag { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  top: 10px; /* 逐行注释：设置当前样式属性。 */
  left: 10px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-body { /* 逐行注释：开始当前样式规则块。 */
  padding: 14px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-title { /* 逐行注释：开始当前样式规则块。 */
  font-weight: 600; /* 逐行注释：设置当前样式属性。 */
  font-size: 15px; /* 逐行注释：设置当前样式属性。 */
  white-space: nowrap; /* 逐行注释：设置当前样式属性。 */
  overflow: hidden; /* 逐行注释：设置当前样式属性。 */
  text-overflow: ellipsis; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-tags { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  gap: 6px; /* 逐行注释：设置当前样式属性。 */
  margin: 10px 0; /* 逐行注释：设置当前样式属性。 */
  flex-wrap: wrap; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.prop-price { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: baseline; /* 逐行注释：设置当前样式属性。 */
  justify-content: space-between; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.total { /* 逐行注释：开始当前样式规则块。 */
  color: #f5222d; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  font-size: 22px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.total small { /* 逐行注释：开始当前样式规则块。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  margin-left: 2px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.unit { /* 逐行注释：开始当前样式规则块。 */
  font-size: 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.pager { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  margin-top: 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
