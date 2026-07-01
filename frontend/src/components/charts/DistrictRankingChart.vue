<!-- 文件功能：根据区域均价排行数据生成横向柱状图配置并渲染。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from './BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  data: { type: Array, default: () => [] }, // 设置 data: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  height: { type: String, default: '360px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 创建 option，用于保存页面状态、计算结果或接口参数。
  // 真实城市可能有数十个商圈，仅取均价最高的前 N 个，避免条形图过密。
  const LIMIT = 18 // 创建 LIMIT，用于保存页面状态、计算结果或接口参数。
  const top = [...props.data] // 创建 top，用于保存页面状态、计算结果或接口参数。
    .sort((a, b) => b.avg_unit_price - a.avg_unit_price) // 设置 .sort((a, b 的值，作为后续渲染、计算或请求的输入。
    .slice(0, LIMIT) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  // Show ascending so the highest bar sits on top of the horizontal chart.
  const sorted = top.sort((a, b) => a.avg_unit_price - b.avg_unit_price) // 创建 sorted，用于保存页面状态、计算结果或接口参数。
  return { // 返回整理后的数据、组件配置或渲染结果。
    grid: { left: 12, right: 60, top: 16, bottom: 16, containLabel: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    tooltip: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      trigger: 'axis', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisPointer: { type: 'shadow' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      valueFormatter: (v) => `${v.toLocaleString()} 元/㎡`, // 设置 valueFormatter: (v 的值，作为后续渲染、计算或请求的输入。
    }, // 结束当前函数、对象、数组或组件配置块。
    xAxis: { type: 'value', axisLabel: { formatter: (v) => v / 10000 + '万' } }, // 设置 xAxis: { type: 'value', axisLabel: { formatter: (v 的值，作为后续渲染、计算或请求的输入。
    yAxis: { type: 'category', data: sorted.map((d) => d.name) }, // 设置 yAxis: { type: 'category', data: sorted.map((d 的值，作为后续渲染、计算或请求的输入。
    series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        type: 'bar', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        data: sorted.map((d) => d.avg_unit_price), // 设置 data: sorted.map((d 的值，作为后续渲染、计算或请求的输入。
        barWidth: '60%', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        label: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          show: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          position: 'right', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          formatter: (p) => (p.value / 10000).toFixed(1) + '万', // 更新 formatter: (p) 响应式状态，让页面展示与最新数据保持一致。
          color: '#475569', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        }, // 结束当前函数、对象、数组或组件配置块。
        itemStyle: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          borderRadius: [0, 6, 6, 0], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          color: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            type: 'linear', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            x: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            y: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            x2: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            y2: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            colorStops: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
              { offset: 0, color: '#60a5fa' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
              { offset: 1, color: '#1d4ed8' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            ], // 结束当前函数、对象、数组或组件配置块。
          }, // 结束当前函数、对象、数组或组件配置块。
        }, // 结束当前函数、对象、数组或组件配置块。
      }, // 结束当前函数、对象、数组或组件配置块。
    ], // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
