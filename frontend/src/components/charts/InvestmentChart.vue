<!-- 文件功能：根据投资潜力排行数据生成雷达和柱状分析图配置。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from './BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  data: { type: Array, default: () => [] }, // 设置 data: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  height: { type: String, default: '400px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 创建 option，用于保存页面状态、计算结果或接口参数。
  const scores = props.data.map((d) => d.score) // 创建 scores，用于保存页面状态、计算结果或接口参数。
  const min = scores.length ? Math.min(...scores) : 0 // 创建 min，用于保存页面状态、计算结果或接口参数。
  const max = scores.length ? Math.max(...scores) : 100 // 创建 max，用于保存页面状态、计算结果或接口参数。
  return { // 返回整理后的数据、组件配置或渲染结果。
    grid: { left: 12, right: 70, top: 30, bottom: 40, containLabel: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    tooltip: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      trigger: 'item', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      formatter: (p) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
        const [ // 创建 [，用于保存页面状态、计算结果或接口参数。
          price, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          heat, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          count, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          score, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          valueScore, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          facilityScore, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          safetyScore, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          freshnessScore, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          categoryCount, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        ] = p.value // 更新 ] 响应式状态，让页面展示与最新数据保持一致。
        return `<b>${name}</b><br/>投资评分：<b>${score}</b><br/>均价：${price.toLocaleString()} 元/㎡<br/>热度/配套指数：${heat}<br/>房源样本：${count} 套<br/>价格洼地：${valueScore}<br/>配套评分：${facilityScore}<br/>交易安全：${safetyScore}<br/>挂牌新鲜度：${freshnessScore}<br/>配套类别：${categoryCount} 类` // 返回整理后的数据、组件配置或渲染结果。
      }, // 结束当前函数、对象、数组或组件配置块。
    }, // 结束当前函数、对象、数组或组件配置块。
    xAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'value', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: '均价(元/㎡)', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      scale: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisLabel: { formatter: (v) => v / 10000 + '万' }, // 设置 axisLabel: { formatter: (v 的值，作为后续渲染、计算或请求的输入。
    }, // 结束当前函数、对象、数组或组件配置块。
    yAxis: { type: 'value', name: '热度/配套', min: 0, max: 100 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    visualMap: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      min, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      max, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      dimension: 4, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      calculable: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      text: ['评分高', '评分低'], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      right: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      top: 'center', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      itemHeight: 140, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      inRange: { color: ['#cbd5e1', '#60a5fa', '#1d4ed8'] }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        type: 'scatter', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        symbolSize: (val) => 12 + Math.min(Math.sqrt(Math.max(val[2], 1)) * 2.2, 52), // 设置 symbolSize: (val 的值，作为后续渲染、计算或请求的输入。
        data: props.data.map((d) => [ // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
          d.avg_unit_price, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.heat_index, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.property_count, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.name, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.score, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.value_score, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.facility_score, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.safety_score, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.freshness_score, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          d.facility_category_count, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        ]), // 结束当前函数、对象、数组或组件配置块。
        label: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          show: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          position: 'top', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          formatter: (p) => p.value[3], // 更新 formatter: (p) 响应式状态，让页面展示与最新数据保持一致。
          fontSize: 11, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          color: '#475569', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        }, // 结束当前函数、对象、数组或组件配置块。
        itemStyle: { opacity: 0.85, borderColor: '#fff', borderWidth: 1 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        emphasis: { focus: 'self', scale: 1.2 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      }, // 结束当前函数、对象、数组或组件配置块。
    ], // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
