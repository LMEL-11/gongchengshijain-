<!-- 文件功能：封装省市区三级选择器，向父组件同步选中的区域值。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  cities: { // 声明cities字段，作为组件配置、请求参数或图表数据的一部分。
    type: Array, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: () => [], // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  districts: { // 声明districts字段，作为组件配置、请求参数或图表数据的一部分。
    type: Array, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: () => [], // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  province: { // 声明province字段，作为组件配置、请求参数或图表数据的一部分。
    type: String, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: '', // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  cityId: { // 声明cityId字段，作为组件配置、请求参数或图表数据的一部分。
    type: Number, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: null, // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  districtId: { // 声明districtId字段，作为组件配置、请求参数或图表数据的一部分。
    type: Number, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: null, // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  size: { // 声明size字段，作为组件配置、请求参数或图表数据的一部分。
    type: String, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: 'default', // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  districtClearable: { // 声明districtClearable字段，作为组件配置、请求参数或图表数据的一部分。
    type: Boolean, // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    default: true, // 声明default字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。

const emit = defineEmits(['update:province', 'update:cityId', 'update:districtId']) // 保存emit相关业务数据，作为后续计算、渲染或请求的输入。

// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 基于响应式数据派生provinces，用于保持界面展示与数据状态同步。
  const seen = new Set() // 保存seen相关业务数据，作为后续计算、渲染或请求的输入。
  const result = [] // 保存result相关业务数据，作为后续计算、渲染或请求的输入。
  for (const city of props.cities) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    const province = city.province || '其他' // 保存province相关业务数据，作为后续计算、渲染或请求的输入。
    if (!seen.has(province)) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      seen.add(province) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      result.push(province) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return result.sort() // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 基于响应式数据派生filteredCities，用于保持界面展示与数据状态同步。
  if (!props.province) return [] // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return props.cities.filter((city) => (city.province || '其他') === props.province) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理省份变化并重置下级选择。
function handleProvinceChange(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  emit('update:province', value || '') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  emit('update:cityId', null) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  emit('update:districtId', null) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理城市变化并重置区域选择。
function handleCityChange(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  emit('update:cityId', value || null) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  emit('update:districtId', null) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：处理区域变化并同步给父组件。
function handleDistrictChange(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  emit('update:districtId', value || null) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <div class="region-selector">
    <el-select
      :model-value="province"
      :size="size"
      class="region-select province-select"
      placeholder="省份"
      @update:model-value="handleProvinceChange"
    >
      <template #prefix><el-icon><Location /></el-icon></template>
      <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
    </el-select>

    <el-select
      :model-value="cityId"
      :size="size"
      class="region-select city-select"
      placeholder="城市"
      :disabled="!province"
      @update:model-value="handleCityChange"
    >
      <el-option v-for="c in filteredCities" :key="c.id" :label="c.name" :value="c.id" />
    </el-select>

    <el-select
      :model-value="districtId"
      :size="size"
      class="region-select district-select"
      placeholder="区域"
      :disabled="!cityId"
      :clearable="districtClearable"
      @update:model-value="handleDistrictChange"
    >
      <el-option v-for="d in districts" :key="d.id" :label="d.name" :value="d.id" />
    </el-select>
  </div>
</template>

<style scoped>
.region-selector { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  flex-wrap: wrap; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.region-select { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 0 0 auto; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.province-select { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 150px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.city-select { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 130px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.district-select { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 140px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
@media (max-width: 640px) { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  .region-selector { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
  .region-select { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
