<!-- 文件功能：根据价格分布数据生成房源价格区间柱状图。 -->
<script setup>
import { computed } from 'vue' // 逐行注释：导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 逐行注释：配置当前对象字段。
  height: { type: String, default: '340px' }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 逐行注释：声明并初始化当前变量。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 逐行注释：配置当前对象字段。
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, // 逐行注释：配置当前对象字段。
  xAxis: { // 逐行注释：配置当前对象字段。
    type: 'category', // 逐行注释：配置当前对象字段。
    data: props.data.map((d) => d.range), // 逐行注释：配置当前对象字段。
    axisLabel: { rotate: 30 }, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  yAxis: { type: 'value', name: '房源套数' }, // 逐行注释：配置当前对象字段。
  series: [ // 逐行注释：执行本行前端逻辑。
    { // 逐行注释：执行本行前端逻辑。
      type: 'bar', // 逐行注释：配置当前对象字段。
      data: props.data.map((d) => d.count), // 逐行注释：配置当前对象字段。
      barWidth: '55%', // 逐行注释：配置当前对象字段。
      itemStyle: { // 逐行注释：配置当前对象字段。
        borderRadius: [6, 6, 0, 0], // 逐行注释：配置当前对象字段。
        color: { // 逐行注释：配置当前对象字段。
          type: 'linear', // 逐行注释：配置当前对象字段。
          x: 0, // 逐行注释：配置当前对象字段。
          y: 0, // 逐行注释：配置当前对象字段。
          x2: 0, // 逐行注释：配置当前对象字段。
          y2: 1, // 逐行注释：配置当前对象字段。
          colorStops: [ // 逐行注释：执行本行前端逻辑。
            { offset: 0, color: '#34d399' }, // 逐行注释：配置当前对象字段。
            { offset: 1, color: '#059669' }, // 逐行注释：配置当前对象字段。
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
