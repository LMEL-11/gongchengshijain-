<!-- 文件功能：根据区域均价排行数据生成横向柱状图配置并渲染。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from './BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  data: { type: Array, default: () => [] }, // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '360px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  // 真实城市可能有数十个商圈，仅取均价最高的前 N 个，避免条形图过密。
  const LIMIT = 18 // 保存LIMIT相关业务数据，作为后续计算、渲染或请求的输入。
  const top = [...props.data] // 保存top相关业务数据，作为后续计算、渲染或请求的输入。
    .sort((a, b) => b.avg_unit_price - a.avg_unit_price) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    .slice(0, LIMIT) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  // Show ascending so the highest bar sits on top of the horizontal chart.
  const sorted = top.sort((a, b) => a.avg_unit_price - b.avg_unit_price) // 保存sorted相关业务数据，作为后续计算、渲染或请求的输入。
  return { // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    grid: { left: 12, right: 60, top: 16, bottom: 16, containLabel: true }, // 声明grid字段，作为组件配置、请求参数或图表数据的一部分。
    tooltip: { // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
      trigger: 'axis', // 声明trigger字段，作为组件配置、请求参数或图表数据的一部分。
      axisPointer: { type: 'shadow' }, // 声明axisPointer字段，作为组件配置、请求参数或图表数据的一部分。
      valueFormatter: (v) => `${v.toLocaleString()} 元/㎡`, // 声明valueFormatter字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    xAxis: { type: 'value', axisLabel: { formatter: (v) => v / 10000 + '万' } }, // 声明xAxis字段，作为组件配置、请求参数或图表数据的一部分。
    yAxis: { type: 'category', data: sorted.map((d) => d.name) }, // 声明yAxis字段，作为组件配置、请求参数或图表数据的一部分。
    series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
      { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
        type: 'bar', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
        data: sorted.map((d) => d.avg_unit_price), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
        barWidth: '60%', // 声明barWidth字段，作为组件配置、请求参数或图表数据的一部分。
        label: { // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
          show: true, // 声明show字段，作为组件配置、请求参数或图表数据的一部分。
          position: 'right', // 声明position字段，作为组件配置、请求参数或图表数据的一部分。
          formatter: (p) => (p.value / 10000).toFixed(1) + '万', // 声明formatter字段，作为组件配置、请求参数或图表数据的一部分。
          color: '#475569', // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
        }, // 完成当前参数、配置或响应式数据结构的组装。
        itemStyle: { // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
          borderRadius: [0, 6, 6, 0], // 声明borderRadius字段，作为组件配置、请求参数或图表数据的一部分。
          color: { // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
            type: 'linear', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
            x: 0, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
            y: 0, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
            x2: 1, // 声明x2字段，作为组件配置、请求参数或图表数据的一部分。
            y2: 0, // 声明y2字段，作为组件配置、请求参数或图表数据的一部分。
            colorStops: [ // 声明colorStops字段，作为组件配置、请求参数或图表数据的一部分。
              { offset: 0, color: '#60a5fa' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
              { offset: 1, color: '#1d4ed8' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
            ], // 完成当前参数、配置或响应式数据结构的组装。
          }, // 完成当前参数、配置或响应式数据结构的组装。
        }, // 完成当前参数、配置或响应式数据结构的组装。
      }, // 完成当前参数、配置或响应式数据结构的组装。
    ], // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
