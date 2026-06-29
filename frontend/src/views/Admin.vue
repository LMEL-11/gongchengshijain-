<!-- 文件功能：实现管理员房源管理页面，支持筛选、分页、新增、编辑、详情和删除。 -->
<script setup>
import { reactive, ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  adminGetProperties,
  adminCreateProperty,
  adminUpdateProperty,
  adminDeleteProperty,
  getCities,
  getCityDistricts,
} from '@/api'

const router = useRouter()

// ---------- 列表 ----------
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const loading = ref(false)

// 函数功能：按当前筛选和分页条件加载房源列表。
async function fetchList() {
  loading.value = true
  try {
    // 后台列表筛选参数和分页参数全部交给后端处理，前端只维护当前查询状态。
    const res = await adminGetProperties({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      district_id: filterDistrictId.value || undefined,
    })
    list.value = res.items
    total.value = res.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

// 函数功能：重置到第一页并执行关键词搜索。
function handleSearch() {
  page.value = 1
  fetchList()
}

// 函数功能：处理分页大小变化并重新加载列表。
function handleSizeChange(size) {
  pageSize.value = size
  page.value = 1
  fetchList()
}

onMounted(() => {
  fetchList()
  loadAllCities() // 预加载城市数据，让省市区选择器立即可用
})

// ---------- 省市区级联数据 ----------
const allCities = ref([])      // 所有城市（含 province 字段）
const selectedProvince = ref('')
const selectedCityId = ref(null)
const districts = ref([])      // 当前城市下的区

// 省份列表从城市数据中计算
// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => {
  const seen = new Set()
  const result = []
  for (const c of allCities.value) {
    const p = c.province || '其他'
    if (!seen.has(p)) {
      seen.add(p)
      result.push(p)
    }
  }
  return result.sort()
})

// 当前省份下的城市列表
// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => {
  if (!selectedProvince.value) return []
  return allCities.value.filter((c) => (c.province || '其他') === selectedProvince.value)
})

// 函数功能：加载全部城市数据，供省市区选择器使用。
async function loadAllCities() {
  if (allCities.value.length) return
  try {
    const data = await getCities()
    allCities.value = Array.isArray(data) ? data : []
  } catch {
    allCities.value = []
  }
}

// 选中省份 → 重置城市和区
watch(selectedProvince, () => {
  selectedCityId.value = null
  form.district_id = null
  districts.value = []
})

// 选中城市 → 加载该城市下的区
watch(selectedCityId, async (cityId) => {
  form.district_id = null
  districts.value = []
  if (!cityId) return
  try {
    districts.value = await getCityDistricts(cityId)
  } catch {
    districts.value = []
  }
})

// ---------- 顶部工具栏省市区筛选（独立于对话框） ----------
const filterProvince = ref('')
const filterCityId = ref(null)
const filterDistrictId = ref(null)
const filterDistricts = ref([])

// 函数功能：根据筛选省份计算筛选城市列表。
const filterCities = computed(() => {
  if (!filterProvince.value) return []
  return allCities.value.filter((c) => (c.province || '其他') === filterProvince.value)
})

watch(filterProvince, () => {
  filterCityId.value = null
  filterDistrictId.value = null
  filterDistricts.value = []
})

watch(filterCityId, async (cityId) => {
  filterDistrictId.value = null
  filterDistricts.value = []
  if (!cityId) return
  try {
    filterDistricts.value = await getCityDistricts(cityId)
  } catch {
    filterDistricts.value = []
  }
})

watch(filterDistrictId, () => {
  page.value = 1
  fetchList()
})

// ---------- 新增 / 编辑 ----------
const dialogVisible = ref(false)
const dialogTitle = ref('新增房源')
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)
const submitting = ref(false)

// 函数功能：返回新增或编辑房源表单的默认数据结构。
function defaultForm() {
  return {
    district_id: null,
    title: '',
    total_price: undefined,
    unit_price: undefined,
    area: undefined,
    rooms: 0,
    halls: 0,
    floor: undefined,
    total_floors: undefined,
    build_year: undefined,
    orientation: '',
    decoration: '',
    has_elevator: false,
    listing_type: '二手房',
    lng: undefined,
    lat: undefined,
    source: 'manual',
    source_url: '',
    listing_date: '',
    ownership_type: '',
    property_right: '',
    mortgage: '',
    selling_point: '',
    community_intro: '',
    layout_intro: '',
    transport_intro: '',
  }
}

const form = reactive(defaultForm())

const decorationOptions = ['毛坯', '简装', '精装', '豪装', '其他']
const orientationOptions = [
  '南北', '南', '北', '东西', '东', '西', '东南', '西南', '东北', '西北',
]
const listingTypeOptions = ['二手房', '新房', '出租']
const ownershipTypeOptions = ['商品房', '已购公房', '经济适用房', '央产房', '私产', '其他']
const propertyRightOptions = ['非共有', '共有']
const mortgageOptions = ['无抵押', '有抵押', '有抵押业主自还', '有抵押客户偿还', '其他']

