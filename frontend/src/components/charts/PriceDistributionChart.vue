<!-- 文件功能：根据价格分布数据生成房源价格区间柱状图。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 配置当前对象字段。
  height: { type: String, default: '340px' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 声明并初始化当前变量。
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true }, // 配置当前对象字段。
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, // 配置当前对象字段。
  xAxis: { // 配置当前对象字段。
    type: 'category', // 配置当前对象字段。
    data: props.data.map((d) => d.range), // 配置当前对象字段。
    axisLabel: { rotate: 30 }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  yAxis: { type: 'value', name: '房源套数' }, // 配置当前对象字段。
  series: [ // 执行本行前端逻辑。
    { // 执行本行前端逻辑。
      type: 'bar', // 配置当前对象字段。
      data: props.data.map((d) => d.count), // 配置当前对象字段。
      barWidth: '55%', // 配置当前对象字段。
      itemStyle: { // 配置当前对象字段。
        borderRadius: [6, 6, 0, 0], // 配置当前对象字段。
        color: { // 配置当前对象字段。
          type: 'linear', // 配置当前对象字段。
          x: 0, // 配置当前对象字段。
          y: 0, // 配置当前对象字段。
          x2: 0, // 配置当前对象字段。
          y2: 1, // 配置当前对象字段。
          colorStops: [ // 执行本行前端逻辑。
            { offset: 0, color: '#34d399' }, // 配置当前对象字段。
            { offset: 1, color: '#059669' }, // 配置当前对象字段。
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
