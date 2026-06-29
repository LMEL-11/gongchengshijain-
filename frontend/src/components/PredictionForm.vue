<!-- 文件功能：提供房价预测表单，加载区域选项并提交预测参数。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { getCityDistricts, predictPrice } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAppStore } from '@/store/app' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const store = useAppStore() // 保存store相关业务数据，作为后续计算、渲染或请求的输入。
const districts = ref([]) // 创建行政区集合，用于驱动页面渲染、表单输入或接口参数。
const result = ref(null) // 创建处理结果，用于驱动页面渲染、表单输入或接口参数。
const loading = ref(false) // 创建加载状态，用于驱动页面渲染、表单输入或接口参数。

const form = reactive({ // 创建表单数据模型，用于驱动页面渲染、表单输入或接口参数。
  city_id: null, // 声明city_id字段，作为组件配置、请求参数或图表数据的一部分。
  district_id: null, // 声明district_id字段，作为组件配置、请求参数或图表数据的一部分。
  area: 90, // 声明area字段，作为组件配置、请求参数或图表数据的一部分。
  rooms: 2, // 声明rooms字段，作为组件配置、请求参数或图表数据的一部分。
  halls: 1, // 声明halls字段，作为组件配置、请求参数或图表数据的一部分。
  build_year: 2015, // 声明build_year字段，作为组件配置、请求参数或图表数据的一部分。
  floor: 8, // 声明floor字段，作为组件配置、请求参数或图表数据的一部分。
  total_floors: 18, // 声明total_floors字段，作为组件配置、请求参数或图表数据的一部分。
  has_elevator: true, // 声明has_elevator字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts(cityId) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!cityId) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  districts.value = await getCityDistricts(cityId) // 等待异步接口或资源加载完成，再继续更新页面状态。
  if (districts.value.length) form.district_id = districts.value[0].id // 根据当前状态、接口结果或用户输入选择对应交互路径。
} // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => form.city_id, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  (id) => loadDistricts(id), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

onMounted(async () => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  await store.loadCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
  form.city_id = store.currentCityId // 更新form.city_id对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：校验表单并提交预测请求。
async function onSubmit() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!form.district_id) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  loading.value = true // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    result.value = await predictPrice({ ...form }) // 等待异步接口或资源加载完成，再继续更新页面状态。
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loading.value = false // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。
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
.result { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-top: 18px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  padding: 18px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-radius: 10px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  background: linear-gradient(135deg, #eff6ff, #eef2ff); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border: 1px solid #dbeafe; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.big { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 18px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.big b { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 30px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #1d4ed8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.sub { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-top: 6px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.meta { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-top: 8px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  font-size: 12px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #64748b; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.fade-enter-active { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  transition: opacity 0.3s ease; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.fade-enter-from { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  opacity: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
