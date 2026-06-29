// 文件功能：维护城市列表、当前城市和基础应用状态。
import { defineStore } from 'pinia' // 逐行注释：导入本行所需的依赖。
import { ref } from 'vue' // 逐行注释：导入本行所需的依赖。

import { getCities } from '@/api' // 逐行注释：导入本行所需的依赖。

export const useAppStore = defineStore('app', () => { // 逐行注释：导出当前变量、函数或配置。
  const cities = ref([]) // 逐行注释：声明并初始化当前变量。
  const currentCityId = ref(1) // 逐行注释：声明并初始化当前变量。
  const loaded = ref(false) // 逐行注释：声明并初始化当前变量。

  // 函数功能：加载城市列表并初始化当前城市。
  async function loadCities() { // 逐行注释：声明当前函数入口。
    if (loaded.value) return // 逐行注释：根据条件判断是否执行分支。
    cities.value = await getCities() // 逐行注释：赋值或更新当前变量/状态。
    loaded.value = true // 逐行注释：赋值或更新当前变量/状态。
    if (cities.value.length && !cities.value.find((c) => c.id === currentCityId.value)) { // 逐行注释：根据条件判断是否执行分支。
      currentCityId.value = cities.value[0].id // 逐行注释：赋值或更新当前变量/状态。
    } // 逐行注释：结束当前代码块或数据结构。
  } // 逐行注释：结束当前代码块或数据结构。

  // 函数功能：更新当前选中的城市编号。
  function setCity(id) { // 逐行注释：声明当前函数入口。
    currentCityId.value = id // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。

  return { cities, currentCityId, loaded, loadCities, setCity } // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。
