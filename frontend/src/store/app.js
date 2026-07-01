// 文件功能：维护城市列表、当前城市和基础应用状态。
import { defineStore } from 'pinia' // 导入 { defineStore }，供当前前端模块渲染或交互逻辑使用。
import { ref } from 'vue' // 导入 { ref }，供当前前端模块渲染或交互逻辑使用。

import { getCities } from '@/api' // 导入 { getCities }，供当前前端模块渲染或交互逻辑使用。

export const useAppStore = defineStore('app', () => { // 导出 useAppStore 方法或状态，供其他页面和组件调用。
  const cities = ref([]) // 创建 cities，用于保存页面状态、计算结果或接口参数。
  const currentCityId = ref(1) // 创建 currentCityId，用于保存页面状态、计算结果或接口参数。
  const loaded = ref(false) // 创建 loaded，用于保存页面状态、计算结果或接口参数。

  // 函数功能：加载城市列表并初始化当前城市。
  async function loadCities() { // 定义 loadCities 函数，处理页面交互、数据加载或状态同步。
    if (loaded.value) return // 根据当前页面状态或接口结果决定是否进入该分支。
    cities.value = await getCities() // 更新 cities.value 响应式状态，让页面展示与最新数据保持一致。
    loaded.value = true // 更新 loaded.value 响应式状态，让页面展示与最新数据保持一致。
    if (cities.value.length && !cities.value.find((c) => c.id === currentCityId.value)) { // 根据当前页面状态或接口结果决定是否进入该分支。
      currentCityId.value = cities.value[0].id // 更新 currentCityId.value 响应式状态，让页面展示与最新数据保持一致。
    } // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。

  // 函数功能：更新当前选中的城市编号。
  function setCity(id) { // 定义 setCity 函数，处理页面交互、数据加载或状态同步。
    currentCityId.value = id // 更新 currentCityId.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。

  return { cities, currentCityId, loaded, loadCities, setCity } // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。
