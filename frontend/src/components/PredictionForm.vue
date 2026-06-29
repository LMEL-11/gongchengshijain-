<!-- 文件功能：提供房价预测表单，加载区域选项并提交预测参数。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue' // 导入本行所需的依赖。

import { getCityDistricts, predictPrice } from '@/api' // 导入本行所需的依赖。
import { useAppStore } from '@/store/app' // 导入本行所需的依赖。

const store = useAppStore() // 声明并初始化当前变量。
const districts = ref([]) // 声明并初始化当前变量。
const result = ref(null) // 声明并初始化当前变量。
const loading = ref(false) // 声明并初始化当前变量。

const form = reactive({ // 声明并初始化当前变量。
  city_id: null, // 配置当前对象字段。
  district_id: null, // 配置当前对象字段。
  area: 90, // 配置当前对象字段。
  rooms: 2, // 配置当前对象字段。
  halls: 1, // 配置当前对象字段。
  build_year: 2015, // 配置当前对象字段。
  floor: 8, // 配置当前对象字段。
  total_floors: 18, // 配置当前对象字段。
  has_elevator: true, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts(cityId) { // 声明当前函数入口。
  if (!cityId) return // 根据条件判断是否执行分支。
  districts.value = await getCityDistricts(cityId) // 赋值或更新当前变量/状态。
  if (districts.value.length) form.district_id = districts.value[0].id // 根据条件判断是否执行分支。
} // 结束当前代码块或数据结构。

watch( // 监听响应式数据变化。
  () => form.city_id, // 继续声明当前列表项或参数项。
  (id) => loadDistricts(id), // 继续声明当前列表项或参数项。
) // 结束当前代码块或数据结构。

onMounted(async () => { // 注册 Vue 生命周期回调。
  await store.loadCities() // 等待异步操作完成。
  form.city_id = store.currentCityId // 赋值或更新当前变量/状态。
}) // 执行本行前端逻辑。

// 函数功能：校验表单并提交预测请求。
async function onSubmit() { // 声明当前函数入口。
  if (!form.district_id) return // 根据条件判断是否执行分支。
  loading.value = true // 赋值或更新当前变量/状态。
  try { // 开始执行可能失败的逻辑。
    result.value = await predictPrice({ ...form }) // 赋值或更新当前变量/状态。
  } finally { // 执行本行前端逻辑。
    loading.value = false // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。
</script>

<template>
  <div class="predict">
    <el-form :model="form" label-width="92px" label-position="left">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="城市">
            <el-select v-model="form.city_id" placeholder="选择城市" style="width: 100%">
              <el-option v-for="c in store.cities" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="行政区">
            <el-select v-model="form.district_id" placeholder="选择行政区" style="width: 100%">
              <el-option v-for="d in districts" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="建筑面积">
            <el-input-number v-model="form.area" :min="15" :max="500" :step="5" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="建成年份">
            <el-input-number v-model="form.build_year" :min="1980" :max="2026" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="室">
            <el-input-number v-model="form.rooms" :min="1" :max="6" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="厅">
            <el-input-number v-model="form.halls" :min="0" :max="4" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="所在楼层">
            <el-input-number v-model="form.floor" :min="1" :max="form.total_floors" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="总楼层">
            <el-input-number v-model="form.total_floors" :min="1" :max="80" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电梯">
            <el-switch v-model="form.has_elevator" active-text="有" inactive-text="无" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-button type="primary" :loading="loading" style="width: 100%" @click="onSubmit">
        <el-icon style="margin-right: 6px"><MagicStick /></el-icon>预测房价
      </el-button>
    </el-form>

    <transition name="fade">
      <div v-if="result" class="result">
        <div class="big">
          预测总价 <b>{{ result.total_price }}</b> 万元
        </div>
        <div class="sub">
          预测单价 <b class="price-text">{{ result.unit_price.toLocaleString() }}</b> 元/㎡
        </div>
        <div class="meta">
          {{ result.district_name }} · 区域均价
          {{ result.district_avg_unit_price?.toLocaleString() || '-' }} 元/㎡ ·
          模型：{{ result.method === 'district_random_forest' ? '行政区随机森林' : '启发式估算' }}
          <template v-if="result.training_sample_count">
            · 样本 {{ result.training_sample_count.toLocaleString() }} 条
          </template>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.result { /* 开始当前样式规则块。 */
  margin-top: 18px; /* 设置当前样式属性。 */
  padding: 18px; /* 设置当前样式属性。 */
  border-radius: 10px; /* 设置当前样式属性。 */
  background: linear-gradient(135deg, #eff6ff, #eef2ff); /* 设置当前样式属性。 */
  border: 1px solid #dbeafe; /* 设置当前样式属性。 */
  text-align: center; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.big { /* 开始当前样式规则块。 */
  font-size: 18px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.big b { /* 开始当前样式规则块。 */
  font-size: 30px; /* 设置当前样式属性。 */
  color: #1d4ed8; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.sub { /* 开始当前样式规则块。 */
  margin-top: 6px; /* 设置当前样式属性。 */
  font-size: 15px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.meta { /* 开始当前样式规则块。 */
  margin-top: 8px; /* 设置当前样式属性。 */
  font-size: 12px; /* 设置当前样式属性。 */
  color: #64748b; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.fade-enter-active { /* 开始当前样式规则块。 */
  transition: opacity 0.3s ease; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.fade-enter-from { /* 开始当前样式规则块。 */
  opacity: 0; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
</style>
