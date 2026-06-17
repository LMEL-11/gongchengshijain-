<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getProperty } from '@/api'

const route = useRoute()
const router = useRouter()

const prop = ref(null)
const loading = ref(true)

const categoryIcon = {
  school: 'Reading',
  hospital: 'FirstAidKit',
  subway: 'Van',
  transport: 'MapLocation',
  mall: 'ShoppingCart',
  park: 'Sunny',
}

// Group facilities by category for display.
const facilityGroups = computed(() => {
  const groups = {}
  for (const f of prop.value?.facilities || []) {
    ;(groups[f.category] ||= { label: f.category_label, items: [] }).items.push(f)
  }
  return groups
})

const specs = computed(() => {
  const p = prop.value
  if (!p) return []
  const floor =
    p.floor && p.total_floors
      ? `${p.floor}/${p.total_floors} 层`
      : p.total_floors
        ? `共 ${p.total_floors} 层`
        : '暂无'
  return [
    { label: '户型', value: p.layout },
    { label: '建筑面积', value: p.area ? `${p.area} ㎡` : '暂无' },
    { label: '楼层', value: floor },
    { label: '朝向', value: p.orientation || '暂无' },
    { label: '装修', value: p.decoration || '暂无' },
    { label: '电梯', value: p.has_elevator ? '有' : '无' },
    { label: '建成年份', value: p.build_year ? `${p.build_year} 年` : '暂无' },
    { label: '类型', value: p.listing_type },
  ]
})

const transactionSummary = computed(() => {
  const t = prop.value?.transaction || {}
  return [
    { label: '挂牌时间', value: t.listing_date },
    { label: '交易权属', value: t.ownership_type },
    { label: '产权情况', value: t.property_right },
    { label: '抵押信息', value: t.mortgage },
  ].filter((item) => item.value)
})

const transactionTexts = computed(() => {
  const t = prop.value?.transaction || {}
  return [
    { title: '核心卖点', value: t.selling_point },
    { title: '小区介绍', value: t.community_intro },
    { title: '户型介绍', value: t.layout_intro },
    { title: '交通出行', value: t.transport_intro },
  ].filter((item) => item.value)
})

const hasTransaction = computed(
  () => transactionSummary.value.length || transactionTexts.value.length,
)

async function load(id) {
  loading.value = true
  try {
    prop.value = await getProperty(id)
  } finally {
    loading.value = false
  }
}

onMounted(() => load(route.params.id))
watch(() => route.params.id, (id) => id && load(id))
</script>

<template>
  <div class="page" v-loading="loading">
    <el-button text :icon="'ArrowLeft'" class="back" @click="router.back()">返回</el-button>

    <template v-if="prop">
      <div class="card head">
        <div class="head-main">
          <h1>{{ prop.title }}</h1>
          <div class="loc">
            <el-icon><Location /></el-icon>
            {{ prop.city_name }} · {{ prop.district_name }}
            <el-tag size="small" effect="plain" style="margin-left: 8px">{{ prop.listing_type }}</el-tag>
          </div>
        </div>
        <div class="head-price">
          <div class="total">{{ prop.total_price }}<small>万元</small></div>
          <div class="unit muted">{{ prop.unit_price?.toLocaleString() }} 元/㎡</div>
        </div>
      </div>

      <el-row :gutter="16">
        <el-col :xs="24" :md="14">
          <div class="card">
            <div class="section-title">房源信息</div>
            <div class="specs">
              <div v-for="s in specs" :key="s.label" class="spec">
                <div class="spec-label muted">{{ s.label }}</div>
                <div class="spec-value">{{ s.value }}</div>
              </div>
            </div>
          </div>

          <div class="card" style="margin-top: 16px">
            <div class="section-title">交易属性</div>
            <template v-if="hasTransaction">
              <div v-if="transactionSummary.length" class="transaction-grid">
                <div v-for="item in transactionSummary" :key="item.label" class="transaction-item">
                  <div class="spec-label muted">{{ item.label }}</div>
                  <div class="spec-value">{{ item.value }}</div>
                </div>
              </div>

              <div class="detail-texts">
                <div v-for="item in transactionTexts" :key="item.title" class="detail-text">
                  <div class="detail-title">{{ item.title }}</div>
                  <p>{{ item.value }}</p>
                </div>
              </div>
            </template>
            <el-empty
              v-else
              description="该房源暂无交易属性扩展信息"
              :image-size="64"
              style="height: 260px"
            />
          </div>
        </el-col>

        <el-col :xs="24" :md="10">
          <div class="card facilities">
            <div class="section-title">周边配套设施</div>
            <p class="muted tip">学校、医院、地铁、商场、公园等，助你评估生活便利性</p>
            <div v-for="(g, key) in facilityGroups" :key="key" class="fac-group">
              <div class="fac-head">
                <el-icon :size="18"><component :is="categoryIcon[key] || 'Location'" /></el-icon>
                <span>{{ g.label }}</span>
              </div>
              <div class="fac-items">
                <el-tag v-for="f in g.items" :key="f.id" effect="plain" round>{{ f.name }}</el-tag>
              </div>
            </div>
            <el-empty
              v-if="!Object.keys(facilityGroups).length"
              description="该区域暂未采集周边配套数据"
              :image-size="64"
            />
          </div>
        </el-col>
      </el-row>
    </template>
  </div>
</template>

<style scoped>
.back {
  margin-bottom: 8px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.head-main h1 {
  margin: 0 0 10px;
  font-size: 24px;
}
.loc {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
}
.head-price {
  text-align: right;
}
.head-price .total {
  font-size: 34px;
  font-weight: 800;
  color: #f5222d;
}
.head-price .total small {
  font-size: 15px;
  margin-left: 4px;
}
.specs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px 12px;
}
.spec-label {
  font-size: 13px;
  margin-bottom: 4px;
}
.spec-value {
  font-size: 16px;
  font-weight: 600;
}
.transaction-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px 12px;
  margin-bottom: 18px;
}
.transaction-item {
  min-width: 0;
}
.detail-texts {
  display: grid;
  gap: 14px;
}
.detail-title {
  margin-bottom: 6px;
  color: #1e3a8a;
  font-weight: 700;
}
.detail-text p {
  margin: 0;
  color: #334155;
  line-height: 1.8;
  word-break: break-word;
}
.tip {
  margin: -6px 0 14px;
  font-size: 13px;
}
.fac-group {
  margin-bottom: 16px;
}
.fac-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1e3a8a;
}
.fac-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
@media (max-width: 768px) {
  .transaction-grid {
    grid-template-columns: 1fr;
  }
}
</style>
