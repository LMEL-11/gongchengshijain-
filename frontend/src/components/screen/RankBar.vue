<!-- 文件功能：渲染大屏排行条形图组件。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from '@/components/charts/BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  data: { type: Array, default: () => [] }, // 设置 data: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  max: { type: Number, default: 8 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  color: { type: String, default: '#3fe0ff' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：格式化排行图中的数值。
function fmtNum(v) { // 定义 fmtNum 函数，处理页面交互、数据加载或状态同步。
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : String(v) // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 创建 option，用于保存页面状态、计算结果或接口参数。
  const d = [...props.data].slice(0, props.max).reverse() // 创建 d，用于保存页面状态、计算结果或接口参数。
  return { // 返回整理后的数据、组件配置或渲染结果。
    grid: { left: 6, right: 48, top: 6, bottom: 6, containLabel: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    tooltip: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      trigger: 'axis', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisPointer: { type: 'shadow' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      backgroundColor: 'rgba(7,25,50,0.92)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      borderColor: 'rgba(63,224,255,0.4)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      textStyle: { color: '#dbeeff' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    xAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'value', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      splitLine: { lineStyle: { color: 'rgba(63,224,255,0.08)' } }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisLabel: { color: '#6f9cc4', formatter: fmtNum }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisLine: { show: false }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    yAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'category', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      data: d.map((x) => x.name), // 设置 data: d.map((x 的值，作为后续渲染、计算或请求的输入。
      axisTick: { show: false }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisLine: { lineStyle: { color: 'rgba(63,224,255,0.2)' } }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisLabel: { color: '#cfe8ff' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        type: 'bar', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        data: d.map((x) => x.value), // 更新 data: d.map((x) 响应式状态，让页面展示与最新数据保持一致。
        barWidth: '52%', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        itemStyle: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          borderRadius: [0, 6, 6, 0], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          color: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            type: 'linear', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            x: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            y: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            x2: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            y2: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            colorStops: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
              { offset: 0, color: 'rgba(63,224,255,0.18)' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
              { offset: 1, color: props.color }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
            ], // 结束当前函数、对象、数组或组件配置块。
          }, // 结束当前函数、对象、数组或组件配置块。
        }, // 结束当前函数、对象、数组或组件配置块。
        label: { show: true, position: 'right', color: '#cfe8ff', formatter: (p) => fmtNum(p.value) }, // 更新 label: { show: true, position: 'right', color: '#cfe8ff', formatter: (p) 响应式状态，让页面展示与最新数据保持一致。
      }, // 结束当前函数、对象、数组或组件配置块。
    ], // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
