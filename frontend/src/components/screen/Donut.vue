<!-- 文件功能：渲染大屏环形占比图组件。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

import BaseChart from '@/components/charts/BaseChart.vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  items: { type: Array, default: () => [] }, // [{ name, value }]
}) // 执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 声明并初始化当前变量。
  color: ['#3fe0ff', '#7c8cff', '#ffd166'], // 配置当前对象字段。
  tooltip: { // 配置当前对象字段。
    trigger: 'item', // 配置当前对象字段。
    backgroundColor: 'rgba(7,25,50,0.92)', // 配置当前对象字段。
    borderColor: 'rgba(63,224,255,0.4)', // 配置当前对象字段。
    textStyle: { color: '#dbeeff' }, // 配置当前对象字段。
    formatter: (p) => `${p.name}<br/><b>${Number(p.value).toLocaleString()}</b> 套 (${p.percent}%)`, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  legend: { // 配置当前对象字段。
    bottom: 0, // 配置当前对象字段。
    icon: 'circle', // 配置当前对象字段。
    itemWidth: 9, // 配置当前对象字段。
    itemHeight: 9, // 配置当前对象字段。
    textStyle: { color: '#cfe8ff', fontSize: 12 }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  series: [ // 执行本行前端逻辑。
    { // 执行本行前端逻辑。
      type: 'pie', // 配置当前对象字段。
      radius: ['46%', '70%'], // 配置当前对象字段。
      center: ['50%', '44%'], // 配置当前对象字段。
      avoidLabelOverlap: true, // 配置当前对象字段。
      itemStyle: { borderColor: '#06122b', borderWidth: 2 }, // 配置当前对象字段。
      label: { color: '#cfe8ff', formatter: '{d}%' }, // 配置当前对象字段。
      labelLine: { length: 8, length2: 8 }, // 配置当前对象字段。
      data: props.items, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
  ], // 结束当前代码块或数据结构。
})) // 执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
