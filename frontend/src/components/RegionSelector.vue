<!-- 文件功能：封装省市区三级选择器，向父组件同步选中的区域值。 -->
<script setup>
import { computed } from 'vue' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  cities: { // 逐行注释：配置当前对象字段。
    type: Array, // 逐行注释：配置当前对象字段。
    default: () => [], // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  districts: { // 逐行注释：配置当前对象字段。
    type: Array, // 逐行注释：配置当前对象字段。
    default: () => [], // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  province: { // 逐行注释：配置当前对象字段。
    type: String, // 逐行注释：配置当前对象字段。
    default: '', // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  cityId: { // 逐行注释：配置当前对象字段。
    type: Number, // 逐行注释：配置当前对象字段。
    default: null, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  districtId: { // 逐行注释：配置当前对象字段。
    type: Number, // 逐行注释：配置当前对象字段。
    default: null, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  size: { // 逐行注释：配置当前对象字段。
    type: String, // 逐行注释：配置当前对象字段。
    default: 'default', // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  districtClearable: { // 逐行注释：配置当前对象字段。
    type: Boolean, // 逐行注释：配置当前对象字段。
    default: true, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
}) // 逐行注释：执行本行前端逻辑。

const emit = defineEmits(['update:province', 'update:cityId', 'update:districtId']) // 逐行注释：声明并初始化当前变量。

// 函数功能：从城市列表中计算可选省份列表。
const provinces = computed(() => { // 逐行注释：声明并初始化当前变量。
  const seen = new Set() // 逐行注释：声明并初始化当前变量。
  const result = [] // 逐行注释：声明并初始化当前变量。
  for (const city of props.cities) { // 逐行注释：遍历集合或范围并逐项处理。
    const province = city.province || '其他' // 逐行注释：声明并初始化当前变量。
    if (!seen.has(province)) { // 逐行注释：根据条件判断是否执行分支。
      seen.add(province) // 逐行注释：执行本行前端逻辑。
      result.push(province) // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
  } // 逐行注释：结束当前代码块或数据结构。
  return result.sort() // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：根据当前省份筛选可选城市。
const filteredCities = computed(() => { // 逐行注释：声明并初始化当前变量。
  if (!props.province) return [] // 逐行注释：根据条件判断是否执行分支。
  return props.cities.filter((city) => (city.province || '其他') === props.province) // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：处理省份变化并重置下级选择。
function handleProvinceChange(value) { // 逐行注释：声明当前函数入口。
  emit('update:province', value || '') // 逐行注释：向父组件派发事件。
  emit('update:cityId', null) // 逐行注释：向父组件派发事件。
  emit('update:districtId', null) // 逐行注释：向父组件派发事件。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理城市变化并重置区域选择。
function handleCityChange(value) { // 逐行注释：声明当前函数入口。
  emit('update:cityId', value || null) // 逐行注释：向父组件派发事件。
  emit('update:districtId', null) // 逐行注释：向父组件派发事件。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：处理区域变化并同步给父组件。
function handleDistrictChange(value) { // 逐行注释：声明当前函数入口。
  emit('update:districtId', value || null) // 逐行注释：向父组件派发事件。
} // 逐行注释：结束当前代码块或数据结构。
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
.region-selector { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 10px; /* 逐行注释：设置当前样式属性。 */
  flex-wrap: wrap; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.region-select { /* 逐行注释：开始当前样式规则块。 */
  flex: 0 0 auto; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.province-select { /* 逐行注释：开始当前样式规则块。 */
  width: 150px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.city-select { /* 逐行注释：开始当前样式规则块。 */
  width: 130px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.district-select { /* 逐行注释：开始当前样式规则块。 */
  width: 140px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
@media (max-width: 640px) { /* 逐行注释：声明响应式媒体查询规则。 */
  .region-selector { /* 逐行注释：开始当前样式规则块。 */
    width: 100%; /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
  .region-select { /* 逐行注释：开始当前样式规则块。 */
    width: 100%; /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
