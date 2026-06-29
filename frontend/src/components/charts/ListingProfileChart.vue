<!-- 文件功能：展示区域挂牌走势、交易属性分布和税费标签画像。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from './BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  data: { type: Array, default: () => [] }, // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '280px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：格式化挂牌画像中的价格展示文本。
function priceLabel(value) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!value) return '暂无' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return `${Number(value).toLocaleString()} 元/㎡` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  color: ['#10b981', '#f59e0b'], // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
  grid: { left: 12, right: 56, top: 42, bottom: 20, containLabel: true }, // 声明grid字段，作为组件配置、请求参数或图表数据的一部分。
  legend: { // 声明legend字段，作为组件配置、请求参数或图表数据的一部分。
    top: 0, // 声明top字段，作为组件配置、请求参数或图表数据的一部分。
    right: 0, // 声明right字段，作为组件配置、请求参数或图表数据的一部分。
    data: ['挂牌套数', '挂牌均价'], // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  tooltip: { // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
    trigger: 'axis', // 声明trigger字段，作为组件配置、请求参数或图表数据的一部分。
    axisPointer: { type: 'cross' }, // 声明axisPointer字段，作为组件配置、请求参数或图表数据的一部分。
    formatter: (params) => { // 声明formatter字段，作为组件配置、请求参数或图表数据的一部分。
      const month = params[0]?.axisValue || '' // 保存month相关业务数据，作为后续计算、渲染或请求的输入。
      const lines = params // 保存lines相关业务数据，作为后续计算、渲染或请求的输入。
        .map((item) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
          const value = // 保存value相关业务数据，作为后续计算、渲染或请求的输入。
            item.seriesName === '挂牌均价' // 更新item.seriesName对应的页面状态，使界面展示与最新业务数据一致。
              ? priceLabel(item.value) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
              : `${Number(item.value || 0).toLocaleString()} 套` // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          return `${item.marker}${item.seriesName}：${value}` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
        }) // 完成当前参数、配置或响应式数据结构的组装。
        .join('<br/>') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      return `<b>${month}</b><br/>${lines}` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  xAxis: { // 声明xAxis字段，作为组件配置、请求参数或图表数据的一部分。
    type: 'category', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    data: props.data.map((d) => d.month), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
    axisLabel: { rotate: 35 }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  yAxis: [ // 声明yAxis字段，作为组件配置、请求参数或图表数据的一部分。
    { type: 'value', name: '房源套数', minInterval: 1 }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      type: 'value', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      name: '元/㎡', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      scale: true, // 声明scale字段，作为组件配置、请求参数或图表数据的一部分。
      axisLabel: { formatter: (v) => `${(v / 10000).toFixed(1)}万` }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  ], // 完成当前参数、配置或响应式数据结构的组装。
  series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      name: '挂牌套数', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      type: 'bar', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      barWidth: '48%', // 声明barWidth字段，作为组件配置、请求参数或图表数据的一部分。
      data: props.data.map((d) => d.count), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
      itemStyle: { borderRadius: [6, 6, 0, 0] }, // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      name: '挂牌均价', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      type: 'line', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      yAxisIndex: 1, // 声明yAxisIndex字段，作为组件配置、请求参数或图表数据的一部分。
      smooth: true, // 声明smooth字段，作为组件配置、请求参数或图表数据的一部分。
      symbol: 'circle', // 声明symbol字段，作为组件配置、请求参数或图表数据的一部分。
      symbolSize: 6, // 声明symbolSize字段，作为组件配置、请求参数或图表数据的一部分。
      data: props.data.map((d) => d.avg_unit_price), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
      lineStyle: { width: 3 }, // 声明lineStyle字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  ], // 完成当前参数、配置或响应式数据结构的组装。
})) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
