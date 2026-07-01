<!-- 文件功能：实现房源详情页面，展示基础信息、交易信息和周边配套。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 导入 { computed, onMounted, ref, watch }，供当前前端模块渲染或交互逻辑使用。
import { useRoute, useRouter } from 'vue-router' // 导入 { useRoute, useRouter }，供当前前端模块渲染或交互逻辑使用。

import { getProperty } from '@/api' // 导入 { getProperty }，供当前前端模块渲染或交互逻辑使用。

const route = useRoute() // 创建 route，用于保存页面状态、计算结果或接口参数。
const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。

const prop = ref(null) // 创建 prop，用于保存页面状态、计算结果或接口参数。
const loading = ref(true) // 创建 loading，用于保存页面状态、计算结果或接口参数。

const categoryIcon = { // 创建 categoryIcon，用于保存页面状态、计算结果或接口参数。
  school: 'Reading', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  hospital: 'FirstAidKit', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  subway: 'Van', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  transport: 'MapLocation', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  mall: 'ShoppingCart', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  park: 'Sunny', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// Group facilities by category for display.
// 函数功能：按设施类型对周边配套进行分组。
const facilityGroups = computed(() => { // 创建 facilityGroups，用于保存页面状态、计算结果或接口参数。
  const groups = {} // 创建 groups，用于保存页面状态、计算结果或接口参数。
  for (const f of prop.value?.facilities || []) { // 遍历当前数据集合，逐项生成页面需要的数据。
    ;(groups[f.category] ||= { label: f.category_label, items: [] }).items.push(f) // 设置 ;(groups[f.category] || 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
  return groups // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：整理房源基础规格信息用于详情展示。
const specs = computed(() => { // 创建 specs，用于保存页面状态、计算结果或接口参数。
  const p = prop.value // 创建 p，用于保存页面状态、计算结果或接口参数。
  if (!p) return [] // 根据当前页面状态或接口结果决定是否进入该分支。
  const floor = // 创建 floor，用于保存页面状态、计算结果或接口参数。
    p.floor && p.total_floors // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      ? `${p.floor}/${p.total_floors} 层` // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      : p.total_floors // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        ? `共 ${p.total_floors} 层` // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        : '暂无' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  return [ // 返回整理后的数据、组件配置或渲染结果。
    { label: '户型', value: p.layout }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '建筑面积', value: p.area ? `${p.area} ㎡` : '暂无' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '楼层', value: floor }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '朝向', value: p.orientation || '暂无' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '装修', value: p.decoration || '暂无' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '电梯', value: p.has_elevator ? '有' : '无' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '建成年份', value: p.build_year ? `${p.build_year} 年` : '暂无' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '类型', value: p.listing_type }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ] // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：整理房源交易摘要信息。
const transactionSummary = computed(() => { // 创建 transactionSummary，用于保存页面状态、计算结果或接口参数。
  const t = prop.value?.transaction || {} // 创建 t，用于保存页面状态、计算结果或接口参数。
  return [ // 返回整理后的数据、组件配置或渲染结果。
    { label: '挂牌时间', value: t.listing_date }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '交易权属', value: t.ownership_type }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '产权情况', value: t.property_right }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { label: '抵押信息', value: t.mortgage }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ].filter((item) => item.value) // 更新 ].filter((item) 响应式状态，让页面展示与最新数据保持一致。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：整理房源交易长文本说明。
const transactionTexts = computed(() => { // 创建 transactionTexts，用于保存页面状态、计算结果或接口参数。
  const t = prop.value?.transaction || {} // 创建 t，用于保存页面状态、计算结果或接口参数。
  return [ // 返回整理后的数据、组件配置或渲染结果。
    { title: '核心卖点', value: t.selling_point }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { title: '小区介绍', value: t.community_intro }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { title: '户型介绍', value: t.layout_intro }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { title: '交通出行', value: t.transport_intro }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  ].filter((item) => item.value) // 更新 ].filter((item) 响应式状态，让页面展示与最新数据保持一致。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：判断房源是否包含可展示的交易扩展信息。
const hasTransaction = computed( // 创建 hasTransaction，用于保存页面状态、计算结果或接口参数。
  () => transactionSummary.value.length || transactionTexts.value.length, // 更新 () 响应式状态，让页面展示与最新数据保持一致。
) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：加载当前页面所需的详情或统计数据。
async function load(id) { // 定义 load 函数，处理页面交互、数据加载或状态同步。
  loading.value = true // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    prop.value = await getProperty(id) // 更新 prop.value 响应式状态，让页面展示与最新数据保持一致。
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loading.value = false // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(() => load(route.params.id)) // 设置 onMounted 的值，作为后续渲染、计算或请求的输入。
watch(() => route.params.id, (id) => id && load(id)) // 设置 watch 的值，作为后续渲染、计算或请求的输入。
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
.back { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 8px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.head { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.head-main h1 { /* 定义当前选择器的样式作用域。 */
  margin: 0 0 10px; /* 设置元素外边距。 */
  font-size: 24px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.loc { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 6px; /* 设置子元素之间的间距。 */
  color: #475569; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.head-price { /* 定义当前选择器的样式作用域。 */
  text-align: right; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.head-price .total { /* 定义当前选择器的样式作用域。 */
  font-size: 34px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
  color: #f5222d; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.head-price .total small { /* 定义当前选择器的样式作用域。 */
  font-size: 15px; /* 设置文字大小。 */
  margin-left: 4px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.specs { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: repeat(2, 1fr); /* 设置网格列布局。 */
  gap: 18px 12px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.spec-label { /* 定义当前选择器的样式作用域。 */
  font-size: 13px; /* 设置文字大小。 */
  margin-bottom: 4px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.spec-value { /* 定义当前选择器的样式作用域。 */
  font-size: 16px; /* 设置文字大小。 */
  font-weight: 600; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */
.transaction-grid { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* 设置网格列布局。 */
  gap: 16px 12px; /* 设置子元素之间的间距。 */
  margin-bottom: 18px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.transaction-item { /* 定义当前选择器的样式作用域。 */
  min-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.detail-texts { /* 定义当前选择器的样式作用域。 */
  display: grid; /* 设置元素布局模式。 */
  gap: 14px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.detail-title { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 6px; /* 设置元素底部外边距。 */
  color: #1e3a8a; /* 设置文字颜色。 */
  font-weight: 700; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */
.detail-text p { /* 定义当前选择器的样式作用域。 */
  margin: 0; /* 设置元素外边距。 */
  color: #334155; /* 设置文字颜色。 */
  line-height: 1.8; /* 设置文本行高。 */
  word-break: break-word; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.tip { /* 定义当前选择器的样式作用域。 */
  margin: -6px 0 14px; /* 设置元素外边距。 */
  font-size: 13px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
.fac-group { /* 定义当前选择器的样式作用域。 */
  margin-bottom: 16px; /* 设置元素底部外边距。 */
} /* 结束当前样式规则块。 */
.fac-head { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 6px; /* 设置子元素之间的间距。 */
  font-weight: 600; /* 设置文字粗细。 */
  margin-bottom: 8px; /* 设置元素底部外边距。 */
  color: #1e3a8a; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.fac-items { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  flex-wrap: wrap; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  gap: 8px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
@media (max-width: 768px) { /* 定义当前选择器的样式作用域。 */
  .transaction-grid { /* 定义当前选择器的样式作用域。 */
    grid-template-columns: 1fr; /* 设置网格列布局。 */
  } /* 结束当前样式规则块。 */
} /* 结束当前样式规则块。 */
</style>
