<!-- 文件功能：根据历史均价数据生成区域房价趋势折线图。 -->
<script setup>
import { computed } from 'vue' // 逐行注释：导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 逐行注释：配置当前对象字段。
  height: { type: String, default: '320px' }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 逐行注释：声明并初始化当前变量。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 逐行注释：配置当前对象字段。
  tooltip: { // 逐行注释：配置当前对象字段。
    trigger: 'axis', // 逐行注释：配置当前对象字段。
    valueFormatter: (v) => `${Number(v).toLocaleString()} 元/㎡`, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  xAxis: { // 逐行注释：配置当前对象字段。
    type: 'category', // 逐行注释：配置当前对象字段。
    boundaryGap: false, // 逐行注释：配置当前对象字段。
    data: props.data.map((d) => d.month), // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  yAxis: { // 逐行注释：配置当前对象字段。
    type: 'value', // 逐行注释：配置当前对象字段。
    scale: true, // 逐行注释：配置当前对象字段。
    name: '元/㎡', // 逐行注释：配置当前对象字段。
    axisLabel: { formatter: (v) => v / 10000 + '万' }, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  series: [ // 逐行注释：执行本行前端逻辑。
    { // 逐行注释：执行本行前端逻辑。
      type: 'line', // 逐行注释：配置当前对象字段。
      smooth: true, // 逐行注释：配置当前对象字段。
      symbol: 'circle', // 逐行注释：配置当前对象字段。
      symbolSize: 6, // 逐行注释：配置当前对象字段。
      data: props.data.map((d) => d.avg_unit_price), // 逐行注释：配置当前对象字段。
      lineStyle: { width: 3, color: '#2563eb' }, // 逐行注释：配置当前对象字段。
      itemStyle: { color: '#2563eb' }, // 逐行注释：配置当前对象字段。
      areaStyle: { // 逐行注释：配置当前对象字段。
        color: { // 逐行注释：配置当前对象字段。
          type: 'linear', // 逐行注释：配置当前对象字段。
          x: 0, // 逐行注释：配置当前对象字段。
          y: 0, // 逐行注释：配置当前对象字段。
          x2: 0, // 逐行注释：配置当前对象字段。
          y2: 1, // 逐行注释：配置当前对象字段。
          colorStops: [ // 逐行注释：执行本行前端逻辑。
            { offset: 0, color: 'rgba(37,99,235,0.35)' }, // 逐行注释：配置当前对象字段。
            { offset: 1, color: 'rgba(37,99,235,0.02)' }, // 逐行注释：配置当前对象字段。
          ], // 逐行注释：结束当前代码块或数据结构。
        }, // 逐行注释：结束当前代码块或数据结构。
      }, // 逐行注释：结束当前代码块或数据结构。
    }, // 逐行注释：结束当前代码块或数据结构。
  ], // 逐行注释：结束当前代码块或数据结构。
})) // 逐行注释：执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
