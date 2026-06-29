// 文件功能：维护城市列表、当前城市和基础应用状态。
import { defineStore } from 'pinia' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { ref } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { getCities } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

export const useAppStore = defineStore('app', () => { // 导出当前配置或接口方法，供应用其他模块复用。
  const cities = ref([]) // 创建城市集合，用于驱动页面渲染、表单输入或接口参数。
  const currentCityId = ref(1) // 创建currentCityId响应式状态，用于驱动页面渲染、表单输入或接口参数。
  const loaded = ref(false) // 创建loaded响应式状态，用于驱动页面渲染、表单输入或接口参数。

  // 函数功能：加载城市列表并初始化当前城市。
  async function loadCities() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    if (loaded.value) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
    cities.value = await getCities() // 等待异步接口或资源加载完成，再继续更新页面状态。
    loaded.value = true // 更新loaded.value对应的页面状态，使界面展示与最新业务数据一致。
    if (cities.value.length && !cities.value.find((c) => c.id === currentCityId.value)) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      currentCityId.value = cities.value[0].id // 更新currentCityId.value对应的页面状态，使界面展示与最新业务数据一致。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 函数功能：更新当前选中的城市编号。
  function setCity(id) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    currentCityId.value = id // 更新currentCityId.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。

  return { cities, currentCityId, loaded, loadCities, setCity } // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。
