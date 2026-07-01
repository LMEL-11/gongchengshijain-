<!-- 文件功能：实现管理员房源管理页面，支持筛选、分页、新增、编辑、详情和删除。 -->
<script setup>
import { reactive, ref, onMounted, computed, watch, nextTick } from 'vue' // 导入 { reactive, ref, onMounted, computed, watch, nextTick }，供当前前端模块渲染或交互逻辑使用。
import { useRouter } from 'vue-router' // 导入 { useRouter }，供当前前端模块渲染或交互逻辑使用。
import { ElMessage, ElMessageBox } from 'element-plus' // 导入 { ElMessage, ElMessageBox }，供当前前端模块渲染或交互逻辑使用。
import { // 导入 {，供当前前端模块渲染或交互逻辑使用。
  adminGetProperties, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  adminCreateProperty, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  adminUpdateProperty, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  adminDeleteProperty, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  getCities, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  getCityDistricts, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} from '@/api' // 执行当前前端代码行，推动页面数据和交互流程继续运行。

const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。

// ---------- 列表 ----------
const list = ref([]) // 创建 list，用于保存页面状态、计算结果或接口参数。
const total = ref(0) // 创建 total，用于保存页面状态、计算结果或接口参数。
const page = ref(1) // 创建 page，用于保存页面状态、计算结果或接口参数。
const pageSize = ref(20) // 创建 pageSize，用于保存页面状态、计算结果或接口参数。
const keyword = ref('') // 创建 keyword，用于保存页面状态、计算结果或接口参数。
const loading = ref(false) // 创建 loading，用于保存页面状态、计算结果或接口参数。

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() { // 定义 fetchList 函数，处理页面交互、数据加载或状态同步。
  loading.value = true // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // 后台列表筛选参数和分页参数全部交给后端处理，前端只维护当前查询状态。
    const res = await adminGetProperties({ // 创建 res，用于保存页面状态、计算结果或接口参数。
      page: page.value, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      page_size: pageSize.value, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      keyword: keyword.value || undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      district_id: filterDistrictId.value || undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }) // 结束当前函数、对象、数组或组件配置块。
    list.value = res.items // 更新 list.value 响应式状态，让页面展示与最新数据保持一致。
    total.value = res.total // 更新 total.value 响应式状态，让页面展示与最新数据保持一致。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // handled by interceptor
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loading.value = false // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：重置到第一页并执行关键词搜索。
function handleSearch() { // 定义 handleSearch 函数，处理页面交互、数据加载或状态同步。
  page.value = 1 // 更新 page.value 响应式状态，让页面展示与最新数据保持一致。
  fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理分页大小变化并重新加载列表。
function handleSizeChange(size) { // 定义 handleSizeChange 函数，处理页面交互、数据加载或状态同步。
  pageSize.value = size // 更新 pageSize.value 响应式状态，让页面展示与最新数据保持一致。
  page.value = 1 // 更新 page.value 响应式状态，让页面展示与最新数据保持一致。
  fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  loadAllCities() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// ---------- 省市区级联数据 ----------
const allCities = ref([]) // 创建 allCities，用于保存页面状态、计算结果或接口参数。
const selectedProvince = ref('') // 创建 selectedProvince，用于保存页面状态、计算结果或接口参数。
const selectedCityId = ref(null) // 创建 selectedCityId，用于保存页面状态、计算结果或接口参数。
const districts = ref([]) // 创建 districts，用于保存页面状态、计算结果或接口参数。

// 省份列表从城市数据中计算
// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 创建 provinces，用于保存页面状态、计算结果或接口参数。
  const seen = new Set() // 创建 seen，用于保存页面状态、计算结果或接口参数。
  const result = [] // 创建 result，用于保存页面状态、计算结果或接口参数。
  for (const c of allCities.value) { // 遍历当前数据集合，逐项生成页面需要的数据。
    const p = c.province || '其他' // 创建 p，用于保存页面状态、计算结果或接口参数。
    if (!seen.has(p)) { // 根据当前页面状态或接口结果决定是否进入该分支。
      seen.add(p) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      result.push(p) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
  return result.sort() // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 当前省份下的城市列表
// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 创建 filteredCities，用于保存页面状态、计算结果或接口参数。
  if (!selectedProvince.value) return [] // 根据当前页面状态或接口结果决定是否进入该分支。
  return allCities.value.filter((c) => (c.province || '其他') === selectedProvince.value) // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：加载全部城市数据，供省市区选择器使用。
async function loadAllCities() { // 定义 loadAllCities 函数，处理页面交互、数据加载或状态同步。
  if (allCities.value.length) return // 根据当前页面状态或接口结果决定是否进入该分支。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    const data = await getCities() // 创建 data，用于保存页面状态、计算结果或接口参数。
    allCities.value = Array.isArray(data) ? data : [] // 更新 allCities.value 响应式状态，让页面展示与最新数据保持一致。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    allCities.value = [] // 更新 allCities.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 选中省份 → 重置城市和区
watch(selectedProvince, () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  selectedCityId.value = null // 更新 selectedCityId.value 响应式状态，让页面展示与最新数据保持一致。
  form.district_id = null // 设置 form.district_id 的值，作为后续渲染、计算或请求的输入。
  districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
}) // 结束当前函数、对象、数组或组件配置块。

// 选中城市 → 加载该城市下的区
watch(selectedCityId, async (cityId) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  form.district_id = null // 设置 form.district_id 的值，作为后续渲染、计算或请求的输入。
  districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
  if (!cityId) return // 根据当前页面状态或接口结果决定是否进入该分支。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    districts.value = await getCityDistricts(cityId) // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。

// ---------- 顶部工具栏省市区筛选（独立于对话框） ----------
const filterProvince = ref('') // 创建 filterProvince，用于保存页面状态、计算结果或接口参数。
const filterCityId = ref(null) // 创建 filterCityId，用于保存页面状态、计算结果或接口参数。
const filterDistrictId = ref(null) // 创建 filterDistrictId，用于保存页面状态、计算结果或接口参数。
const filterDistricts = ref([]) // 创建 filterDistricts，用于保存页面状态、计算结果或接口参数。

// 函数功能：根据筛选省份计算筛选城市列表。
const filterCities = computed(() => { // 创建 filterCities，用于保存页面状态、计算结果或接口参数。
  if (!filterProvince.value) return [] // 根据当前页面状态或接口结果决定是否进入该分支。
  return allCities.value.filter((c) => (c.province || '其他') === filterProvince.value) // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

watch(filterProvince, () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  filterCityId.value = null // 更新 filterCityId.value 响应式状态，让页面展示与最新数据保持一致。
  filterDistrictId.value = null // 更新 filterDistrictId.value 响应式状态，让页面展示与最新数据保持一致。
  filterDistricts.value = [] // 更新 filterDistricts.value 响应式状态，让页面展示与最新数据保持一致。
}) // 结束当前函数、对象、数组或组件配置块。

watch(filterCityId, async (cityId) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  filterDistrictId.value = null // 更新 filterDistrictId.value 响应式状态，让页面展示与最新数据保持一致。
  filterDistricts.value = [] // 更新 filterDistricts.value 响应式状态，让页面展示与最新数据保持一致。
  if (!cityId) return // 根据当前页面状态或接口结果决定是否进入该分支。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    filterDistricts.value = await getCityDistricts(cityId) // 更新 filterDistricts.value 响应式状态，让页面展示与最新数据保持一致。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    filterDistricts.value = [] // 更新 filterDistricts.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。

watch(filterDistrictId, () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  page.value = 1 // 更新 page.value 响应式状态，让页面展示与最新数据保持一致。
  fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// ---------- 新增 / 编辑 ----------
const dialogVisible = ref(false) // 创建 dialogVisible，用于保存页面状态、计算结果或接口参数。
const dialogTitle = ref('新增房源') // 创建 dialogTitle，用于保存页面状态、计算结果或接口参数。
const isEdit = ref(false) // 创建 isEdit，用于保存页面状态、计算结果或接口参数。
const editId = ref(null) // 创建 editId，用于保存页面状态、计算结果或接口参数。
const formRef = ref(null) // 创建 formRef，用于保存页面状态、计算结果或接口参数。
const submitting = ref(false) // 创建 submitting，用于保存页面状态、计算结果或接口参数。

// 函数功能：返回新增或编辑房源表单的默认数据结构。
function defaultForm() { // 定义 defaultForm 函数，处理页面交互、数据加载或状态同步。
  return { // 返回整理后的数据、组件配置或渲染结果。
    district_id: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    title: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    total_price: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    unit_price: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    area: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    rooms: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    halls: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    floor: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    total_floors: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    build_year: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    orientation: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    decoration: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    has_elevator: false, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    listing_type: '二手房', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    lng: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    lat: undefined, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    source: 'manual', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    source_url: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    listing_date: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ownership_type: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    property_right: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    mortgage: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    selling_point: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    community_intro: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    layout_intro: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    transport_intro: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

const form = reactive(defaultForm()) // 创建 form，用于保存页面状态、计算结果或接口参数。

const decorationOptions = ['毛坯', '简装', '精装', '豪装', '其他'] // 创建 decorationOptions，用于保存页面状态、计算结果或接口参数。
const orientationOptions = [ // 创建 orientationOptions，用于保存页面状态、计算结果或接口参数。
  '南北', '南', '北', '东西', '东', '西', '东南', '西南', '东北', '西北', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
] // 结束当前函数、对象、数组或组件配置块。
const listingTypeOptions = ['二手房', '新房', '出租'] // 创建 listingTypeOptions，用于保存页面状态、计算结果或接口参数。
const ownershipTypeOptions = ['商品房', '已购公房', '经济适用房', '央产房', '私产', '其他'] // 创建 ownershipTypeOptions，用于保存页面状态、计算结果或接口参数。
const propertyRightOptions = ['非共有', '共有'] // 创建 propertyRightOptions，用于保存页面状态、计算结果或接口参数。
const mortgageOptions = ['无抵押', '有抵押', '有抵押业主自还', '有抵押客户偿还', '其他'] // 创建 mortgageOptions，用于保存页面状态、计算结果或接口参数。

const formRules = { // 创建 formRules，用于保存页面状态、计算结果或接口参数。
  title: [{ required: true, message: '请输入房源标题', trigger: 'blur' }], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  district_id: [{ required: true, message: '请选择区域', trigger: 'change' }], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：打开新增房源对话框并重置表单状态。
async function openCreate() { // 定义 openCreate 函数，处理页面交互、数据加载或状态同步。
  await loadAllCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  dialogTitle.value = '新增房源' // 更新 dialogTitle.value 响应式状态，让页面展示与最新数据保持一致。
  isEdit.value = false // 更新 isEdit.value 响应式状态，让页面展示与最新数据保持一致。
  editId.value = null // 更新 editId.value 响应式状态，让页面展示与最新数据保持一致。
  Object.assign(form, defaultForm()) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  selectedProvince.value = '' // 更新 selectedProvince.value 响应式状态，让页面展示与最新数据保持一致。
  selectedCityId.value = null // 更新 selectedCityId.value 响应式状态，让页面展示与最新数据保持一致。
  districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
  dialogVisible.value = true // 更新 dialogVisible.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：打开编辑房源对话框并回填当前行数据。
async function openEdit(row) { // 定义 openEdit 函数，处理页面交互、数据加载或状态同步。
  await loadAllCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  dialogTitle.value = '编辑房源' // 更新 dialogTitle.value 响应式状态，让页面展示与最新数据保持一致。
  isEdit.value = true // 更新 isEdit.value 响应式状态，让页面展示与最新数据保持一致。
  editId.value = row.id // 更新 editId.value 响应式状态，让页面展示与最新数据保持一致。

  // 填充表单数据：房源主体字段来自 Property，交易扩展字段来自 transaction。
  const t = row.transaction || {} // 创建 t，用于保存页面状态、计算结果或接口参数。
  Object.assign(form, { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    district_id: row.district_id, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    title: row.title, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    total_price: row.total_price, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    unit_price: row.unit_price, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    area: row.area, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    rooms: row.rooms ?? 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    halls: row.halls ?? 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    floor: row.floor, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    total_floors: row.total_floors, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    build_year: row.build_year, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    orientation: row.orientation || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    decoration: row.decoration || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    has_elevator: row.has_elevator ?? false, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    listing_type: row.listing_type || '二手房', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    lng: row.lng, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    lat: row.lat, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    source: row.source || 'manual', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    source_url: row.source_url || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    listing_date: t.listing_date || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ownership_type: t.ownership_type || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    property_right: t.property_right || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    mortgage: t.mortgage || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    selling_point: t.selling_point || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    community_intro: t.community_intro || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    layout_intro: t.layout_intro || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    transport_intro: t.transport_intro || '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。

  // 根据 district_id 反查省/市/区并级联
  selectedProvince.value = '' // 更新 selectedProvince.value 响应式状态，让页面展示与最新数据保持一致。
  selectedCityId.value = null // 更新 selectedCityId.value 响应式状态，让页面展示与最新数据保持一致。
  districts.value = [] // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。

  if (!row.district_id) { // 根据当前页面状态或接口结果决定是否进入该分支。
    dialogVisible.value = true // 更新 dialogVisible.value 响应式状态，让页面展示与最新数据保持一致。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  // 遍历所有城市找到包含该区的那一个
  for (const c of allCities.value) { // 遍历当前数据集合，逐项生成页面需要的数据。
    try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      const dists = await getCityDistricts(c.id) // 创建 dists，用于保存页面状态、计算结果或接口参数。
      const found = dists.find((d) => d.id === row.district_id) // 创建 found，用于保存页面状态、计算结果或接口参数。
      if (found) { // 根据当前页面状态或接口结果决定是否进入该分支。
        selectedProvince.value = c.province || '其他' // 更新 selectedProvince.value 响应式状态，让页面展示与最新数据保持一致。
        selectedCityId.value = c.id // 更新 selectedCityId.value 响应式状态，让页面展示与最新数据保持一致。
        districts.value = dists // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
        await nextTick() // 等待异步接口或资源加载完成，再继续更新页面状态。
        form.district_id = row.district_id // 设置 form.district_id 的值，作为后续渲染、计算或请求的输入。
        break // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      } // 结束当前函数、对象、数组或组件配置块。
    } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      // continue trying other cities
    } // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。

  dialogVisible.value = true // 更新 dialogVisible.value 响应式状态，让页面展示与最新数据保持一致。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：跳转到房源详情页面。
function openDetail(row) { // 定义 openDetail 函数，处理页面交互、数据加载或状态同步。
  if (!row?.id) return // 根据当前页面状态或接口结果决定是否进入该分支。
  router.push({ name: 'property-detail', params: { id: row.id } }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：校验并提交新增或编辑房源表单。
async function handleSubmit() { // 定义 handleSubmit 函数，处理页面交互、数据加载或状态同步。
  const valid = await formRef.value.validate().catch(() => false) // 创建 valid，用于保存页面状态、计算结果或接口参数。
  if (!valid) return // 根据当前页面状态或接口结果决定是否进入该分支。

  submitting.value = true // 更新 submitting.value 响应式状态，让页面展示与最新数据保持一致。
  const payload = { ...form } // 创建 payload，用于保存页面状态、计算结果或接口参数。
  // 清理空字符串：用 null 表达“未填写”，方便后端删除或跳过交易扩展字段。
  if (payload.orientation === '') payload.orientation = null // 根据当前页面状态或接口结果决定是否进入该分支。
  if (payload.decoration === '') payload.decoration = null // 根据当前页面状态或接口结果决定是否进入该分支。
  if (payload.source_url === '') payload.source_url = null // 根据当前页面状态或接口结果决定是否进入该分支。
  for (const field of [ // 遍历当前数据集合，逐项生成页面需要的数据。
    'listing_date', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'ownership_type', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'property_right', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'mortgage', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'selling_point', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'community_intro', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'layout_intro', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    'transport_intro', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ]) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    if (payload[field] === '') payload[field] = null // 根据当前页面状态或接口结果决定是否进入该分支。
  } // 结束当前函数、对象、数组或组件配置块。

  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    let savedProperty = null // 创建 savedProperty，用于保存页面状态、计算结果或接口参数。
    if (isEdit.value) { // 根据当前页面状态或接口结果决定是否进入该分支。
      savedProperty = await adminUpdateProperty(editId.value, payload) // 更新 savedProperty 响应式状态，让页面展示与最新数据保持一致。
      ElMessage.success('房源已更新') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      savedProperty = await adminCreateProperty(payload) // 等待异步接口或资源加载完成，再继续更新页面状态。
      ElMessage.success('房源已创建') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
    dialogVisible.value = false // 更新 dialogVisible.value 响应式状态，让页面展示与最新数据保持一致。
    fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。

    if (!isEdit.value && savedProperty?.id) { // 根据当前页面状态或接口结果决定是否进入该分支。
      ElMessageBox.confirm('房源已创建，是否立即查看详情页？', '创建成功', { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        type: 'success', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        confirmButtonText: '查看详情', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        cancelButtonText: '继续管理', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      }) // 结束当前函数、对象、数组或组件配置块。
        .then(() => openDetail(savedProperty)) // 设置 .then 的值，作为后续渲染、计算或请求的输入。
        .catch(() => {}) // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    } // 结束当前函数、对象、数组或组件配置块。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // handled by interceptor
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    submitting.value = false // 更新 submitting.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：确认后删除指定房源并刷新列表。
async function handleDelete(row) { // 定义 handleDelete 函数，处理页面交互、数据加载或状态同步。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    await ElMessageBox.confirm( // 等待异步接口或资源加载完成，再继续更新页面状态。
      `确定要删除房源「${row.title}」吗？删除后不可恢复。`, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      '删除确认', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    ) // 结束当前函数、对象、数组或组件配置块。
    await adminDeleteProperty(row.id) // 等待异步接口或资源加载完成，再继续更新页面状态。
    ElMessage.success('已删除') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    fetchList() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // cancelled or error
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

// ---------- 表格格式化 ----------
// 函数功能：格式化总价展示文本。
function formatPrice(val) { // 定义 formatPrice 函数，处理页面交互、数据加载或状态同步。
  if (val == null) return '-' // 根据当前页面状态或接口结果决定是否进入该分支。
  return `${val} 万` // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
// 函数功能：格式化单价展示文本。
function formatUnitPrice(val) { // 定义 formatUnitPrice 函数，处理页面交互、数据加载或状态同步。
  if (val == null) return '-' // 根据当前页面状态或接口结果决定是否进入该分支。
  return `${val} 元/㎡` // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
// 函数功能：格式化面积展示文本。
function formatArea(val) { // 定义 formatArea 函数，处理页面交互、数据加载或状态同步。
  if (val == null) return '-' // 根据当前页面状态或接口结果决定是否进入该分支。
  return `${val} ㎡` // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
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
.admin-page { /* 定义当前选择器的样式作用域。 */
  max-width: 1280px; /* 设置元素最大宽度。 */
  margin: 0 auto; /* 设置元素外边距。 */
  padding: 24px 20px 40px; /* 设置元素内边距。 */
} /* 结束当前样式规则块。 */

.page-header { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
  margin-bottom: 20px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */

.page-header h2 { /* 定义当前选择器的样式作用域。 */
  margin: 0; /* 设置元素外边距。 */
  font-size: 22px; /* 设置文字大小。 */
  color: #1e3a8a; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */

.toolbar { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  gap: 12px; /* 设置子元素之间的间距。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */

.pagination-wrap { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  justify-content: flex-end; /* 设置主轴内容分布方式。 */
  margin-top: 16px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
</style>
