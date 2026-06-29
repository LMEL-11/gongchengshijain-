<!-- 文件功能：渲染大屏排行条形图组件。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from '@/components/charts/BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  data: { type: Array, default: () => [] }, // [{ name, value }]
  max: { type: Number, default: 8 }, // 声明max字段，作为组件配置、请求参数或图表数据的一部分。
  color: { type: String, default: '#3fe0ff' }, // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：格式化排行图中的数值。
function fmtNum(v) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : String(v) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  const d = [...props.data].slice(0, props.max).reverse() // 保存d相关业务数据，作为后续计算、渲染或请求的输入。
  return { // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    grid: { left: 6, right: 48, top: 6, bottom: 6, containLabel: true }, // 声明grid字段，作为组件配置、请求参数或图表数据的一部分。
    tooltip: { // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
      trigger: 'axis', // 声明trigger字段，作为组件配置、请求参数或图表数据的一部分。
      axisPointer: { type: 'shadow' }, // 声明axisPointer字段，作为组件配置、请求参数或图表数据的一部分。
      backgroundColor: 'rgba(7,25,50,0.92)', // 声明backgroundColor字段，作为组件配置、请求参数或图表数据的一部分。
      borderColor: 'rgba(63,224,255,0.4)', // 声明borderColor字段，作为组件配置、请求参数或图表数据的一部分。
      textStyle: { color: '#dbeeff' }, // 声明textStyle字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    xAxis: { // 声明xAxis字段，作为组件配置、请求参数或图表数据的一部分。
      type: 'value', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      splitLine: { lineStyle: { color: 'rgba(63,224,255,0.08)' } }, // 声明splitLine字段，作为组件配置、请求参数或图表数据的一部分。
      axisLabel: { color: '#6f9cc4', formatter: fmtNum }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
      axisLine: { show: false }, // 声明axisLine字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    yAxis: { // 声明yAxis字段，作为组件配置、请求参数或图表数据的一部分。
      type: 'category', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      data: d.map((x) => x.name), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
      axisTick: { show: false }, // 声明axisTick字段，作为组件配置、请求参数或图表数据的一部分。
      axisLine: { lineStyle: { color: 'rgba(63,224,255,0.2)' } }, // 声明axisLine字段，作为组件配置、请求参数或图表数据的一部分。
      axisLabel: { color: '#cfe8ff' }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
      { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
        type: 'bar', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
        data: d.map((x) => x.value), // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
        barWidth: '52%', // 声明barWidth字段，作为组件配置、请求参数或图表数据的一部分。
        itemStyle: { // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
          borderRadius: [0, 6, 6, 0], // 声明borderRadius字段，作为组件配置、请求参数或图表数据的一部分。
          color: { // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
            type: 'linear', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
            x: 0, // 声明x字段，作为组件配置、请求参数或图表数据的一部分。
            y: 0, // 声明y字段，作为组件配置、请求参数或图表数据的一部分。
            x2: 1, // 声明x2字段，作为组件配置、请求参数或图表数据的一部分。
            y2: 0, // 声明y2字段，作为组件配置、请求参数或图表数据的一部分。
            colorStops: [ // 声明colorStops字段，作为组件配置、请求参数或图表数据的一部分。
              { offset: 0, color: 'rgba(63,224,255,0.18)' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
              { offset: 1, color: props.color }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
            ], // 完成当前参数、配置或响应式数据结构的组装。
          }, // 完成当前参数、配置或响应式数据结构的组装。
        }, // 完成当前参数、配置或响应式数据结构的组装。
        label: { show: true, position: 'right', color: '#cfe8ff', formatter: (p) => fmtNum(p.value) }, // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
      }, // 完成当前参数、配置或响应式数据结构的组装。
    ], // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
