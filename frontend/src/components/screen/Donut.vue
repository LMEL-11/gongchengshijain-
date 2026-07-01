<!-- 文件功能：渲染大屏环形占比图组件。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from '@/components/charts/BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  items: { type: Array, default: () => [] }, // 设置 items: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 创建 option，用于保存页面状态、计算结果或接口参数。
  color: ['#3fe0ff', '#7c8cff', '#ffd166'], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  tooltip: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    trigger: 'item', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    backgroundColor: 'rgba(7,25,50,0.92)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    borderColor: 'rgba(63,224,255,0.4)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    textStyle: { color: '#dbeeff' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    formatter: (p) => `${p.name}<br/><b>${Number(p.value).toLocaleString()}</b> 套 (${p.percent}%)`, // 更新 formatter: (p) 响应式状态，让页面展示与最新数据保持一致。
  }, // 结束当前函数、对象、数组或组件配置块。
  legend: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    bottom: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    icon: 'circle', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    itemWidth: 9, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    itemHeight: 9, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    textStyle: { color: '#cfe8ff', fontSize: 12 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'pie', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      radius: ['46%', '70%'], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      center: ['50%', '44%'], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      avoidLabelOverlap: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      itemStyle: { borderColor: '#06122b', borderWidth: 2 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      label: { color: '#cfe8ff', formatter: '{d}%' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      labelLine: { length: 8, length2: 8 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      data: props.items, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
  ], // 结束当前函数、对象、数组或组件配置块。
})) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
