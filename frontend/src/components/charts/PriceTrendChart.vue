<!-- 文件功能：根据历史均价数据生成区域房价趋势折线图。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from './BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  data: { type: Array, default: () => [] }, // 设置 data: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  height: { type: String, default: '320px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 创建 option，用于保存页面状态、计算结果或接口参数。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  tooltip: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    trigger: 'axis', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    valueFormatter: (v) => `${Number(v).toLocaleString()} 元/㎡`, // 设置 valueFormatter: (v 的值，作为后续渲染、计算或请求的输入。
  }, // 结束当前函数、对象、数组或组件配置块。
  xAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: 'category', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    boundaryGap: false, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    data: props.data.map((d) => d.month), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
  }, // 结束当前函数、对象、数组或组件配置块。
  yAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: 'value', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    scale: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: '元/㎡', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    axisLabel: { formatter: (v) => v / 10000 + '万' }, // 设置 axisLabel: { formatter: (v 的值，作为后续渲染、计算或请求的输入。
  }, // 结束当前函数、对象、数组或组件配置块。
  series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'line', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      smooth: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      symbol: 'circle', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      symbolSize: 6, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      data: props.data.map((d) => d.avg_unit_price), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
      lineStyle: { width: 3, color: '#2563eb' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      itemStyle: { color: '#2563eb' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      areaStyle: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        color: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          type: 'linear', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          x: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          y: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          x2: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          y2: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          colorStops: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            { offset: 0, color: 'rgba(37,99,235,0.35)' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            { offset: 1, color: 'rgba(37,99,235,0.02)' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          ], // 结束当前函数、对象、数组或组件配置块。
        }, // 结束当前函数、对象、数组或组件配置块。
      }, // 结束当前函数、对象、数组或组件配置块。
    }, // 结束当前函数、对象、数组或组件配置块。
  ], // 结束当前函数、对象、数组或组件配置块。
})) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
