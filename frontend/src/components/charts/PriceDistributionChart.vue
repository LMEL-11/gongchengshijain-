<!-- 文件功能：根据价格分布数据生成房源价格区间柱状图。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from './BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  data: { type: Array, default: () => [] }, // 设置 data: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  height: { type: String, default: '340px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 创建 option，用于保存页面状态、计算结果或接口参数。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  xAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: 'category', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    data: props.data.map((d) => d.range), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
    axisLabel: { rotate: 30 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  yAxis: { type: 'value', name: '房源套数' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'bar', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      data: props.data.map((d) => d.count), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
      barWidth: '55%', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      itemStyle: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        borderRadius: [6, 6, 0, 0], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        color: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          type: 'linear', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          x: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          y: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          x2: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          y2: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          colorStops: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            { offset: 0, color: '#34d399' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            { offset: 1, color: '#059669' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
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
