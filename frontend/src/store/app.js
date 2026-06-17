import { defineStore } from 'pinia'
import { ref } from 'vue'

import { getCities } from '@/api'

export const useAppStore = defineStore('app', () => {
  const cities = ref([])
  const currentCityId = ref(1)
  const loaded = ref(false)

  async function loadCities() {
    if (loaded.value) return
    cities.value = await getCities()
    loaded.value = true
    if (cities.value.length && !cities.value.find((c) => c.id === currentCityId.value)) {
      currentCityId.value = cities.value[0].id
    }
  }

  function setCity(id) {
    currentCityId.value = id
  }

  return { cities, currentCityId, loaded, loadCities, setCity }
})
