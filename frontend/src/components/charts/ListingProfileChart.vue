<!-- 文件功能：展示区域挂牌走势、交易属性分布和税费标签画像。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。

import BaseChart from './BaseChart.vue' // 导入 BaseChart，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  data: { type: Array, default: () => [] }, // 设置 data: { type: Array, default:  的值，作为后续渲染、计算或请求的输入。
  height: { type: String, default: '280px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// 函数功能：格式化挂牌画像中的价格展示文本。
function priceLabel(value) { // 定义 priceLabel 函数，处理页面交互、数据加载或状态同步。
  if (!value) return '暂无' // 根据当前页面状态或接口结果决定是否进入该分支。
  return `${Number(value).toLocaleString()} 元/㎡` // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 创建 option，用于保存页面状态、计算结果或接口参数。
  color: ['#10b981', '#f59e0b'], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  grid: { left: 12, right: 56, top: 42, bottom: 20, containLabel: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  legend: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    top: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    right: 0, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    data: ['挂牌套数', '挂牌均价'], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  tooltip: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    trigger: 'axis', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    axisPointer: { type: 'cross' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    formatter: (params) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
      const month = params[0]?.axisValue || '' // 创建 month，用于保存页面状态、计算结果或接口参数。
      const lines = params // 创建 lines，用于保存页面状态、计算结果或接口参数。
        .map((item) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
          const value = // 创建 value，用于保存页面状态、计算结果或接口参数。
            item.seriesName === '挂牌均价' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
              ? priceLabel(item.value) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
              : `${Number(item.value || 0).toLocaleString()} 套` // 执行当前前端代码行，推动页面数据和交互流程继续运行。
          return `${item.marker}${item.seriesName}：${value}` // 返回整理后的数据、组件配置或渲染结果。
        }) // 结束当前函数、对象、数组或组件配置块。
        .join('<br/>') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      return `<b>${month}</b><br/>${lines}` // 返回整理后的数据、组件配置或渲染结果。
    }, // 结束当前函数、对象、数组或组件配置块。
  }, // 结束当前函数、对象、数组或组件配置块。
  xAxis: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    type: 'category', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    data: props.data.map((d) => d.month), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
    axisLabel: { rotate: 35 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  yAxis: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { type: 'value', name: '房源套数', minInterval: 1 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'value', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: '元/㎡', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      scale: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      axisLabel: { formatter: (v) => `${(v / 10000).toFixed(1)}万` }, // 设置 axisLabel: { formatter: (v 的值，作为后续渲染、计算或请求的输入。
    }, // 结束当前函数、对象、数组或组件配置块。
  ], // 结束当前函数、对象、数组或组件配置块。
  series: [ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: '挂牌套数', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'bar', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      barWidth: '48%', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      data: props.data.map((d) => d.count), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
      itemStyle: { borderRadius: [6, 6, 0, 0] }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
    { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      name: '挂牌均价', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      type: 'line', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      yAxisIndex: 1, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      smooth: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      symbol: 'circle', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      symbolSize: 6, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      data: props.data.map((d) => d.avg_unit_price), // 设置 data: props.data.map((d 的值，作为后续渲染、计算或请求的输入。
      lineStyle: { width: 3 }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
  ], // 结束当前函数、对象、数组或组件配置块。
})) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
