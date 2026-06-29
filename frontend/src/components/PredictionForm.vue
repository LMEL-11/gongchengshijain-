<!-- 文件功能：提供房价预测表单，加载区域选项并提交预测参数。 -->
<script setup>
import { onMounted, reactive, ref, watch } from 'vue'

import { getCityDistricts, predictPrice } from '@/api'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const districts = ref([])
const result = ref(null)
const loading = ref(false)

const form = reactive({
  city_id: null,
  district_id: null,
  area: 90,
  rooms: 2,
  halls: 1,
  build_year: 2015,
  floor: 8,
  total_floors: 18,
  has_elevator: true,
})

// 函数功能：根据当前城市加载区域选项。
async function loadDistricts(cityId) {
  if (!cityId) return
  districts.value = await getCityDistricts(cityId)
  if (districts.value.length) form.district_id = districts.value[0].id
}

watch(
  () => form.city_id,
  (id) => loadDistricts(id),
)

onMounted(async () => {
  await store.loadCities()
  form.city_id = store.currentCityId
})

// 函数功能：校验表单并提交预测请求。
async function onSubmit() {
  if (!form.district_id) return
  loading.value = true
  try {
    result.value = await predictPrice({ ...form })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="predict">
    <el-form :model="form" label-width="92px" label-position="left">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="城市">
            <el-select v-model="form.city_id" placeholder="选择城市" style="width: 100%">
              <el-option v-for="c in store.cities" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="行政区">
            <el-select v-model="form.district_id" placeholder="选择行政区" style="width: 100%">
              <el-option v-for="d in districts" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="建筑面积">
            <el-input-number v-model="form.area" :min="15" :max="500" :step="5" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="建成年份">
            <el-input-number v-model="form.build_year" :min="1980" :max="2026" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="室">
            <el-input-number v-model="form.rooms" :min="1" :max="6" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="厅">
            <el-input-number v-model="form.halls" :min="0" :max="4" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="所在楼层">
            <el-input-number v-model="form.floor" :min="1" :max="form.total_floors" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="总楼层">
            <el-input-number v-model="form.total_floors" :min="1" :max="80" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电梯">
            <el-switch v-model="form.has_elevator" active-text="有" inactive-text="无" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-button type="primary" :loading="loading" style="width: 100%" @click="onSubmit">
        <el-icon style="margin-right: 6px"><MagicStick /></el-icon>预测房价
      </el-button>
    </el-form>

    <transition name="fade">
      <div v-if="result" class="result">
        <div class="big">
          预测总价 <b>{{ result.total_price }}</b> 万元
        </div>
        <div class="sub">
          预测单价 <b class="price-text">{{ result.unit_price.toLocaleString() }}</b> 元/㎡
        </div>
        <div class="meta">
          {{ result.district_name }} · 区域均价
          {{ result.district_avg_unit_price?.toLocaleString() || '-' }} 元/㎡ ·
          模型：{{ result.method === 'district_random_forest' ? '行政区随机森林' : '启发式估算' }}
          <template v-if="result.training_sample_count">
            · 样本 {{ result.training_sample_count.toLocaleString() }} 条
          </template>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.result {
  margin-top: 18px;
  padding: 18px;
  border-radius: 10px;
  background: linear-gradient(135deg, #eff6ff, #eef2ff);
  border: 1px solid #dbeafe;
  text-align: center;
}
.big {
  font-size: 18px;
}
.big b {
  font-size: 30px;
  color: #1d4ed8;
}
.sub {
  margin-top: 6px;
  font-size: 15px;
}
.meta {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}
.fade-enter-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from {
  opacity: 0;
}
</style>
