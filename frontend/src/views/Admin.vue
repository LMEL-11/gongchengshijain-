<!-- 文件功能：实现管理员房源管理页面，支持筛选、分页、新增、编辑、详情和删除。 -->
<script setup>
import { reactive, ref, onMounted, computed, watch, nextTick } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { ElMessage, ElMessageBox } from 'element-plus' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
  adminGetProperties, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  adminCreateProperty, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  adminUpdateProperty, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  adminDeleteProperty, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  getCities, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  getCityDistricts, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} from '@/api' // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。

// ---------- 列表 ----------
const list = ref([]) // 创建list响应式状态，用于驱动页面渲染、表单输入或接口参数。
const total = ref(0) // 创建总数统计，用于驱动页面渲染、表单输入或接口参数。
const page = ref(1) // 创建当前页码，用于驱动页面渲染、表单输入或接口参数。
const pageSize = ref(20) // 创建pageSize响应式状态，用于驱动页面渲染、表单输入或接口参数。
const keyword = ref('') // 创建搜索关键词，用于驱动页面渲染、表单输入或接口参数。
const loading = ref(false) // 创建加载状态，用于驱动页面渲染、表单输入或接口参数。

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  loading.value = true // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    // 后台列表筛选参数和分页参数全部交给后端处理，前端只维护当前查询状态。
    const res = await adminGetProperties({ // 保存res相关业务数据，作为后续计算、渲染或请求的输入。
      page: page.value, // 声明page字段，作为组件配置、请求参数或图表数据的一部分。
      page_size: pageSize.value, // 声明page_size字段，作为组件配置、请求参数或图表数据的一部分。
      keyword: keyword.value || undefined, // 声明keyword字段，作为组件配置、请求参数或图表数据的一部分。
      district_id: filterDistrictId.value || undefined, // 声明district_id字段，作为组件配置、请求参数或图表数据的一部分。
    }) // 完成当前参数、配置或响应式数据结构的组装。
    list.value = res.items // 更新list.value对应的页面状态，使界面展示与最新业务数据一致。
    total.value = res.total // 更新total.value对应的页面状态，使界面展示与最新业务数据一致。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    // handled by interceptor
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loading.value = false // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：重置到第一页并执行关键词搜索。
function handleSearch() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  page.value = 1 // 更新page.value对应的页面状态，使界面展示与最新业务数据一致。
  fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理分页大小变化并重新加载列表。
function handleSizeChange(size) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  pageSize.value = size // 更新pageSize.value对应的页面状态，使界面展示与最新业务数据一致。
  page.value = 1 // 更新page.value对应的页面状态，使界面展示与最新业务数据一致。
  fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  loadAllCities() // 预加载城市数据，让省市区选择器立即可用
}) // 完成当前参数、配置或响应式数据结构的组装。

// ---------- 省市区级联数据 ----------
const allCities = ref([])      // 所有城市（含 province 字段）
const selectedProvince = ref('') // 创建selectedProvince响应式状态，用于驱动页面渲染、表单输入或接口参数。
const selectedCityId = ref(null) // 创建selectedCityId响应式状态，用于驱动页面渲染、表单输入或接口参数。
const districts = ref([])      // 当前城市下的区

// 省份列表从城市数据中计算
// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 基于响应式数据派生provinces，用于保持界面展示与数据状态同步。
  const seen = new Set() // 保存seen相关业务数据，作为后续计算、渲染或请求的输入。
  const result = [] // 保存result相关业务数据，作为后续计算、渲染或请求的输入。
  for (const c of allCities.value) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    const p = c.province || '其他' // 保存p相关业务数据，作为后续计算、渲染或请求的输入。
    if (!seen.has(p)) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      seen.add(p) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      result.push(p) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return result.sort() // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 当前省份下的城市列表
// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 基于响应式数据派生filteredCities，用于保持界面展示与数据状态同步。
  if (!selectedProvince.value) return [] // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return allCities.value.filter((c) => (c.province || '其他') === selectedProvince.value) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：加载全部城市数据，供省市区选择器使用。
