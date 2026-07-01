<!-- 文件功能：提供房价预测表单，加载区域选项并提交预测参数。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue' // 导入 { onMounted, reactive, ref, watch }，供当前前端模块渲染或交互逻辑使用。

import { getCityDistricts, predictPrice } from '@/api' // 导入 { getCityDistricts, predictPrice }，供当前前端模块渲染或交互逻辑使用。
import { useAppStore } from '@/store/app' // 导入 { useAppStore }，供当前前端模块渲染或交互逻辑使用。

const store = useAppStore() // 创建 store，用于保存页面状态、计算结果或接口参数。
const districts = ref([]) // 创建 districts，用于保存页面状态、计算结果或接口参数。
const result = ref(null) // 创建 result，用于保存页面状态、计算结果或接口参数。
const loading = ref(false) // 创建 loading，用于保存页面状态、计算结果或接口参数。

const form = reactive({ // 创建 form，用于保存页面状态、计算结果或接口参数。
  city_id: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  district_id: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  area: 90, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  rooms: 2, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  halls: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  build_year: 2015, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  floor: 8, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  total_floors: 18, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  has_elevator: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts(cityId) { // 定义 loadDistricts 函数，处理页面交互、数据加载或状态同步。
  if (!cityId) return // 根据当前页面状态或接口结果决定是否进入该分支。
  districts.value = await getCityDistricts(cityId) // 更新 districts.value 响应式状态，让页面展示与最新数据保持一致。
  if (districts.value.length) form.district_id = districts.value[0].id // 根据当前页面状态或接口结果决定是否进入该分支。
} // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => form.city_id, // 设置  的值，作为后续渲染、计算或请求的输入。
  (id) => loadDistricts(id), // 设置 id 的值，作为后续渲染、计算或请求的输入。
) // 结束当前函数、对象、数组或组件配置块。

onMounted(async () => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  form.city_id = store.currentCityId // 设置 form.city_id 的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：校验表单并提交预测请求。
async function onSubmit() { // 定义 onSubmit 函数，处理页面交互、数据加载或状态同步。
  if (!form.district_id) return // 根据当前页面状态或接口结果决定是否进入该分支。
  loading.value = true // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    result.value = await predictPrice({ ...form }) // 更新 result.value 响应式状态，让页面展示与最新数据保持一致。
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loading.value = false // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。
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
.result { /* 定义当前选择器的样式作用域。 */
  margin-top: 18px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding: 18px; /* 设置元素内边距。 */
  border-radius: 10px; /* 设置圆角半径。 */
  background: linear-gradient(135deg, #eff6ff, #eef2ff); /* 设置背景样式。 */
  border: 1px solid #dbeafe; /* 设置边框样式。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.big { /* 定义当前选择器的样式作用域。 */
  font-size: 18px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.big b { /* 定义当前选择器的样式作用域。 */
  font-size: 30px; /* 设置文字大小。 */
  color: #1d4ed8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.sub { /* 定义当前选择器的样式作用域。 */
  margin-top: 6px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  font-size: 15px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.meta { /* 定义当前选择器的样式作用域。 */
  margin-top: 8px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  font-size: 12px; /* 设置文字大小。 */
  color: #64748b; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.fade-enter-active { /* 定义当前选择器的样式作用域。 */
  transition: opacity 0.3s ease; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.fade-enter-from { /* 定义当前选择器的样式作用域。 */
  opacity: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
</style>
