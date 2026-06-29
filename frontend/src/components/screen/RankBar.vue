<!-- 文件功能：渲染大屏排行条形图组件。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

import BaseChart from '@/components/charts/BaseChart.vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // [{ name, value }]
  max: { type: Number, default: 8 }, // 配置当前对象字段。
  color: { type: String, default: '#3fe0ff' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// 函数功能：格式化排行图中的数值。
function fmtNum(v) { // 声明当前函数入口。
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : String(v) // 返回当前表达式结果。
} // 结束当前代码块或数据结构。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 声明并初始化当前变量。
  const d = [...props.data].slice(0, props.max).reverse() // 声明并初始化当前变量。
  return { // 返回当前表达式结果。
    grid: { left: 6, right: 48, top: 6, bottom: 6, containLabel: true }, // 配置当前对象字段。
    tooltip: { // 配置当前对象字段。
      trigger: 'axis', // 配置当前对象字段。
      axisPointer: { type: 'shadow' }, // 配置当前对象字段。
      backgroundColor: 'rgba(7,25,50,0.92)', // 配置当前对象字段。
      borderColor: 'rgba(63,224,255,0.4)', // 配置当前对象字段。
      textStyle: { color: '#dbeeff' }, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
    xAxis: { // 配置当前对象字段。
      type: 'value', // 配置当前对象字段。
      splitLine: { lineStyle: { color: 'rgba(63,224,255,0.08)' } }, // 配置当前对象字段。
      axisLabel: { color: '#6f9cc4', formatter: fmtNum }, // 配置当前对象字段。
      axisLine: { show: false }, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
    yAxis: { // 配置当前对象字段。
      type: 'category', // 配置当前对象字段。
      data: d.map((x) => x.name), // 配置当前对象字段。
      axisTick: { show: false }, // 配置当前对象字段。
      axisLine: { lineStyle: { color: 'rgba(63,224,255,0.2)' } }, // 配置当前对象字段。
      axisLabel: { color: '#cfe8ff' }, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
    series: [ // 执行本行前端逻辑。
      { // 执行本行前端逻辑。
        type: 'bar', // 配置当前对象字段。
        data: d.map((x) => x.value), // 配置当前对象字段。
        barWidth: '52%', // 配置当前对象字段。
        itemStyle: { // 配置当前对象字段。
          borderRadius: [0, 6, 6, 0], // 配置当前对象字段。
          color: { // 配置当前对象字段。
            type: 'linear', // 配置当前对象字段。
            x: 0, // 配置当前对象字段。
            y: 0, // 配置当前对象字段。
            x2: 1, // 配置当前对象字段。
            y2: 0, // 配置当前对象字段。
            colorStops: [ // 执行本行前端逻辑。
              { offset: 0, color: 'rgba(63,224,255,0.18)' }, // 配置当前对象字段。
              { offset: 1, color: props.color }, // 配置当前对象字段。
            ], // 结束当前代码块或数据结构。
          }, // 结束当前代码块或数据结构。
        }, // 结束当前代码块或数据结构。
        label: { show: true, position: 'right', color: '#cfe8ff', formatter: (p) => fmtNum(p.value) }, // 配置当前对象字段。
      }, // 结束当前代码块或数据结构。
    ], // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
