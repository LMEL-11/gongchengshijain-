// 文件功能：维护城市列表、当前城市和基础应用状态。
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getCities } from '@/api'

export const useAppStore = defineStore('app', () => {
  const cities = ref([])
  const currentCityId = ref(1)
  const loaded = ref(false)

  // 函数功能：加载城市列表并初始化当前城市。
  async function loadCities() {
    if (loaded.value) return
    cities.value = await getCities()
    loaded.value = true
    if (cities.value.length && !cities.value.find((c) => c.id === currentCityId.value)) {
      currentCityId.value = cities.value[0].id
    }
  }

  // 函数功能：更新当前选中的城市编号。
  function setCity(id) {
    currentCityId.value = id
  }

  return { cities, currentCityId, loaded, loadCities, setCity }
})
