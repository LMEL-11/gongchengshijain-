<!-- 文件功能：实现房源探索页面，支持条件筛选、分页列表和详情跳转。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue' // 导入 { onMounted, reactive, ref, watch }，供当前前端模块渲染或交互逻辑使用。
import { useRoute, useRouter } from 'vue-router' // 导入 { useRoute, useRouter }，供当前前端模块渲染或交互逻辑使用。

import { getCityDistricts, getProperties } from '@/api' // 导入 { getCityDistricts, getProperties }，供当前前端模块渲染或交互逻辑使用。
import RegionSelector from '@/components/RegionSelector.vue' // 导入 RegionSelector，供当前前端模块渲染或交互逻辑使用。
import { useAppStore } from '@/store/app' // 导入 { useAppStore }，供当前前端模块渲染或交互逻辑使用。

const store = useAppStore() // 创建 store，用于保存页面状态、计算结果或接口参数。
const route = useRoute() // 创建 route，用于保存页面状态、计算结果或接口参数。
const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。

const districts = ref([]) // 创建 districts，用于保存页面状态、计算结果或接口参数。
const list = ref([]) // 创建 list，用于保存页面状态、计算结果或接口参数。
const total = ref(0) // 创建 total，用于保存页面状态、计算结果或接口参数。
const loading = ref(false) // 创建 loading，用于保存页面状态、计算结果或接口参数。
const selectedProvince = ref('') // 创建 selectedProvince，用于保存页面状态、计算结果或接口参数。
let changingCity = false // 创建 changingCity，用于保存页面状态、计算结果或接口参数。

