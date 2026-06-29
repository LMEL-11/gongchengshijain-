<!-- 文件功能：根据区域均价排行数据生成横向柱状图配置并渲染。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 配置当前对象字段。
  height: { type: String, default: '360px' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 声明并初始化当前变量。
  // 真实城市可能有数十个商圈，仅取均价最高的前 N 个，避免条形图过密。
  const LIMIT = 18 // 声明并初始化当前变量。
  const top = [...props.data] // 声明并初始化当前变量。
    .sort((a, b) => b.avg_unit_price - a.avg_unit_price) // 执行本行前端逻辑。
    .slice(0, LIMIT) // 执行本行前端逻辑。
  // Show ascending so the highest bar sits on top of the horizontal chart.
  const sorted = top.sort((a, b) => a.avg_unit_price - b.avg_unit_price) // 声明并初始化当前变量。
  return { // 返回当前表达式结果。
    grid: { left: 12, right: 60, top: 16, bottom: 16, containLabel: true }, // 配置当前对象字段。
    tooltip: { // 配置当前对象字段。
      trigger: 'axis', // 配置当前对象字段。
      axisPointer: { type: 'shadow' }, // 配置当前对象字段。
      valueFormatter: (v) => `${v.toLocaleString()} 元/㎡`, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
    xAxis: { type: 'value', axisLabel: { formatter: (v) => v / 10000 + '万' } }, // 配置当前对象字段。
    yAxis: { type: 'category', data: sorted.map((d) => d.name) }, // 配置当前对象字段。
    series: [ // 执行本行前端逻辑。
      { // 执行本行前端逻辑。
        type: 'bar', // 配置当前对象字段。
        data: sorted.map((d) => d.avg_unit_price), // 配置当前对象字段。
        barWidth: '60%', // 配置当前对象字段。
        label: { // 配置当前对象字段。
          show: true, // 配置当前对象字段。
          position: 'right', // 配置当前对象字段。
          formatter: (p) => (p.value / 10000).toFixed(1) + '万', // 配置当前对象字段。
          color: '#475569', // 配置当前对象字段。
        }, // 结束当前代码块或数据结构。
        itemStyle: { // 配置当前对象字段。
          borderRadius: [0, 6, 6, 0], // 配置当前对象字段。
          color: { // 配置当前对象字段。
            type: 'linear', // 配置当前对象字段。
            x: 0, // 配置当前对象字段。
            y: 0, // 配置当前对象字段。
            x2: 1, // 配置当前对象字段。
            y2: 0, // 配置当前对象字段。
            colorStops: [ // 执行本行前端逻辑。
              { offset: 0, color: '#60a5fa' }, // 配置当前对象字段。
              { offset: 1, color: '#1d4ed8' }, // 配置当前对象字段。
            ], // 结束当前代码块或数据结构。
          }, // 结束当前代码块或数据结构。
        }, // 结束当前代码块或数据结构。
      }, // 结束当前代码块或数据结构。
    ], // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