const formRules = {
  title: [{ required: true, message: '请输入房源标题', trigger: 'blur' }],
  district_id: [{ required: true, message: '请选择区域', trigger: 'change' }],
}

// 函数功能：打开新增房源对话框并重置表单状态。
async function openCreate() {
  await loadAllCities()
  dialogTitle.value = '新增房源'
  isEdit.value = false
  editId.value = null
  Object.assign(form, defaultForm())
  selectedProvince.value = ''
  selectedCityId.value = null
  districts.value = []
  dialogVisible.value = true
}

// 函数功能：打开编辑房源对话框并回填当前行数据。
async function openEdit(row) {
  await loadAllCities()
  dialogTitle.value = '编辑房源'
  isEdit.value = true
  editId.value = row.id

  // 填充表单数据：房源主体字段来自 Property，交易扩展字段来自 transaction。
  const t = row.transaction || {}
  Object.assign(form, {
    district_id: row.district_id,
    title: row.title,
    total_price: row.total_price,
    unit_price: row.unit_price,
    area: row.area,
    rooms: row.rooms ?? 0,
    halls: row.halls ?? 0,
    floor: row.floor,
    total_floors: row.total_floors,
    build_year: row.build_year,
    orientation: row.orientation || '',
    decoration: row.decoration || '',
    has_elevator: row.has_elevator ?? false,
    listing_type: row.listing_type || '二手房',
    lng: row.lng,
    lat: row.lat,
    source: row.source || 'manual',
    source_url: row.source_url || '',
    listing_date: t.listing_date || '',
    ownership_type: t.ownership_type || '',
    property_right: t.property_right || '',
    mortgage: t.mortgage || '',
    selling_point: t.selling_point || '',
    community_intro: t.community_intro || '',
    layout_intro: t.layout_intro || '',
    transport_intro: t.transport_intro || '',
  })

  // 根据 district_id 反查省/市/区并级联
  selectedProvince.value = ''
  selectedCityId.value = null
  districts.value = []

  if (!row.district_id) {
    dialogVisible.value = true
    return
  }

  // 遍历所有城市找到包含该区的那一个
  for (const c of allCities.value) {
    try {
      const dists = await getCityDistricts(c.id)
      const found = dists.find((d) => d.id === row.district_id)
      if (found) {
        selectedProvince.value = c.province || '其他'
        selectedCityId.value = c.id
        districts.value = dists
        await nextTick()
        form.district_id = row.district_id
        break
      }
    } catch {
      // continue trying other cities
    }
  }

  dialogVisible.value = true
}

// 函数功能：跳转到房源详情页面。
function openDetail(row) {
  if (!row?.id) return
  router.push({ name: 'property-detail', params: { id: row.id } })
}

// 函数功能：校验并提交新增或编辑房源表单。
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  const payload = { ...form }
  // 清理空字符串：用 null 表达“未填写”，方便后端删除或跳过交易扩展字段。
  if (payload.orientation === '') payload.orientation = null
  if (payload.decoration === '') payload.decoration = null
  if (payload.source_url === '') payload.source_url = null
  for (const field of [
    'listing_date',
    'ownership_type',
    'property_right',
    'mortgage',
    'selling_point',
    'community_intro',
    'layout_intro',
    'transport_intro',
  ]) {
    if (payload[field] === '') payload[field] = null
  }

  try {
    let savedProperty = null
    if (isEdit.value) {
      savedProperty = await adminUpdateProperty(editId.value, payload)
      ElMessage.success('房源已更新')
    } else {
      savedProperty = await adminCreateProperty(payload)
      ElMessage.success('房源已创建')
    }
    dialogVisible.value = false
    fetchList()

    if (!isEdit.value && savedProperty?.id) {
      ElMessageBox.confirm('房源已创建，是否立即查看详情页？', '创建成功', {
        type: 'success',
        confirmButtonText: '查看详情',
        cancelButtonText: '继续管理',
      })
        .then(() => openDetail(savedProperty))
        .catch(() => {})
    }
  } catch {
    // handled by interceptor
  } finally {
    submitting.value = false
  }
}

// 函数功能：确认后删除指定房源并刷新列表。
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除房源「${row.title}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' },
    )
    await adminDeleteProperty(row.id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    // cancelled or error
  }
}

// ---------- 表格格式化 ----------
// 函数功能：格式化总价展示文本。
function formatPrice(val) {
  if (val == null) return '-'
  return `${val} 万`
}
// 函数功能：格式化单价展示文本。
function formatUnitPrice(val) {
  if (val == null) return '-'
  return `${val} 元/㎡`
}
// 函数功能：格式化面积展示文本。
function formatArea(val) {
  if (val == null) return '-'
  return `${val} ㎡`
}
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
.admin-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  color: #1e3a8a;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
