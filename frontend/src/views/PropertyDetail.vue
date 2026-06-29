<!-- 文件功能：实现房源详情页面，展示基础信息、交易信息和周边配套。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。
import { useRoute, useRouter } from 'vue-router' // 逐行注释：导入本行所需的依赖。

import { getProperty } from '@/api' // 逐行注释：导入本行所需的依赖。

const route = useRoute() // 逐行注释：声明并初始化当前变量。
const router = useRouter() // 逐行注释：声明并初始化当前变量。

const prop = ref(null) // 逐行注释：声明并初始化当前变量。
const loading = ref(true) // 逐行注释：声明并初始化当前变量。

const categoryIcon = { // 逐行注释：声明并初始化当前变量。
  school: 'Reading', // 逐行注释：配置当前对象字段。
  hospital: 'FirstAidKit', // 逐行注释：配置当前对象字段。
  subway: 'Van', // 逐行注释：配置当前对象字段。
  transport: 'MapLocation', // 逐行注释：配置当前对象字段。
  mall: 'ShoppingCart', // 逐行注释：配置当前对象字段。
  park: 'Sunny', // 逐行注释：配置当前对象字段。
} // 逐行注释：结束当前代码块或数据结构。

// Group facilities by category for display.
// 函数功能：按设施类型对周边配套进行分组。
const facilityGroups = computed(() => { // 逐行注释：声明并初始化当前变量。
  const groups = {} // 逐行注释：声明并初始化当前变量。
  for (const f of prop.value?.facilities || []) { // 逐行注释：遍历集合或范围并逐项处理。
    ;(groups[f.category] ||= { label: f.category_label, items: [] }).items.push(f) // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
  return groups // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：整理房源基础规格信息用于详情展示。
const specs = computed(() => { // 逐行注释：声明并初始化当前变量。
  const p = prop.value // 逐行注释：声明并初始化当前变量。
  if (!p) return [] // 逐行注释：根据条件判断是否执行分支。
  const floor = // 逐行注释：声明并初始化当前变量。
    p.floor && p.total_floors // 逐行注释：执行本行前端逻辑。
      ? `${p.floor}/${p.total_floors} 层` // 逐行注释：执行本行前端逻辑。
      : p.total_floors // 逐行注释：执行本行前端逻辑。
        ? `共 ${p.total_floors} 层` // 逐行注释：执行本行前端逻辑。
        : '暂无' // 逐行注释：执行本行前端逻辑。
  return [ // 逐行注释：返回当前表达式结果。
    { label: '户型', value: p.layout }, // 逐行注释：配置当前对象字段。
    { label: '建筑面积', value: p.area ? `${p.area} ㎡` : '暂无' }, // 逐行注释：配置当前对象字段。
    { label: '楼层', value: floor }, // 逐行注释：配置当前对象字段。
    { label: '朝向', value: p.orientation || '暂无' }, // 逐行注释：配置当前对象字段。
    { label: '装修', value: p.decoration || '暂无' }, // 逐行注释：配置当前对象字段。
    { label: '电梯', value: p.has_elevator ? '有' : '无' }, // 逐行注释：配置当前对象字段。
    { label: '建成年份', value: p.build_year ? `${p.build_year} 年` : '暂无' }, // 逐行注释：配置当前对象字段。
    { label: '类型', value: p.listing_type }, // 逐行注释：配置当前对象字段。
  ] // 逐行注释：结束当前代码块或数据结构。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：整理房源交易摘要信息。
const transactionSummary = computed(() => { // 逐行注释：声明并初始化当前变量。
  const t = prop.value?.transaction || {} // 逐行注释：声明并初始化当前变量。
  return [ // 逐行注释：返回当前表达式结果。
    { label: '挂牌时间', value: t.listing_date }, // 逐行注释：配置当前对象字段。
    { label: '交易权属', value: t.ownership_type }, // 逐行注释：配置当前对象字段。
    { label: '产权情况', value: t.property_right }, // 逐行注释：配置当前对象字段。
    { label: '抵押信息', value: t.mortgage }, // 逐行注释：配置当前对象字段。
  ].filter((item) => item.value) // 逐行注释：执行本行前端逻辑。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：整理房源交易长文本说明。
const transactionTexts = computed(() => { // 逐行注释：声明并初始化当前变量。
  const t = prop.value?.transaction || {} // 逐行注释：声明并初始化当前变量。
  return [ // 逐行注释：返回当前表达式结果。
    { title: '核心卖点', value: t.selling_point }, // 逐行注释：配置当前对象字段。
    { title: '小区介绍', value: t.community_intro }, // 逐行注释：配置当前对象字段。
    { title: '户型介绍', value: t.layout_intro }, // 逐行注释：配置当前对象字段。
    { title: '交通出行', value: t.transport_intro }, // 逐行注释：配置当前对象字段。
  ].filter((item) => item.value) // 逐行注释：执行本行前端逻辑。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：判断房源是否包含可展示的交易扩展信息。
const hasTransaction = computed( // 逐行注释：声明并初始化当前变量。
  () => transactionSummary.value.length || transactionTexts.value.length, // 逐行注释：继续声明当前列表项或参数项。
) // 逐行注释：结束当前代码块或数据结构。

// 函数功能：加载当前页面所需的详情或统计数据。
async function load(id) { // 逐行注释：声明当前函数入口。
  loading.value = true // 逐行注释：赋值或更新当前变量/状态。
  try { // 逐行注释：开始执行可能失败的逻辑。
    prop.value = await getProperty(id) // 逐行注释：赋值或更新当前变量/状态。
  } finally { // 逐行注释：执行本行前端逻辑。
    loading.value = false // 逐行注释：赋值或更新当前变量/状态。
  } // 逐行注释：结束当前代码块或数据结构。
} // 逐行注释：结束当前代码块或数据结构。

onMounted(() => load(route.params.id)) // 逐行注释：注册 Vue 生命周期回调。
watch(() => route.params.id, (id) => id && load(id)) // 逐行注释：监听响应式数据变化。
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
.back { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 8px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.head { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: space-between; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.head-main h1 { /* 逐行注释：开始当前样式规则块。 */
  margin: 0 0 10px; /* 逐行注释：设置当前样式属性。 */
  font-size: 24px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.loc { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 6px; /* 逐行注释：设置当前样式属性。 */
  color: #475569; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.head-price { /* 逐行注释：开始当前样式规则块。 */
  text-align: right; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.head-price .total { /* 逐行注释：开始当前样式规则块。 */
  font-size: 34px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  color: #f5222d; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.head-price .total small { /* 逐行注释：开始当前样式规则块。 */
  font-size: 15px; /* 逐行注释：设置当前样式属性。 */
  margin-left: 4px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.specs { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: repeat(2, 1fr); /* 逐行注释：设置当前样式属性。 */
  gap: 18px 12px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.spec-label { /* 逐行注释：开始当前样式规则块。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 4px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.spec-value { /* 逐行注释：开始当前样式规则块。 */
  font-size: 16px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 600; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.transaction-grid { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* 逐行注释：设置当前样式属性。 */
  gap: 16px 12px; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 18px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.transaction-item { /* 逐行注释：开始当前样式规则块。 */
  min-width: 0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.detail-texts { /* 逐行注释：开始当前样式规则块。 */
  display: grid; /* 逐行注释：设置当前样式属性。 */
  gap: 14px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.detail-title { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 6px; /* 逐行注释：设置当前样式属性。 */
  color: #1e3a8a; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.detail-text p { /* 逐行注释：开始当前样式规则块。 */
  margin: 0; /* 逐行注释：设置当前样式属性。 */
  color: #334155; /* 逐行注释：设置当前样式属性。 */
  line-height: 1.8; /* 逐行注释：设置当前样式属性。 */
  word-break: break-word; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.tip { /* 逐行注释：开始当前样式规则块。 */
  margin: -6px 0 14px; /* 逐行注释：设置当前样式属性。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.fac-group { /* 逐行注释：开始当前样式规则块。 */
  margin-bottom: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.fac-head { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 6px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 600; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 8px; /* 逐行注释：设置当前样式属性。 */
  color: #1e3a8a; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.fac-items { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-wrap: wrap; /* 逐行注释：设置当前样式属性。 */
  gap: 8px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
@media (max-width: 768px) { /* 逐行注释：声明响应式媒体查询规则。 */
  .transaction-grid { /* 逐行注释：开始当前样式规则块。 */
    grid-template-columns: 1fr; /* 逐行注释：设置当前样式属性。 */
  } /* 逐行注释：结束当前样式规则块。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
