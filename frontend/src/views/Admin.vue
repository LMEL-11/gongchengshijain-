<!-- 文件功能：实现管理员房源管理页面，支持筛选、分页、新增、编辑、详情和删除。 -->
<script setup>
import { reactive, ref, onMounted, computed, watch, nextTick } from 'vue' // 导入本行所需的依赖。
import { useRouter } from 'vue-router' // 导入本行所需的依赖。
import { ElMessage, ElMessageBox } from 'element-plus' // 导入本行所需的依赖。
import { // 导入本行所需的依赖。
  adminGetProperties, // 继续声明当前列表项或参数项。
  adminCreateProperty, // 继续声明当前列表项或参数项。
  adminUpdateProperty, // 继续声明当前列表项或参数项。
  adminDeleteProperty, // 继续声明当前列表项或参数项。
  getCities, // 继续声明当前列表项或参数项。
  getCityDistricts, // 继续声明当前列表项或参数项。
} from '@/api' // 执行本行前端逻辑。

const router = useRouter() // 声明并初始化当前变量。

// ---------- 列表 ----------
const list = ref([]) // 声明并初始化当前变量。
const total = ref(0) // 声明并初始化当前变量。
const page = ref(1) // 声明并初始化当前变量。
const pageSize = ref(20) // 声明并初始化当前变量。
const keyword = ref('') // 声明并初始化当前变量。
const loading = ref(false) // 声明并初始化当前变量。

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() { // 声明当前函数入口。
  loading.value = true // 赋值或更新当前变量/状态。
  try { // 开始执行可能失败的逻辑。
    const res = await adminGetProperties({ // 声明并初始化当前变量。
      page: page.value, // 配置当前对象字段。
      page_size: pageSize.value, // 配置当前对象字段。
      keyword: keyword.value || undefined, // 配置当前对象字段。
      district_id: filterDistrictId.value || undefined, // 配置当前对象字段。
    }) // 执行本行前端逻辑。
    list.value = res.items // 赋值或更新当前变量/状态。
    total.value = res.total // 赋值或更新当前变量/状态。
  } catch { // 执行本行前端逻辑。
    // handled by interceptor
  } finally { // 执行本行前端逻辑。
    loading.value = false // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// 函数功能：重置到第一页并执行关键词搜索。
function handleSearch() { // 声明当前函数入口。
  page.value = 1 // 赋值或更新当前变量/状态。
  fetchList() // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

// 函数功能：处理分页大小变化并重新加载列表。
function handleSizeChange(size) { // 声明当前函数入口。
  pageSize.value = size // 赋值或更新当前变量/状态。
  page.value = 1 // 赋值或更新当前变量/状态。
  fetchList() // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

onMounted(() => { // 注册 Vue 生命周期回调。
  fetchList() // 执行本行前端逻辑。
  loadAllCities() // 预加载城市数据，让省市区选择器立即可用
}) // 执行本行前端逻辑。

// ---------- 省市区级联数据 ----------
const allCities = ref([])      // 所有城市（含 province 字段）
const selectedProvince = ref('') // 声明并初始化当前变量。
const selectedCityId = ref(null) // 声明并初始化当前变量。
const districts = ref([])      // 当前城市下的区

// 省份列表从城市数据中计算
// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 声明并初始化当前变量。
  const seen = new Set() // 声明并初始化当前变量。
  const result = [] // 声明并初始化当前变量。
  for (const c of allCities.value) { // 遍历集合或范围并逐项处理。
    const p = c.province || '其他' // 声明并初始化当前变量。
    if (!seen.has(p)) { // 根据条件判断是否执行分支。
      seen.add(p) // 执行本行前端逻辑。
      result.push(p) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。
  return result.sort() // 返回当前表达式结果。
}) // 执行本行前端逻辑。

// 当前省份下的城市列表
// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 声明并初始化当前变量。
  if (!selectedProvince.value) return [] // 根据条件判断是否执行分支。
  return allCities.value.filter((c) => (c.province || '其他') === selectedProvince.value) // 返回当前表达式结果。
}) // 执行本行前端逻辑。

// 函数功能：加载全部城市数据，供省市区选择器使用。
async function loadAllCities() { // 声明当前函数入口。
  if (allCities.value.length) return // 根据条件判断是否执行分支。
  try { // 开始执行可能失败的逻辑。
    const data = await getCities() // 声明并初始化当前变量。
    allCities.value = Array.isArray(data) ? data : [] // 赋值或更新当前变量/状态。
  } catch { // 执行本行前端逻辑。
    allCities.value = [] // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// 选中省份 → 重置城市和区
watch(selectedProvince, () => { // 监听响应式数据变化。
  selectedCityId.value = null // 赋值或更新当前变量/状态。
  form.district_id = null // 赋值或更新当前变量/状态。
  districts.value = [] // 赋值或更新当前变量/状态。
}) // 执行本行前端逻辑。

// 选中城市 → 加载该城市下的区
watch(selectedCityId, async (cityId) => { // 监听响应式数据变化。
  form.district_id = null // 赋值或更新当前变量/状态。
  districts.value = [] // 赋值或更新当前变量/状态。
  if (!cityId) return // 根据条件判断是否执行分支。
  try { // 开始执行可能失败的逻辑。
    districts.value = await getCityDistricts(cityId) // 赋值或更新当前变量/状态。
  } catch { // 执行本行前端逻辑。
    districts.value = [] // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。

// ---------- 顶部工具栏省市区筛选（独立于对话框） ----------
const filterProvince = ref('') // 声明并初始化当前变量。
const filterCityId = ref(null) // 声明并初始化当前变量。
const filterDistrictId = ref(null) // 声明并初始化当前变量。
const filterDistricts = ref([]) // 声明并初始化当前变量。

// 函数功能：根据筛选省份计算筛选城市列表。
const filterCities = computed(() => { // 声明并初始化当前变量。
  if (!filterProvince.value) return [] // 根据条件判断是否执行分支。
  return allCities.value.filter((c) => (c.province || '其他') === filterProvince.value) // 返回当前表达式结果。
}) // 执行本行前端逻辑。

watch(filterProvince, () => { // 监听响应式数据变化。
  filterCityId.value = null // 赋值或更新当前变量/状态。
  filterDistrictId.value = null // 赋值或更新当前变量/状态。
  filterDistricts.value = [] // 赋值或更新当前变量/状态。
}) // 执行本行前端逻辑。

watch(filterCityId, async (cityId) => { // 监听响应式数据变化。
  filterDistrictId.value = null // 赋值或更新当前变量/状态。
  filterDistricts.value = [] // 赋值或更新当前变量/状态。
  if (!cityId) return // 根据条件判断是否执行分支。
  try { // 开始执行可能失败的逻辑。
    filterDistricts.value = await getCityDistricts(cityId) // 赋值或更新当前变量/状态。
  } catch { // 执行本行前端逻辑。
    filterDistricts.value = [] // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。

watch(filterDistrictId, () => { // 监听响应式数据变化。
  page.value = 1 // 赋值或更新当前变量/状态。
  fetchList() // 执行本行前端逻辑。
}) // 执行本行前端逻辑。

// ---------- 新增 / 编辑 ----------
const dialogVisible = ref(false) // 声明并初始化当前变量。
const dialogTitle = ref('新增房源') // 声明并初始化当前变量。
const isEdit = ref(false) // 声明并初始化当前变量。
const editId = ref(null) // 声明并初始化当前变量。
const formRef = ref(null) // 声明并初始化当前变量。
const submitting = ref(false) // 声明并初始化当前变量。

// 函数功能：返回新增或编辑房源表单的默认数据结构。
function defaultForm() { // 声明当前函数入口。
  return { // 返回当前表达式结果。
    district_id: null, // 配置当前对象字段。
    title: '', // 配置当前对象字段。
    total_price: undefined, // 配置当前对象字段。
    unit_price: undefined, // 配置当前对象字段。
    area: undefined, // 配置当前对象字段。
    rooms: 0, // 配置当前对象字段。
    halls: 0, // 配置当前对象字段。
    floor: undefined, // 配置当前对象字段。
    total_floors: undefined, // 配置当前对象字段。
    build_year: undefined, // 配置当前对象字段。
    orientation: '', // 配置当前对象字段。
    decoration: '', // 配置当前对象字段。
    has_elevator: false, // 配置当前对象字段。
    listing_type: '二手房', // 配置当前对象字段。
    lng: undefined, // 配置当前对象字段。
    lat: undefined, // 配置当前对象字段。
    source: 'manual', // 配置当前对象字段。
    source_url: '', // 配置当前对象字段。
    listing_date: '', // 配置当前对象字段。
    ownership_type: '', // 配置当前对象字段。
    property_right: '', // 配置当前对象字段。
    mortgage: '', // 配置当前对象字段。
    selling_point: '', // 配置当前对象字段。
    community_intro: '', // 配置当前对象字段。
    layout_intro: '', // 配置当前对象字段。
    transport_intro: '', // 配置当前对象字段。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

const form = reactive(defaultForm()) // 声明并初始化当前变量。

const decorationOptions = ['毛坯', '简装', '精装', '豪装', '其他'] // 声明并初始化当前变量。
const orientationOptions = [ // 声明并初始化当前变量。
  '南北', '南', '北', '东西', '东', '西', '东南', '西南', '东北', '西北', // 继续声明当前列表项或参数项。
] // 结束当前代码块或数据结构。
const listingTypeOptions = ['二手房', '新房', '出租'] // 声明并初始化当前变量。
const ownershipTypeOptions = ['商品房', '已购公房', '经济适用房', '央产房', '私产', '其他'] // 声明并初始化当前变量。
const propertyRightOptions = ['非共有', '共有'] // 声明并初始化当前变量。
const mortgageOptions = ['无抵押', '有抵押', '有抵押业主自还', '有抵押客户偿还', '其他'] // 声明并初始化当前变量。

const formRules = { // 声明并初始化当前变量。
  title: [{ required: true, message: '请输入房源标题', trigger: 'blur' }], // 配置当前对象字段。
  district_id: [{ required: true, message: '请选择区域', trigger: 'change' }], // 配置当前对象字段。
} // 结束当前代码块或数据结构。

// 函数功能：打开新增房源对话框并重置表单状态。
async function openCreate() { // 声明当前函数入口。
  await loadAllCities() // 等待异步操作完成。
  dialogTitle.value = '新增房源' // 赋值或更新当前变量/状态。
  isEdit.value = false // 赋值或更新当前变量/状态。
  editId.value = null // 赋值或更新当前变量/状态。
  Object.assign(form, defaultForm()) // 执行本行前端逻辑。
  selectedProvince.value = '' // 赋值或更新当前变量/状态。
  selectedCityId.value = null // 赋值或更新当前变量/状态。
  districts.value = [] // 赋值或更新当前变量/状态。
  dialogVisible.value = true // 赋值或更新当前变量/状态。
} // 结束当前代码块或数据结构。

// 函数功能：打开编辑房源对话框并回填当前行数据。
async function openEdit(row) { // 声明当前函数入口。
  await loadAllCities() // 等待异步操作完成。
  dialogTitle.value = '编辑房源' // 赋值或更新当前变量/状态。
  isEdit.value = true // 赋值或更新当前变量/状态。
  editId.value = row.id // 赋值或更新当前变量/状态。

  // 填充表单数据
  const t = row.transaction || {} // 声明并初始化当前变量。
  Object.assign(form, { // 执行本行前端逻辑。
    district_id: row.district_id, // 配置当前对象字段。
    title: row.title, // 配置当前对象字段。
    total_price: row.total_price, // 配置当前对象字段。
    unit_price: row.unit_price, // 配置当前对象字段。
    area: row.area, // 配置当前对象字段。
    rooms: row.rooms ?? 0, // 配置当前对象字段。
    halls: row.halls ?? 0, // 配置当前对象字段。
    floor: row.floor, // 配置当前对象字段。
    total_floors: row.total_floors, // 配置当前对象字段。
    build_year: row.build_year, // 配置当前对象字段。
    orientation: row.orientation || '', // 配置当前对象字段。
    decoration: row.decoration || '', // 配置当前对象字段。
    has_elevator: row.has_elevator ?? false, // 配置当前对象字段。
    listing_type: row.listing_type || '二手房', // 配置当前对象字段。
    lng: row.lng, // 配置当前对象字段。
    lat: row.lat, // 配置当前对象字段。
    source: row.source || 'manual', // 配置当前对象字段。
    source_url: row.source_url || '', // 配置当前对象字段。
    listing_date: t.listing_date || '', // 配置当前对象字段。
    ownership_type: t.ownership_type || '', // 配置当前对象字段。
    property_right: t.property_right || '', // 配置当前对象字段。
    mortgage: t.mortgage || '', // 配置当前对象字段。
    selling_point: t.selling_point || '', // 配置当前对象字段。
    community_intro: t.community_intro || '', // 配置当前对象字段。
    layout_intro: t.layout_intro || '', // 配置当前对象字段。
    transport_intro: t.transport_intro || '', // 配置当前对象字段。
  }) // 执行本行前端逻辑。

  // 根据 district_id 反查省/市/区并级联
  selectedProvince.value = '' // 赋值或更新当前变量/状态。
  selectedCityId.value = null // 赋值或更新当前变量/状态。
  districts.value = [] // 赋值或更新当前变量/状态。

  if (!row.district_id) { // 根据条件判断是否执行分支。
    dialogVisible.value = true // 赋值或更新当前变量/状态。
    return // 返回当前表达式结果。
  } // 结束当前代码块或数据结构。

  // 遍历所有城市找到包含该区的那一个
  for (const c of allCities.value) { // 遍历集合或范围并逐项处理。
    try { // 开始执行可能失败的逻辑。
      const dists = await getCityDistricts(c.id) // 声明并初始化当前变量。
      const found = dists.find((d) => d.id === row.district_id) // 声明并初始化当前变量。
      if (found) { // 根据条件判断是否执行分支。
        selectedProvince.value = c.province || '其他' // 赋值或更新当前变量/状态。
        selectedCityId.value = c.id // 赋值或更新当前变量/状态。
        districts.value = dists // 赋值或更新当前变量/状态。
        await nextTick() // 等待异步操作完成。
        form.district_id = row.district_id // 赋值或更新当前变量/状态。
        break // 执行本行前端逻辑。
      } // 结束当前代码块或数据结构。
    } catch { // 执行本行前端逻辑。
      // continue trying other cities
    } // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。

  dialogVisible.value = true // 赋值或更新当前变量/状态。
} // 结束当前代码块或数据结构。

// 函数功能：跳转到房源详情页面。
function openDetail(row) { // 声明当前函数入口。
  if (!row?.id) return // 根据条件判断是否执行分支。
  router.push({ name: 'property-detail', params: { id: row.id } }) // 执行路由跳转或路由操作。
} // 结束当前代码块或数据结构。

// 函数功能：校验并提交新增或编辑房源表单。
async function handleSubmit() { // 声明当前函数入口。
  const valid = await formRef.value.validate().catch(() => false) // 声明并初始化当前变量。
  if (!valid) return // 根据条件判断是否执行分支。

  submitting.value = true // 赋值或更新当前变量/状态。
  const payload = { ...form } // 声明并初始化当前变量。
  // 清理空字符串
  if (payload.orientation === '') payload.orientation = null // 根据条件判断是否执行分支。
  if (payload.decoration === '') payload.decoration = null // 根据条件判断是否执行分支。
  if (payload.source_url === '') payload.source_url = null // 根据条件判断是否执行分支。
  for (const field of [ // 遍历集合或范围并逐项处理。
    'listing_date', // 继续声明当前列表项或参数项。
    'ownership_type', // 继续声明当前列表项或参数项。
    'property_right', // 继续声明当前列表项或参数项。
    'mortgage', // 继续声明当前列表项或参数项。
    'selling_point', // 继续声明当前列表项或参数项。
    'community_intro', // 继续声明当前列表项或参数项。
    'layout_intro', // 继续声明当前列表项或参数项。
    'transport_intro', // 继续声明当前列表项或参数项。
  ]) { // 执行本行前端逻辑。
    if (payload[field] === '') payload[field] = null // 根据条件判断是否执行分支。
  } // 结束当前代码块或数据结构。

  try { // 开始执行可能失败的逻辑。
    let savedProperty = null // 声明并初始化当前变量。
    if (isEdit.value) { // 根据条件判断是否执行分支。
      savedProperty = await adminUpdateProperty(editId.value, payload) // 赋值或更新当前变量/状态。
      ElMessage.success('房源已更新') // 执行本行前端逻辑。
    } else { // 执行本行前端逻辑。
      savedProperty = await adminCreateProperty(payload) // 赋值或更新当前变量/状态。
      ElMessage.success('房源已创建') // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
    dialogVisible.value = false // 赋值或更新当前变量/状态。
    fetchList() // 执行本行前端逻辑。

    if (!isEdit.value && savedProperty?.id) { // 根据条件判断是否执行分支。
      ElMessageBox.confirm('房源已创建，是否立即查看详情页？', '创建成功', { // 执行本行前端逻辑。
        type: 'success', // 配置当前对象字段。
        confirmButtonText: '查看详情', // 配置当前对象字段。
        cancelButtonText: '继续管理', // 配置当前对象字段。
      }) // 执行本行前端逻辑。
        .then(() => openDetail(savedProperty)) // 执行本行前端逻辑。
        .catch(() => {}) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
  } catch { // 执行本行前端逻辑。
    // handled by interceptor
  } finally { // 执行本行前端逻辑。
    submitting.value = false // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// 函数功能：确认后删除指定房源并刷新列表。
async function handleDelete(row) { // 声明当前函数入口。
  try { // 开始执行可能失败的逻辑。
    await ElMessageBox.confirm( // 等待异步操作完成。
      `确定要删除房源「${row.title}」吗？删除后不可恢复。`, // 继续声明当前列表项或参数项。
      '删除确认', // 继续声明当前列表项或参数项。
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }, // 配置当前对象字段。
    ) // 结束当前代码块或数据结构。
    await adminDeleteProperty(row.id) // 等待异步操作完成。
    ElMessage.success('已删除') // 执行本行前端逻辑。
    fetchList() // 执行本行前端逻辑。
  } catch { // 执行本行前端逻辑。
    // cancelled or error
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。

// ---------- 表格格式化 ----------
// 函数功能：格式化总价展示文本。
function formatPrice(val) { // 声明当前函数入口。
  if (val == null) return '-' // 根据条件判断是否执行分支。
  return `${val} 万` // 返回当前表达式结果。
} // 结束当前代码块或数据结构。
// 函数功能：格式化单价展示文本。
function formatUnitPrice(val) { // 声明当前函数入口。
  if (val == null) return '-' // 根据条件判断是否执行分支。
  return `${val} 元/㎡` // 返回当前表达式结果。
} // 结束当前代码块或数据结构。
// 函数功能：格式化面积展示文本。
function formatArea(val) { // 声明当前函数入口。
  if (val == null) return '-' // 根据条件判断是否执行分支。
  return `${val} ㎡` // 返回当前表达式结果。
} // 结束当前代码块或数据结构。
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
.admin-page { /* 开始当前样式规则块。 */
  max-width: 1280px; /* 设置当前样式属性。 */
  margin: 0 auto; /* 设置当前样式属性。 */
  padding: 24px 20px 40px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.page-header { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: space-between; /* 设置当前样式属性。 */
  margin-bottom: 20px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.page-header h2 { /* 开始当前样式规则块。 */
  margin: 0; /* 设置当前样式属性。 */
  font-size: 22px; /* 设置当前样式属性。 */
  color: #1e3a8a; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.toolbar { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  gap: 12px; /* 设置当前样式属性。 */
  margin-bottom: 16px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.pagination-wrap { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  justify-content: flex-end; /* 设置当前样式属性。 */
  margin-top: 16px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
</style>
