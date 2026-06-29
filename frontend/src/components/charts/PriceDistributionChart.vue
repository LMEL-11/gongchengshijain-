<!-- 文件功能：根据价格分布数据生成房源价格区间柱状图。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from './BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  data: { type: Array, default: () => [] }, // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '340px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 声明grid字段，作为组件配置、请求参数或图表数据的一部分。
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
  xAxis: { // 声明xAxis字段，作为组件配置、请求参数或图表数据的一部分。
    type: 'category', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
    data: props.data.map((d) => d.range), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
    axisLabel: { rotate: 30 }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  yAxis: { type: 'value', name: '房源套数' }, // 声明yAxis字段，作为组件配置、请求参数或图表数据的一部分。
  series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      type: 'bar', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      data: props.data.map((d) => d.count), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
      barWidth: '55%', // 声明barWidth字段，作为组件配置、请求参数或图表数据的一部分。
      itemStyle: { // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
        borderRadius: [6, 6, 0, 0], // 声明borderRadius字段，作为组件配置、请求参数或图表数据的一部分。
        color: { // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
          type: 'linear', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
          x: 0, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
          y: 0, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
          x2: 0, // 声明x2字段，作为组件配置、请求参数或图表数据的一部分。
          y2: 1, // 声明y2字段，作为组件配置、请求参数或图表数据的一部分。
          colorStops: [ // 声明colorStops字段，作为组件配置、请求参数或图表数据的一部分。
            { offset: 0, color: '#34d399' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
            { offset: 1, color: '#059669' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
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
