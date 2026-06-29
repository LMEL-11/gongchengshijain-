<!-- 文件功能：根据历史均价数据生成区域房价趋势折线图。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from './BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  data: { type: Array, default: () => [] }, // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '320px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 声明grid字段，作为组件配置、请求参数或图表数据的一部分。
  tooltip: { // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
    trigger: 'axis', // 声明trigger字段，作为组件配置、请求参数或图表数据的一部分。
    valueFormatter: (v) => `${Number(v).toLocaleString()} 元/㎡`, // 声明valueFormatter字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  xAxis: { // 声明xAxis字段，作为组件配置、请求参数或图表数据的一部分。
    type: 'category', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    boundaryGap: false, // 声明boundaryGap字段，作为组件配置、请求参数或图表数据的一部分。
    data: props.data.map((d) => d.month), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  yAxis: { // 声明yAxis字段，作为组件配置、请求参数或图表数据的一部分。
    type: 'value', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    scale: true, // 声明scale字段，作为组件配置、请求参数或图表数据的一部分。
    name: '元/㎡', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    axisLabel: { formatter: (v) => v / 10000 + '万' }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      type: 'line', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      smooth: true, // 声明smooth字段，作为组件配置、请求参数或图表数据的一部分。
      symbol: 'circle', // 声明symbol字段，作为组件配置、请求参数或图表数据的一部分。
      symbolSize: 6, // 声明symbolSize字段，作为组件配置、请求参数或图表数据的一部分。
      data: props.data.map((d) => d.avg_unit_price), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
      lineStyle: { width: 3, color: '#2563eb' }, // 声明lineStyle字段，作为组件配置、请求参数或图表数据的一部分。
      itemStyle: { color: '#2563eb' }, // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
      areaStyle: { // 声明areaStyle字段，作为组件配置、请求参数或图表数据的一部分。
        color: { // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
          type: 'linear', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
          x: 0, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
          y: 0, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
          x2: 0, // 声明x2字段，作为组件配置、请求参数或图表数据的一部分。
          y2: 1, // 声明y2字段，作为组件配置、请求参数或图表数据的一部分。
          colorStops: [ // 声明colorStops字段，作为组件配置、请求参数或图表数据的一部分。
            { offset: 0, color: 'rgba(37,99,235,0.35)' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
            { offset: 1, color: 'rgba(37,99,235,0.02)' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          ], // 完成当前参数、配置或响应式数据结构的组装。
        }, // 完成当前参数、配置或响应式数据结构的组装。
      }, // 完成当前参数、配置或响应式数据结构的组装。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  ], // 完成当前参数、配置或响应式数据结构的组装。
})) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