async function loadAllCities() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (allCities.value.length) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    const data = await getCities() // 保存data相关业务数据，作为后续计算、渲染或请求的输入。
    allCities.value = Array.isArray(data) ? data : [] // 更新allCities.value对应的页面状态，使界面展示与最新业务数据一致。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    allCities.value = [] // 更新allCities.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 选中省份 → 重置城市和区
watch(selectedProvince, () => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  selectedCityId.value = null // 更新selectedCityId.value对应的页面状态，使界面展示与最新业务数据一致。
  form.district_id = null // 更新form.district_id对应的页面状态，使界面展示与最新业务数据一致。
  districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 选中城市 → 加载该城市下的区
watch(selectedCityId, async (cityId) => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  form.district_id = null // 更新form.district_id对应的页面状态，使界面展示与最新业务数据一致。
  districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
  if (!cityId) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    districts.value = await getCityDistricts(cityId) // 等待异步接口或资源加载完成，再继续更新页面状态。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。

// ---------- 顶部工具栏省市区筛选（独立于对话框） ----------
const filterProvince = ref('') // 创建filterProvince响应式状态，用于驱动页面渲染、表单输入或接口参数。
const filterCityId = ref(null) // 创建filterCityId响应式状态，用于驱动页面渲染、表单输入或接口参数。
const filterDistrictId = ref(null) // 创建filterDistrictId响应式状态，用于驱动页面渲染、表单输入或接口参数。
const filterDistricts = ref([]) // 创建filterDistricts响应式状态，用于驱动页面渲染、表单输入或接口参数。

// 函数功能：根据筛选省份计算筛选城市列表。
const filterCities = computed(() => { // 基于响应式数据派生filterCities，用于保持界面展示与数据状态同步。
  if (!filterProvince.value) return [] // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return allCities.value.filter((c) => (c.province || '其他') === filterProvince.value) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch(filterProvince, () => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  filterCityId.value = null // 更新filterCityId.value对应的页面状态，使界面展示与最新业务数据一致。
  filterDistrictId.value = null // 更新filterDistrictId.value对应的页面状态，使界面展示与最新业务数据一致。
  filterDistricts.value = [] // 更新filterDistricts.value对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch(filterCityId, async (cityId) => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  filterDistrictId.value = null // 更新filterDistrictId.value对应的页面状态，使界面展示与最新业务数据一致。
  filterDistricts.value = [] // 更新filterDistricts.value对应的页面状态，使界面展示与最新业务数据一致。
  if (!cityId) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    filterDistricts.value = await getCityDistricts(cityId) // 等待异步接口或资源加载完成，再继续更新页面状态。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    filterDistricts.value = [] // 更新filterDistricts.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch(filterDistrictId, () => { // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  page.value = 1 // 更新page.value对应的页面状态，使界面展示与最新业务数据一致。
  fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
}) // 完成当前参数、配置或响应式数据结构的组装。

// ---------- 新增 / 编辑 ----------
const dialogVisible = ref(false) // 创建dialogVisible响应式状态，用于驱动页面渲染、表单输入或接口参数。
const dialogTitle = ref('新增房源') // 创建dialogTitle响应式状态，用于驱动页面渲染、表单输入或接口参数。
const isEdit = ref(false) // 创建isEdit响应式状态，用于驱动页面渲染、表单输入或接口参数。
const editId = ref(null) // 创建editId响应式状态，用于驱动页面渲染、表单输入或接口参数。
const formRef = ref(null) // 创建formRef响应式状态，用于驱动页面渲染、表单输入或接口参数。
const submitting = ref(false) // 创建submitting响应式状态，用于驱动页面渲染、表单输入或接口参数。

// 函数功能：返回新增或编辑房源表单的默认数据结构。
function defaultForm() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return { // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    district_id: null, // 声明district_id字段，作为组件配置、请求参数或图表数据的一部分。
    title: '', // 声明title字段，作为组件配置、请求参数或图表数据的一部分。
    total_price: undefined, // 声明total_price字段，作为组件配置、请求参数或图表数据的一部分。
    unit_price: undefined, // 声明unit_price字段，作为组件配置、请求参数或图表数据的一部分。
    area: undefined, // 声明area字段，作为组件配置、请求参数或图表数据的一部分。
    rooms: 0, // 声明rooms字段，作为组件配置、请求参数或图表数据的一部分。
    halls: 0, // 声明halls字段，作为组件配置、请求参数或图表数据的一部分。
    floor: undefined, // 声明floor字段，作为组件配置、请求参数或图表数据的一部分。
    total_floors: undefined, // 声明total_floors字段，作为组件配置、请求参数或图表数据的一部分。
    build_year: undefined, // 声明build_year字段，作为组件配置、请求参数或图表数据的一部分。
    orientation: '', // 声明orientation字段，作为组件配置、请求参数或图表数据的一部分。
    decoration: '', // 声明decoration字段，作为组件配置、请求参数或图表数据的一部分。
    has_elevator: false, // 声明has_elevator字段，作为组件配置、请求参数或图表数据的一部分。
    listing_type: '二手房', // 声明listing_type字段，作为组件配置、请求参数或图表数据的一部分。
    lng: undefined, // 声明lng字段，作为组件配置、请求参数或图表数据的一部分。
    lat: undefined, // 声明lat字段，作为组件配置、请求参数或图表数据的一部分。
    source: 'manual', // 声明source字段，作为组件配置、请求参数或图表数据的一部分。
    source_url: '', // 声明source_url字段，作为组件配置、请求参数或图表数据的一部分。
    listing_date: '', // 声明listing_date字段，作为组件配置、请求参数或图表数据的一部分。
    ownership_type: '', // 声明ownership_type字段，作为组件配置、请求参数或图表数据的一部分。
    property_right: '', // 声明property_right字段，作为组件配置、请求参数或图表数据的一部分。
    mortgage: '', // 声明mortgage字段，作为组件配置、请求参数或图表数据的一部分。
    selling_point: '', // 声明selling_point字段，作为组件配置、请求参数或图表数据的一部分。
    community_intro: '', // 声明community_intro字段，作为组件配置、请求参数或图表数据的一部分。
    layout_intro: '', // 声明layout_intro字段，作为组件配置、请求参数或图表数据的一部分。
    transport_intro: '', // 声明transport_intro字段，作为组件配置、请求参数或图表数据的一部分。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

const form = reactive(defaultForm()) // 创建表单数据模型，用于驱动页面渲染、表单输入或接口参数。

const decorationOptions = ['毛坯', '简装', '精装', '豪装', '其他'] // 保存decorationOptions相关业务数据，作为后续计算、渲染或请求的输入。
const orientationOptions = [ // 保存orientationOptions相关业务数据，作为后续计算、渲染或请求的输入。
  '南北', '南', '北', '东西', '东', '西', '东南', '西南', '东北', '西北', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
] // 完成当前参数、配置或响应式数据结构的组装。
const listingTypeOptions = ['二手房', '新房', '出租'] // 保存listingTypeOptions相关业务数据，作为后续计算、渲染或请求的输入。
const ownershipTypeOptions = ['商品房', '已购公房', '经济适用房', '央产房', '私产', '其他'] // 保存ownershipTypeOptions相关业务数据，作为后续计算、渲染或请求的输入。
const propertyRightOptions = ['非共有', '共有'] // 保存propertyRightOptions相关业务数据，作为后续计算、渲染或请求的输入。
const mortgageOptions = ['无抵押', '有抵押', '有抵押业主自还', '有抵押客户偿还', '其他'] // 保存mortgageOptions相关业务数据，作为后续计算、渲染或请求的输入。

const formRules = { // 保存formRules相关业务数据，作为后续计算、渲染或请求的输入。
  title: [{ required: true, message: '请输入房源标题', trigger: 'blur' }], // 声明title字段，作为组件配置、请求参数或图表数据的一部分。
  district_id: [{ required: true, message: '请选择区域', trigger: 'change' }], // 声明district_id字段，作为组件配置、请求参数或图表数据的一部分。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：打开新增房源对话框并重置表单状态。
async function openCreate() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  await loadAllCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  dialogTitle.value = '新增房源' // 更新dialogTitle.value对应的页面状态，使界面展示与最新业务数据一致。
  isEdit.value = false // 更新isEdit.value对应的页面状态，使界面展示与最新业务数据一致。
  editId.value = null // 更新editId.value对应的页面状态，使界面展示与最新业务数据一致。
  Object.assign(form, defaultForm()) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  selectedProvince.value = '' // 更新selectedProvince.value对应的页面状态，使界面展示与最新业务数据一致。
  selectedCityId.value = null // 更新selectedCityId.value对应的页面状态，使界面展示与最新业务数据一致。
  districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
  dialogVisible.value = true // 更新dialogVisible.value对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：打开编辑房源对话框并回填当前行数据。
async function openEdit(row) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  await loadAllCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  dialogTitle.value = '编辑房源' // 更新dialogTitle.value对应的页面状态，使界面展示与最新业务数据一致。
  isEdit.value = true // 更新isEdit.value对应的页面状态，使界面展示与最新业务数据一致。
  editId.value = row.id // 更新editId.value对应的页面状态，使界面展示与最新业务数据一致。

  // 填充表单数据：房源主体字段来自 Property，交易扩展字段来自 transaction。
  const t = row.transaction || {} // 保存t相关业务数据，作为后续计算、渲染或请求的输入。
  Object.assign(form, { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    district_id: row.district_id, // 声明district_id字段，作为组件配置、请求参数或图表数据的一部分。
    title: row.title, // 声明title字段，作为组件配置、请求参数或图表数据的一部分。
    total_price: row.total_price, // 声明total_price字段，作为组件配置、请求参数或图表数据的一部分。
    unit_price: row.unit_price, // 声明unit_price字段，作为组件配置、请求参数或图表数据的一部分。
    area: row.area, // 声明area字段，作为组件配置、请求参数或图表数据的一部分。
    rooms: row.rooms ?? 0, // 声明rooms字段，作为组件配置、请求参数或图表数据的一部分。
    halls: row.halls ?? 0, // 声明halls字段，作为组件配置、请求参数或图表数据的一部分。
    floor: row.floor, // 声明floor字段，作为组件配置、请求参数或图表数据的一部分。
    total_floors: row.total_floors, // 声明total_floors字段，作为组件配置、请求参数或图表数据的一部分。
    build_year: row.build_year, // 声明build_year字段，作为组件配置、请求参数或图表数据的一部分。
    orientation: row.orientation || '', // 声明orientation字段，作为组件配置、请求参数或图表数据的一部分。
    decoration: row.decoration || '', // 声明decoration字段，作为组件配置、请求参数或图表数据的一部分。
    has_elevator: row.has_elevator ?? false, // 声明has_elevator字段，作为组件配置、请求参数或图表数据的一部分。
    listing_type: row.listing_type || '二手房', // 声明listing_type字段，作为组件配置、请求参数或图表数据的一部分。
    lng: row.lng, // 声明lng字段，作为组件配置、请求参数或图表数据的一部分。
    lat: row.lat, // 声明lat字段，作为组件配置、请求参数或图表数据的一部分。
    source: row.source || 'manual', // 声明source字段，作为组件配置、请求参数或图表数据的一部分。
    source_url: row.source_url || '', // 声明source_url字段，作为组件配置、请求参数或图表数据的一部分。
    listing_date: t.listing_date || '', // 声明listing_date字段，作为组件配置、请求参数或图表数据的一部分。
    ownership_type: t.ownership_type || '', // 声明ownership_type字段，作为组件配置、请求参数或图表数据的一部分。
    property_right: t.property_right || '', // 声明property_right字段，作为组件配置、请求参数或图表数据的一部分。
    mortgage: t.mortgage || '', // 声明mortgage字段，作为组件配置、请求参数或图表数据的一部分。
    selling_point: t.selling_point || '', // 声明selling_point字段，作为组件配置、请求参数或图表数据的一部分。
    community_intro: t.community_intro || '', // 声明community_intro字段，作为组件配置、请求参数或图表数据的一部分。
    layout_intro: t.layout_intro || '', // 声明layout_intro字段，作为组件配置、请求参数或图表数据的一部分。
    transport_intro: t.transport_intro || '', // 声明transport_intro字段，作为组件配置、请求参数或图表数据的一部分。
  }) // 完成当前参数、配置或响应式数据结构的组装。

  // 根据 district_id 反查省/市/区并级联
  selectedProvince.value = '' // 更新selectedProvince.value对应的页面状态，使界面展示与最新业务数据一致。
  selectedCityId.value = null // 更新selectedCityId.value对应的页面状态，使界面展示与最新业务数据一致。
  districts.value = [] // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。

  if (!row.district_id) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    dialogVisible.value = true // 更新dialogVisible.value对应的页面状态，使界面展示与最新业务数据一致。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 遍历所有城市找到包含该区的那一个
  for (const c of allCities.value) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    try { // 开始执行可能失败的接口请求或异步页面更新。
      const dists = await getCityDistricts(c.id) // 保存dists相关业务数据，作为后续计算、渲染或请求的输入。
      const found = dists.find((d) => d.id === row.district_id) // 保存found相关业务数据，作为后续计算、渲染或请求的输入。
      if (found) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
        selectedProvince.value = c.province || '其他' // 更新selectedProvince.value对应的页面状态，使界面展示与最新业务数据一致。
        selectedCityId.value = c.id // 更新selectedCityId.value对应的页面状态，使界面展示与最新业务数据一致。
        districts.value = dists // 更新districts.value对应的页面状态，使界面展示与最新业务数据一致。
        await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
        form.district_id = row.district_id // 更新form.district_id对应的页面状态，使界面展示与最新业务数据一致。
        break // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      } // 完成当前参数、配置或响应式数据结构的组装。
    } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      // continue trying other cities
    } // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。

  dialogVisible.value = true // 更新dialogVisible.value对应的页面状态，使界面展示与最新业务数据一致。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：跳转到房源详情页面。
function openDetail(row) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!row?.id) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  router.push({ name: 'property-detail', params: { id: row.id } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：校验并提交新增或编辑房源表单。
async function handleSubmit() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const valid = await formRef.value.validate().catch(() => false) // 保存valid相关业务数据，作为后续计算、渲染或请求的输入。
  if (!valid) return // 根据当前状态、接口结果或用户输入选择对应交互路径。

  submitting.value = true // 更新submitting.value对应的页面状态，使界面展示与最新业务数据一致。
  const payload = { ...form } // 保存payload相关业务数据，作为后续计算、渲染或请求的输入。
  // 清理空字符串：用 null 表达“未填写”，方便后端删除或跳过交易扩展字段。
  if (payload.orientation === '') payload.orientation = null // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (payload.decoration === '') payload.decoration = null // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (payload.source_url === '') payload.source_url = null // 根据当前状态、接口结果或用户输入选择对应交互路径。
  for (const field of [ // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    'listing_date', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'ownership_type', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'property_right', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'mortgage', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'selling_point', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'community_intro', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'layout_intro', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    'transport_intro', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ]) { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    if (payload[field] === '') payload[field] = null // 根据当前状态、接口结果或用户输入选择对应交互路径。
  } // 完成当前参数、配置或响应式数据结构的组装。

  try { // 开始执行可能失败的接口请求或异步页面更新。
    let savedProperty = null // 保存savedProperty相关业务数据，作为后续计算、渲染或请求的输入。
    if (isEdit.value) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      savedProperty = await adminUpdateProperty(editId.value, payload) // 等待异步接口或资源加载完成，再继续更新页面状态。
      ElMessage.success('房源已更新') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      savedProperty = await adminCreateProperty(payload) // 等待异步接口或资源加载完成，再继续更新页面状态。
      ElMessage.success('房源已创建') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
    dialogVisible.value = false // 更新dialogVisible.value对应的页面状态，使界面展示与最新业务数据一致。
    fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

    if (!isEdit.value && savedProperty?.id) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      ElMessageBox.confirm('房源已创建，是否立即查看详情页？', '创建成功', { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
        type: 'success', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
        confirmButtonText: '查看详情', // 声明confirmButtonText字段，作为组件配置、请求参数或图表数据的一部分。
        cancelButtonText: '继续管理', // 声明cancelButtonText字段，作为组件配置、请求参数或图表数据的一部分。
      }) // 完成当前参数、配置或响应式数据结构的组装。
        .then(() => openDetail(savedProperty)) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        .catch(() => {}) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    // handled by interceptor
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    submitting.value = false // 更新submitting.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：确认后删除指定房源并刷新列表。
async function handleDelete(row) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    await ElMessageBox.confirm( // 等待异步接口或资源加载完成，再继续更新页面状态。
      `确定要删除房源「${row.title}」吗？删除后不可恢复。`, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      '删除确认', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    ) // 完成当前参数、配置或响应式数据结构的组装。
    await adminDeleteProperty(row.id) // 等待异步接口或资源加载完成，再继续更新页面状态。
    ElMessage.success('已删除') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    fetchList() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    // cancelled or error
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

// ---------- 表格格式化 ----------
// 函数功能：格式化总价展示文本。
function formatPrice(val) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (val == null) return '-' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return `${val} 万` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：格式化单价展示文本。
function formatUnitPrice(val) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (val == null) return '-' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return `${val} 元/㎡` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：格式化面积展示文本。
function formatArea(val) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (val == null) return '-' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return `${val} ㎡` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>管理后台 · 房源管理</h2>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        新增房源
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-select
        v-model="filterProvince"
        placeholder="省份"
        clearable
        style="width: 130px"
      >
        <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
      </el-select>
      <el-select
        v-model="filterCityId"
        placeholder="城市"
        clearable
        style="width: 130px"
        :disabled="!filterProvince"
      >
        <el-option v-for="c in filterCities" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select
        v-model="filterDistrictId"
        placeholder="区域"
        clearable
        style="width: 150px"
        :disabled="!filterCityId"
      >
        <el-option v-for="d in filterDistricts" :key="d.id" :label="d.name" :value="d.id" />
      </el-select>
      <el-input
        v-model="keyword"
        placeholder="搜索房源标题…"
        clearable
        style="width: 220px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button
        @click="filterProvince = ''; filterCityId = null; filterDistrictId = null; keyword = ''; page = 1; fetchList()"
      >
        重置
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" stripe border style="width: 100%">
      <el-table-column type="index" :index="(idx) => (page - 1) * pageSize + idx + 1" label="序号" width="60" />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="city_name" label="城市" width="100" />
      <el-table-column prop="district_name" label="区域" width="100" />
      <el-table-column label="总价" width="100" align="right">
        <template #default="{ row }">{{ formatPrice(row.total_price) }}</template>
      </el-table-column>
      <el-table-column label="单价" width="110" align="right">
        <template #default="{ row }">{{ formatUnitPrice(row.unit_price) }}</template>
      </el-table-column>
      <el-table-column label="面积" width="90" align="right">
        <template #default="{ row }">{{ formatArea(row.area) }}</template>
      </el-table-column>
      <el-table-column prop="layout" label="户型" width="80" />
      <el-table-column prop="listing_type" label="类型" width="80" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="success" link size="small" @click="openDetail(row)">查看详情</el-button>
          <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > 0">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchList"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="820px"
      top="24px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="90px"
        label-position="right"
      >
        <el-divider content-position="left">基础信息</el-divider>

        <!-- 省 → 市 → 区 三级级联 -->
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="省份">
              <el-select
                v-model="selectedProvince"
                placeholder="选择省份"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="p in provinces"
                  :key="p"
                  :label="p"
                  :value="p"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="城市">
              <el-select
                v-model="selectedCityId"
                placeholder="选择城市"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="c in filteredCities"
                  :key="c.id"
                  :label="c.name"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="区域" prop="district_id">
              <el-select
                v-model="form.district_id"
                placeholder="选择区域"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="d in districts"
                  :key="d.id"
                  :label="d.name"
                  :value="d.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 标题 -->
        <el-form-item label="房源标题" prop="title">
          <el-input v-model="form.title" placeholder="如：阳光花园 精装三房 南北通透" />
        </el-form-item>

        <!-- 价格 / 面积 -->
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="总价(万元)">
              <el-input-number
                v-model="form.total_price"
                :min="0"
                :precision="1"
                :controls="false"
                placeholder="总价"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价(元/㎡)">
              <el-input-number
                v-model="form.unit_price"
                :min="0"
                :precision="0"
                :controls="false"
                placeholder="单价"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="建筑面积">
              <el-input-number
                v-model="form.area"
                :min="0"
                :precision="2"
                :controls="false"
                placeholder="㎡"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">房源信息</el-divider>

        <!-- 户型 -->
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="室">
              <el-input-number
                v-model="form.rooms"
                :min="0"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="厅">
              <el-input-number
                v-model="form.halls"
                :min="0"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="楼层">
              <el-input-number
                v-model="form.floor"
                :min="1"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="总楼层">
              <el-input-number
                v-model="form.total_floors"
                :min="1"
                :controls="false"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 属性 -->
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="建成年份">
              <el-input-number
                v-model="form.build_year"
                :min="1900"
                :max="2030"
                :controls="false"
                placeholder="年份"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="朝向">
              <el-select
                v-model="form.orientation"
                placeholder="朝向"
                clearable
                style="width: 100%"
              >
                <el-option v-for="o in orientationOptions" :key="o" :label="o" :value="o" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="装修">
              <el-select
                v-model="form.decoration"
                placeholder="装修"
                clearable
                style="width: 100%"
              >
                <el-option v-for="d in decorationOptions" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 类型 / 电梯 -->
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="类型">
              <el-select v-model="form.listing_type" style="width: 100%">
                <el-option v-for="t in listingTypeOptions" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="有电梯">
              <el-switch v-model="form.has_elevator" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">交易属性</el-divider>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="挂牌时间">
              <el-date-picker
                v-model="form.listing_date"
                type="date"
                value-format="YYYY/M/D"
                placeholder="选择挂牌日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="交易权属">
              <el-select
                v-model="form.ownership_type"
                placeholder="如 商品房"
                clearable
                filterable
                allow-create
                style="width: 100%"
              >
                <el-option v-for="o in ownershipTypeOptions" :key="o" :label="o" :value="o" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="产权情况">
              <el-select
                v-model="form.property_right"
                placeholder="如 非共有"
                clearable
                filterable
                allow-create
                style="width: 100%"
              >
                <el-option v-for="o in propertyRightOptions" :key="o" :label="o" :value="o" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="抵押信息">
              <el-select
                v-model="form.mortgage"
                placeholder="如 无抵押"
                clearable
                filterable
                allow-create
                style="width: 100%"
              >
                <el-option v-for="o in mortgageOptions" :key="o" :label="o" :value="o" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="核心卖点">
          <el-input
            v-model="form.selling_point"
            type="textarea"
            :rows="2"
            placeholder="如：此房在凤凰路东侧，距离汉峪金谷300米，上下班方便，总价低。"
          />
        </el-form-item>
        <el-form-item label="小区介绍">
          <el-input
            v-model="form.community_intro"
            type="textarea"
            :rows="2"
            placeholder="填写小区环境、物业、生活配套等介绍"
          />
        </el-form-item>
        <el-form-item label="户型介绍">
          <el-input
            v-model="form.layout_intro"
            type="textarea"
            :rows="2"
            placeholder="填写朝向、结构、梯户比、楼层等户型说明"
          />
        </el-form-item>
        <el-form-item label="交通出行">
          <el-input
            v-model="form.transport_intro"
            type="textarea"
            :rows="2"
            placeholder="填写公交、地铁、自驾等交通情况"
          />
        </el-form-item>

        <el-divider content-position="left">来源与坐标</el-divider>

        <!-- 坐标 -->
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="经度">
              <el-input-number
                v-model="form.lng"
                :precision="6"
                :controls="false"
                placeholder="经度"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="纬度">
              <el-input-number
                v-model="form.lat"
                :precision="6"
                :controls="false"
                placeholder="纬度"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数据来源">
              <el-input v-model="form.source" placeholder="如 manual" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 来源链接 -->
        <el-form-item label="来源链接">
          <el-input v-model="form.source_url" placeholder="可选，如 https://..." />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '确认创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-page { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  max-width: 1280px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin: 0 auto; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  padding: 24px 20px 40px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.page-header { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  margin-bottom: 20px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.page-header h2 { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 22px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #1e3a8a; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.toolbar { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.pagination-wrap { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: flex-end; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  margin-top: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
