<!-- 文件功能：实现房源详情页面，展示基础信息、交易信息和周边配套。 -->
<script setup>
import { computed, onMounted, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRoute, useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { getProperty } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const route = useRoute() // 保存route相关业务数据，作为后续计算、渲染或请求的输入。
const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。

const prop = ref(null) // 创建prop响应式状态，用于驱动页面渲染、表单输入或接口参数。
const loading = ref(true) // 创建加载状态，用于驱动页面渲染、表单输入或接口参数。

const categoryIcon = { // 保存categoryIcon相关业务数据，作为后续计算、渲染或请求的输入。
  school: 'Reading', // 声明school字段，作为组件配置、请求参数或图表数据的一部分。
  hospital: 'FirstAidKit', // 声明hospital字段，作为组件配置、请求参数或图表数据的一部分。
  subway: 'Van', // 声明subway字段，作为组件配置、请求参数或图表数据的一部分。
  transport: 'MapLocation', // 声明transport字段，作为组件配置、请求参数或图表数据的一部分。
  mall: 'ShoppingCart', // 声明mall字段，作为组件配置、请求参数或图表数据的一部分。
  park: 'Sunny', // 声明park字段，作为组件配置、请求参数或图表数据的一部分。
} // 完成当前参数、配置或响应式数据结构的组装。

// Group facilities by category for display.
// 函数功能：按设施类型对周边配套进行分组。
const facilityGroups = computed(() => { // 基于响应式数据派生facilityGroups，用于保持界面展示与数据状态同步。
  const groups = {} // 保存groups相关业务数据，作为后续计算、渲染或请求的输入。
  for (const f of prop.value?.facilities || []) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    ;(groups[f.category] ||= { label: f.category_label, items: [] }).items.push(f) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return groups // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：整理房源基础规格信息用于详情展示。
const specs = computed(() => { // 基于响应式数据派生specs，用于保持界面展示与数据状态同步。
  const p = prop.value // 保存p相关业务数据，作为后续计算、渲染或请求的输入。
  if (!p) return [] // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const floor = // 保存floor相关业务数据，作为后续计算、渲染或请求的输入。
    p.floor && p.total_floors // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      ? `${p.floor}/${p.total_floors} 层` // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      : p.total_floors // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        ? `共 ${p.total_floors} 层` // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        : '暂无' // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  return [ // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    { label: '户型', value: p.layout }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '建筑面积', value: p.area ? `${p.area} ㎡` : '暂无' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '楼层', value: floor }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '朝向', value: p.orientation || '暂无' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '装修', value: p.decoration || '暂无' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '电梯', value: p.has_elevator ? '有' : '无' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '建成年份', value: p.build_year ? `${p.build_year} 年` : '暂无' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '类型', value: p.listing_type }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ] // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：整理房源交易摘要信息。
const transactionSummary = computed(() => { // 基于响应式数据派生transactionSummary，用于保持界面展示与数据状态同步。
  const t = prop.value?.transaction || {} // 保存t相关业务数据，作为后续计算、渲染或请求的输入。
  return [ // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    { label: '挂牌时间', value: t.listing_date }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '交易权属', value: t.ownership_type }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '产权情况', value: t.property_right }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { label: '抵押信息', value: t.mortgage }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ].filter((item) => item.value) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：整理房源交易长文本说明。
const transactionTexts = computed(() => { // 基于响应式数据派生transactionTexts，用于保持界面展示与数据状态同步。
  const t = prop.value?.transaction || {} // 保存t相关业务数据，作为后续计算、渲染或请求的输入。
  return [ // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    { title: '核心卖点', value: t.selling_point }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { title: '小区介绍', value: t.community_intro }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { title: '户型介绍', value: t.layout_intro }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { title: '交通出行', value: t.transport_intro }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  ].filter((item) => item.value) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：判断房源是否包含可展示的交易扩展信息。
const hasTransaction = computed( // 基于响应式数据派生hasTransaction，用于保持界面展示与数据状态同步。
  () => transactionSummary.value.length || transactionTexts.value.length, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：加载当前页面所需的详情或统计数据。
async function load(id) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  loading.value = true // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    prop.value = await getProperty(id) // 等待异步接口或资源加载完成，再继续更新页面状态。
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loading.value = false // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(() => load(route.params.id)) // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
watch(() => route.params.id, (id) => id && load(id)) // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
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
.back { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 8px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.head-main h1 { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0 0 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 24px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.loc { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  color: #475569; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.head-price { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  text-align: right; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.head-price .total { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 34px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #f5222d; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.head-price .total small { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin-left: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.specs { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: repeat(2, 1fr); /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 18px 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.spec-label { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin-bottom: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.spec-value { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 16px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 600; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.transaction-grid { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  grid-template-columns: repeat(2, minmax(0, 1fr)); /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 16px 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin-bottom: 18px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.transaction-item { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  min-width: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.detail-texts { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: grid; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.detail-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 6px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #1e3a8a; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.detail-text p { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  color: #334155; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  line-height: 1.8; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  word-break: break-word; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.tip { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: -6px 0 14px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.fac-group { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin-bottom: 16px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.fac-head { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-weight: 600; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin-bottom: 8px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #1e3a8a; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.fac-items { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-wrap: wrap; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  gap: 8px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
@media (max-width: 768px) { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  .transaction-grid { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
    grid-template-columns: 1fr; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  } /* 收束该样式块，使后续选择器保持独立。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
