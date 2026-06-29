<!-- 文件功能：封装省市区三级选择器，向父组件同步选中的区域值。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  cities: { // 配置当前对象字段。
    type: Array, // 配置当前对象字段。
    default: () => [], // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  districts: { // 配置当前对象字段。
    type: Array, // 配置当前对象字段。
    default: () => [], // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  province: { // 配置当前对象字段。
    type: String, // 配置当前对象字段。
    default: '', // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  cityId: { // 配置当前对象字段。
    type: Number, // 配置当前对象字段。
    default: null, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  districtId: { // 配置当前对象字段。
    type: Number, // 配置当前对象字段。
    default: null, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  size: { // 配置当前对象字段。
    type: String, // 配置当前对象字段。
    default: 'default', // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  districtClearable: { // 配置当前对象字段。
    type: Boolean, // 配置当前对象字段。
    default: true, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。

const emit = defineEmits(['update:province', 'update:cityId', 'update:districtId']) // 声明并初始化当前变量。

// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 声明并初始化当前变量。
  const seen = new Set() // 声明并初始化当前变量。
  const result = [] // 声明并初始化当前变量。
  for (const city of props.cities) { // 遍历集合或范围并逐项处理。
    const province = city.province || '其他' // 声明并初始化当前变量。
    if (!seen.has(province)) { // 根据条件判断是否执行分支。
      seen.add(province) // 执行本行前端逻辑。
      result.push(province) // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。
  return result.sort() // 返回当前表达式结果。
}) // 执行本行前端逻辑。

// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 声明并初始化当前变量。
  if (!props.province) return [] // 根据条件判断是否执行分支。
  return props.cities.filter((city) => (city.province || '其他') === props.province) // 返回当前表达式结果。
}) // 执行本行前端逻辑。

// 函数功能：处理省份变化并重置下级选择。
function handleProvinceChange(value) { // 声明当前函数入口。
  emit('update:province', value || '') // 向父组件派发事件。
  emit('update:cityId', null) // 向父组件派发事件。
  emit('update:districtId', null) // 向父组件派发事件。
} // 结束当前代码块或数据结构。

// 函数功能：处理城市变化并重置区域选择。
function handleCityChange(value) { // 声明当前函数入口。
  emit('update:cityId', value || null) // 向父组件派发事件。
  emit('update:districtId', null) // 向父组件派发事件。
} // 结束当前代码块或数据结构。

// 函数功能：处理区域变化并同步给父组件。
function handleDistrictChange(value) { // 声明当前函数入口。
  emit('update:districtId', value || null) // 向父组件派发事件。
} // 结束当前代码块或数据结构。
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
.region-selector { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 10px; /* 设置当前样式属性。 */
  flex-wrap: wrap; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.region-select { /* 开始当前样式规则块。 */
  flex: 0 0 auto; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.province-select { /* 开始当前样式规则块。 */
  width: 150px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.city-select { /* 开始当前样式规则块。 */
  width: 130px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.district-select { /* 开始当前样式规则块。 */
  width: 140px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
@media (max-width: 640px) { /* 声明响应式媒体查询规则。 */
  .region-selector { /* 开始当前样式规则块。 */
    width: 100%; /* 设置当前样式属性。 */
  } /* 结束当前样式规则块。 */
  .region-select { /* 开始当前样式规则块。 */
    width: 100%; /* 设置当前样式属性。 */
  } /* 结束当前样式规则块。 */
} /* 结束当前样式规则块。 */
</style>
