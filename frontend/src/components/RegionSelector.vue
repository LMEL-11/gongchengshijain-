<!-- 文件功能：封装省市区三级选择器，向父组件同步选中的区域值。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  cities: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: Array, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: () => [], // 设置 default:  的值，作为后续渲染、计算或请求的输入。
  }, // 结束当前函数、对象、数组或组件配置块。
  districts: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: Array, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: () => [], // 设置 default:  的值，作为后续渲染、计算或请求的输入。
  }, // 结束当前函数、对象、数组或组件配置块。
  province: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: String, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  cityId: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: Number, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  districtId: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: Number, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: null, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  size: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: String, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: 'default', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  districtClearable: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: Boolean, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    default: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。

const emit = defineEmits(['update:province', 'update:cityId', 'update:districtId']) // 创建 emit，用于保存页面状态、计算结果或接口参数。

// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 创建 provinces，用于保存页面状态、计算结果或接口参数。
  const seen = new Set() // 创建 seen，用于保存页面状态、计算结果或接口参数。
  const result = [] // 创建 result，用于保存页面状态、计算结果或接口参数。
  for (const city of props.cities) { // 遍历当前数据集合，逐项生成页面需要的数据。
    const province = city.province || '其他' // 创建 province，用于保存页面状态、计算结果或接口参数。
    if (!seen.has(province)) { // 根据当前页面状态或接口结果决定是否进入该分支。
      seen.add(province) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      result.push(province) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
  return result.sort() // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 创建 filteredCities，用于保存页面状态、计算结果或接口参数。
  if (!props.province) return [] // 根据当前页面状态或接口结果决定是否进入该分支。
  return props.cities.filter((city) => (city.province || '其他') === props.province) // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理省份变化并重置下级选择。
function handleProvinceChange(value) { // 定义 handleProvinceChange 函数，处理页面交互、数据加载或状态同步。
  emit('update:province', value || '') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  emit('update:cityId', null) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  emit('update:districtId', null) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理城市变化并重置区域选择。
function handleCityChange(value) { // 定义 handleCityChange 函数，处理页面交互、数据加载或状态同步。
  emit('update:cityId', value || null) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  emit('update:districtId', null) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：处理区域变化并同步给父组件。
function handleDistrictChange(value) { // 定义 handleDistrictChange 函数，处理页面交互、数据加载或状态同步。
  emit('update:districtId', value || null) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。
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
.region-selector { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 10px; /* 设置子元素之间的间距。 */
  flex-wrap: wrap; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.region-select { /* 定义当前选择器的样式作用域。 */
  flex: 0 0 auto; /* 设置弹性布局占比。 */
} /* 结束当前样式规则块。 */
.province-select { /* 定义当前选择器的样式作用域。 */
  width: 150px; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */
.city-select { /* 定义当前选择器的样式作用域。 */
  width: 130px; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */
.district-select { /* 定义当前选择器的样式作用域。 */
  width: 140px; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */
@media (max-width: 640px) { /* 定义当前选择器的样式作用域。 */
  .region-selector { /* 定义当前选择器的样式作用域。 */
    width: 100%; /* 设置元素宽度。 */
  } /* 结束当前样式规则块。 */
  .region-select { /* 定义当前选择器的样式作用域。 */
    width: 100%; /* 设置元素宽度。 */
  } /* 结束当前样式规则块。 */
} /* 结束当前样式规则块。 */
</style>
