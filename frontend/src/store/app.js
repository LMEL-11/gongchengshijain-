// 文件功能：维护城市列表、当前城市和基础应用状态。
import { defineStore } from 'pinia' // 导入本行所需的依赖。
import { ref } from 'vue' // 导入本行所需的依赖。

import { getCities } from '@/api' // 导入本行所需的依赖。

export const useAppStore = defineStore('app', () => { // 导出当前变量、函数或配置。
  const cities = ref([]) // 声明并初始化当前变量。
  const currentCityId = ref(1) // 声明并初始化当前变量。
  const loaded = ref(false) // 声明并初始化当前变量。

  // 函数功能：加载城市列表并初始化当前城市。
  async function loadCities() { // 声明当前函数入口。
    if (loaded.value) return // 根据条件判断是否执行分支。
    cities.value = await getCities() // 赋值或更新当前变量/状态。
    loaded.value = true // 赋值或更新当前变量/状态。
    if (cities.value.length && !cities.value.find((c) => c.id === currentCityId.value)) { // 根据条件判断是否执行分支。
      currentCityId.value = cities.value[0].id // 赋值或更新当前变量/状态。
    } // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。

  // 函数功能：更新当前选中的城市编号。
  function setCity(id) { // 声明当前函数入口。
    currentCityId.value = id // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。

  return { cities, currentCityId, loaded, loadCities, setCity } // 返回当前表达式结果。
}) // 执行本行前端逻辑。
