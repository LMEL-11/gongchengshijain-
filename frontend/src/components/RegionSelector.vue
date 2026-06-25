<script setup>
import { computed } from 'vue'

const props = defineProps({
  cities: {
    type: Array,
    default: () => [],
  },
  districts: {
    type: Array,
    default: () => [],
  },
  province: {
    type: String,
    default: '',
  },
  cityId: {
    type: Number,
    default: null,
  },
  districtId: {
    type: Number,
    default: null,
  },
  size: {
    type: String,
    default: 'default',
  },
  districtClearable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:province', 'update:cityId', 'update:districtId'])

const provinces = computed(() => {
  const seen = new Set()
  const result = []
  for (const city of props.cities) {
    const province = city.province || '其他'
    if (!seen.has(province)) {
      seen.add(province)
      result.push(province)
    }
  }
  return result.sort()
})

const filteredCities = computed(() => {
  if (!props.province) return []
  return props.cities.filter((city) => (city.province || '其他') === props.province)
})

function handleProvinceChange(value) {
  emit('update:province', value || '')
  emit('update:cityId', null)
  emit('update:districtId', null)
}

function handleCityChange(value) {
  emit('update:cityId', value || null)
  emit('update:districtId', null)
}

function handleDistrictChange(value) {
  emit('update:districtId', value || null)
}
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
.region-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.region-select {
  flex: 0 0 auto;
}
.province-select {
  width: 150px;
}
.city-select {
  width: 130px;
}
.district-select {
  width: 140px;
}
@media (max-width: 640px) {
  .region-selector {
    width: 100%;
  }
  .region-select {
    width: 100%;
  }
}
</style>
