<!-- 文件功能：实现房源探索页面，支持条件筛选、分页列表和详情跳转。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRoute, useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { getCityDistricts, getProperties } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import RegionSelector from '@/components/RegionSelector.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAppStore } from '@/store/app' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const store = useAppStore() // 保存store相关业务数据，作为后续计算、渲染或请求的输入。
const route = useRoute() // 保存route相关业务数据，作为后续计算、渲染或请求的输入。
const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。

const districts = ref([]) // 创建行政区集合，用于驱动页面渲染、表单输入或接口参数。
const list = ref([]) // 创建list响应式状态，用于驱动页面渲染、表单输入或接口参数。
const total = ref(0) // 创建总数统计，用于驱动页面渲染、表单输入或接口参数。
const loading = ref(false) // 创建加载状态，用于驱动页面渲染、表单输入或接口参数。
const selectedProvince = ref('') // 创建selectedProvince响应式状态，用于驱动页面渲染、表单输入或接口参数。
let changingCity = false // 保存changingCity相关业务数据，作为后续计算、渲染或请求的输入。

const filters = reactive({ // 创建filters响应式状态，用于驱动页面渲染、表单输入或接口参数。
  city_id: Number(route.query.city_id) || null, // 声明city_id字段，作为组件配置、请求参数或图表数据的一部分。
  district_id: Number(route.query.district_id) || null, // 声明district_id字段，作为组件配置、请求参数或图表数据的一部分。
  rooms: null, // 声明rooms字段，作为组件配置、请求参数或图表数据的一部分。
  keyword: '', // 声明keyword字段，作为组件配置、请求参数或图表数据的一部分。
  sort: 'price_asc', // 声明sort字段，作为组件配置、请求参数或图表数据的一部分。
  min_total_price: null, // 声明min_total_price字段，作为组件配置、请求参数或图表数据的一部分。
  max_total_price: null, // 声明max_total_price字段，作为组件配置、请求参数或图表数据的一部分。
  page: 1, // 声明page字段，作为组件配置、请求参数或图表数据的一部分。
  page_size: 12, // 声明page_size字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

const roomOptions = [ // 保存roomOptions相关业务数据，作为后续计算、渲染或请求的输入。
  { label: '不限', value: null }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '1 室', value: 1 }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '2 室', value: 2 }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '3 室', value: 3 }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '4 室及以上', value: 4 }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
] // 完成当前参数、配置或响应式数据结构的组装。
const sortOptions = [ // 保存sortOptions相关业务数据，作为后续计算、渲染或请求的输入。
  { label: '总价从低到高', value: 'price_asc' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '总价从高到低', value: 'price_desc' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '面积优先', value: 'area_desc' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { label: '最新发布', value: 'newest' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
] // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  districts.value = filters.city_id ? await getCityDistricts(filters.city_id) : [] // 等待异步接口或资源加载完成，再继续更新页面状态。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!filters.city_id) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    list.value = [] // 更新list.value对应的页面状态，使界面展示与最新业务数据一致。
    total.value = 0 // 更新total.value对应的页面状态，使界面展示与最新业务数据一致。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  loading.value = true // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    const params = {} // 保存params相关业务数据，作为后续计算、渲染或请求的输入。
    Object.keys(filters).forEach((k) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      const v = filters[k] // 保存v相关业务数据，作为后续计算、渲染或请求的输入。
      if (v !== null && v !== '') params[k] = v // 根据当前状态、接口结果或用户输入选择对应交互路径。
    }) // 完成当前参数、配置或响应式数据结构的组装。
    const res = await getProperties(params) // 保存res相关业务数据，作为后续计算、渲染或请求的输入。
    list.value = res.items // 更新list.value对应的页面状态，使界面展示与最新业务数据一致。
    total.value = res.total // 更新total.value对应的页面状态，使界面展示与最新业务数据一致。
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loading.value = false // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：应用筛选条件并重新加载房源列表。
function applyFilters() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  filters.page = 1 // 更新filters.page对应的页面状态，使界面展示与最新业务数据一致。
  fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理分页页码变化并重新加载房源列表。
function onPage(p) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  filters.page = p // 更新filters.page对应的页面状态，使界面展示与最新业务数据一致。
  fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：跳转到房源详情页面。
function openDetail(id) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  router.push({ name: 'property-detail', params: { id } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据当前城市编号同步选中的省份。
function syncProvinceByCity(cityId) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!cityId) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const city = store.cities.find((c) => c.id === cityId) // 保存city相关业务数据，作为后续计算、渲染或请求的输入。
  selectedProvince.value = city?.province || '' // 更新selectedProvince.value对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(async () => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  if (!filters.city_id) filters.city_id = store.currentCityId // 根据当前状态、接口结果或用户输入选择对应交互路径。
  syncProvinceByCity(filters.city_id) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  await loadDistricts() // 等待异步接口或资源加载完成，再继续更新页面状态。
  await fetchList() // 等待异步接口或资源加载完成，再继续更新页面状态。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => filters.city_id, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  async (cityId) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    changingCity = true // 更新changingCity对应的页面状态，使界面展示与最新业务数据一致。
    filters.page = 1 // 更新filters.page对应的页面状态，使界面展示与最新业务数据一致。
    filters.district_id = null // 更新filters.district_id对应的页面状态，使界面展示与最新业务数据一致。
    syncProvinceByCity(cityId) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    if (cityId) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      store.setCity(cityId) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      await loadDistricts() // 等待异步接口或资源加载完成，再继续更新页面状态。
      await fetchList() // 等待异步接口或资源加载完成，再继续更新页面状态。
    } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
      list.value = [] // 更新list.value对应的页面状态，使界面展示与最新业务数据一致。
      total.value = 0 // 更新total.value对应的页面状态，使界面展示与最新业务数据一致。
    } // 完成当前参数、配置或响应式数据结构的组装。
    changingCity = false // 更新changingCity对应的页面状态，使界面展示与最新业务数据一致。
  }, // 完成当前参数、配置或响应式数据结构的组装。
) // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => filters.district_id, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  () => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    if (!changingCity) applyFilters() // 根据当前状态、接口结果或用户输入选择对应交互路径。
  }, // 完成当前参数、配置或响应式数据结构的组装。
) // 完成当前参数、配置或响应式数据结构的组装。
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
.filter-bar { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.filters :deep(.el-form-item) { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 8px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.result-meta { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 4px 4px 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-card { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: var(--card-radius); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  box-shadow: var(--shadow); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  overflow: hidden; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  cursor: pointer; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  transition: transform 0.18s, box-shadow 0.18s; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-card:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  transform: translateY(-4px); /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.cover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: relative; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  height: 132px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  color: rgba(255, 255, 255, 0.9); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: linear-gradient(135deg, #60a5fa, #2563eb); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.type-tag { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  position: absolute; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  top: 10px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  left: 10px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-body { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  padding: 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-weight: 600; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  white-space: nowrap; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  overflow: hidden; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  text-overflow: ellipsis; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-tags { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin: 10px 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  flex-wrap: wrap; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.prop-price { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: baseline; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.total { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: #f5222d; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-size: 22px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.total small { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin-left: 2px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.unit { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.pager { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  margin-top: 12px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
