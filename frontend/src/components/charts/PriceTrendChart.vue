<!-- 文件功能：根据历史均价数据生成区域房价趋势折线图。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 配置当前对象字段。
  height: { type: String, default: '320px' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 声明并初始化当前变量。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 配置当前对象字段。
  tooltip: { // 配置当前对象字段。
    trigger: 'axis', // 配置当前对象字段。
    valueFormatter: (v) => `${Number(v).toLocaleString()} 元/㎡`, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  xAxis: { // 配置当前对象字段。
    type: 'category', // 配置当前对象字段。
    boundaryGap: false, // 配置当前对象字段。
    data: props.data.map((d) => d.month), // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  yAxis: { // 配置当前对象字段。
    type: 'value', // 配置当前对象字段。
    scale: true, // 配置当前对象字段。
    name: '元/㎡', // 配置当前对象字段。
    axisLabel: { formatter: (v) => v / 10000 + '万' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  series: [ // 执行本行前端逻辑。
    { // 执行本行前端逻辑。
      type: 'line', // 配置当前对象字段。
      smooth: true, // 配置当前对象字段。
      symbol: 'circle', // 配置当前对象字段。
      symbolSize: 6, // 配置当前对象字段。
      data: props.data.map((d) => d.avg_unit_price), // 配置当前对象字段。
      lineStyle: { width: 3, color: '#2563eb' }, // 配置当前对象字段。
      itemStyle: { color: '#2563eb' }, // 配置当前对象字段。
      areaStyle: { // 配置当前对象字段。
        color: { // 配置当前对象字段。
          type: 'linear', // 配置当前对象字段。
          x: 0, // 配置当前对象字段。
          y: 0, // 配置当前对象字段。
          x2: 0, // 配置当前对象字段。
          y2: 1, // 配置当前对象字段。
          colorStops: [ // 执行本行前端逻辑。
            { offset: 0, color: 'rgba(37,99,235,0.35)' }, // 配置当前对象字段。
            { offset: 1, color: 'rgba(37,99,235,0.02)' }, // 配置当前对象字段。
          ], // 结束当前代码块或数据结构。
        }, // 结束当前代码块或数据结构。
      }, // 结束当前代码块或数据结构。
    }, // 结束当前代码块或数据结构。
  ], // 结束当前代码块或数据结构。
})) // 执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