const filters = reactive({ // 创建 filters，用于保存页面状态、计算结果或接口参数。
  city_id: Number(route.query.city_id) || null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  district_id: Number(route.query.district_id) || null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  rooms: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  keyword: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  sort: 'price_asc', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  min_total_price: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  max_total_price: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  page: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  page_size: 12, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

const roomOptions = [ // 创建 roomOptions，用于保存页面状态、计算结果或接口参数。
  { label: '不限', value: null }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '1 室', value: 1 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '2 室', value: 2 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '3 室', value: 3 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '4 室及以上', value: 4 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
] // 结束当前函数、对象、数组或组件配置块。
const sortOptions = [ // 创建 sortOptions，用于保存页面状态、计算结果或接口参数。
  { label: '总价从低到高', value: 'price_asc' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '总价从高到低', value: 'price_desc' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '面积优先', value: 'area_desc' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { label: '最新发布', value: 'newest' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
] // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts() { // 定义 loadDistricts 函数，处理页面交互、数据加载或状态同步。
  districts.value = filters.city_id ? await getCityDistricts(filters.city_id) : [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() { // 定义 fetchList 函数，处理页面交互、数据加载或状态同步。
  if (!filters.city_id) { // 根据当前页面状态或接口结果决定是否进入该分支。
    list.value = [] // 更新 list.value 响应式状态，让页面展示与最新数据保持一致。
    total.value = 0 // 更新 total.value 响应式状态，让页面展示与最新数据保持一致。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  loading.value = true // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    const params = {} // 创建 params，用于保存页面状态、计算结果或接口参数。
    Object.keys(filters).forEach((k) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
      const v = filters[k] // 创建 v，用于保存页面状态、计算结果或接口参数。
      if (v !== null && v !== '') params[k] = v // 根据当前页面状态或接口结果决定是否进入该分支。
    }) // 结束当前函数、对象、数组或组件配置块。
    const res = await getProperties(params) // 创建 res，用于保存页面状态、计算结果或接口参数。
    list.value = res.items // 更新 list.value 响应式状态，让页面展示与最新数据保持一致。
    total.value = res.total // 更新 total.value 响应式状态，让页面展示与最新数据保持一致。
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loading.value = false // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：应用筛选条件并重新加载房源列表。
function applyFilters() { // 定义 applyFilters 函数，处理页面交互、数据加载或状态同步。
  filters.page = 1 // 设置 filters.page 的值，作为后续渲染、计算或请求的输入。
  fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理分页页码变化并重新加载房源列表。
function onPage(p) { // 定义 onPage 函数，处理页面交互、数据加载或状态同步。
  filters.page = p // 设置 filters.page 的值，作为后续渲染、计算或请求的输入。
  fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：跳转到房源详情页面。
function openDetail(id) { // 定义 openDetail 函数，处理页面交互、数据加载或状态同步。
  router.push({ name: 'property-detail', params: { id } }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) { // 定义 syncProvinceByCity 函数，处理页面交互、数据加载或状态同步。
  if (!cityId) return // 根据当前页面状态或接口结果决定是否进入该分支。
  const city = store.cities.find((c) => c.id === cityId) // 创建 city，用于保存页面状态、计算结果或接口参数。
  selectedProvince.value = city?.province || '' // 更新 selectedProvince.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(async () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  if (!filters.city_id) filters.city_id = store.currentCityId // 根据当前页面状态或接口结果决定是否进入该分支。
  syncProvinceByCity(filters.city_id) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  await loadDistricts() // 等待异步接口或资源加载完成，再继续更新页面状态。
  await fetchList() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => filters.city_id, // 设置  的值，作为后续渲染、计算或请求的输入。
  async (cityId) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    changingCity = true // 设置 changingCity 的值，作为后续渲染、计算或请求的输入。
    filters.page = 1 // 设置 filters.page 的值，作为后续渲染、计算或请求的输入。
    filters.district_id = null // 设置 filters.district_id 的值，作为后续渲染、计算或请求的输入。
    syncProvinceByCity(cityId) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    if (cityId) { // 根据当前页面状态或接口结果决定是否进入该分支。
      store.setCity(cityId) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      await loadDistricts() // 等待异步接口或资源加载完成，再继续更新页面状态。
      await fetchList() // 等待异步接口或资源加载完成，再继续更新页面状态。
    } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
      list.value = [] // 更新 list.value 响应式状态，让页面展示与最新数据保持一致。
      total.value = 0 // 更新 total.value 响应式状态，让页面展示与最新数据保持一致。
    } // 结束当前函数、对象、数组或组件配置块。
    changingCity = false // 设置 changingCity 的值，作为后续渲染、计算或请求的输入。
  }, // 结束当前函数、对象、数组或组件配置块。
) // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => filters.district_id, // 设置  的值，作为后续渲染、计算或请求的输入。
  () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    if (!changingCity) applyFilters() // 根据当前页面状态或接口结果决定是否进入该分支。
  }, // 结束当前函数、对象、数组或组件配置块。
) // 结束当前函数、对象、数组或组件配置块。
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
.filter-bar { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.filters :deep(.el-form-item) { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 8px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.result-meta { /* 定义当前选择器的样式作用域。 */
  margin: 4px 4px 14px; /* 设置元素外边距。 */
} /* 结束当前样式规则块。 */
.prop-card { /* 定义当前选择器的样式作用域。 */
  background: #fff; /* 设置背景样式。 */
  border-radius: var(--card-radius); /* 设置圆角半径。 */
  box-shadow: var(--shadow); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  overflow: hidden; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  cursor: pointer; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
  transition: transform 0.18s, box-shadow 0.18s; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.prop-card:hover { /* 定义当前选择器的样式作用域。 */
  transform: translateY(-4px); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.cover { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  height: 132px; /* 设置元素高度。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  color: rgba(255, 255, 255, 0.9); /* 设置文字颜色。 */
  background: linear-gradient(135deg, #60a5fa, #2563eb); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */
.type-tag { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  top: 10px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: 10px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.prop-body { /* 定义当前选择器的样式作用域。 */
  padding: 14px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */
.prop-title { /* 定义当前选择器的样式作用域。 */
  font-weight: 600; /* 设置文字粗细。 */
  font-size: 15px; /* 设置文字大小。 */
  white-space: nowrap; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  overflow: hidden; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  text-overflow: ellipsis; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.prop-tags { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  gap: 6px; /* 设置子元素之间的间距。 */
  margin: 10px 0; /* 设置元素外边距。 */
  flex-wrap: wrap; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.prop-price { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: baseline; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
} /* 结束当前样式规则块。 */
.total { /* 定义当前选择器的样式作用域。 */
  color: #f5222d; /* 设置文字颜色。 */
  font-weight: 800; /* 设置文字粗细。 */
  font-size: 22px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.total small { /* 定义当前选择器的样式作用域。 */
  font-size: 13px; /* 设置文字大小。 */
  margin-left: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.unit { /* 定义当前选择器的样式作用域。 */
  font-size: 12px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.pager { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  margin-top: 12px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
</style>
