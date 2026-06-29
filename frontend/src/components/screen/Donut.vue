<!-- 文件功能：渲染大屏环形占比图组件。 -->
<script setup>
import { computed } from 'vue' // 逐行注释：导入本行所需的依赖。

import BaseChart from '@/components/charts/BaseChart.vue' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  items: { type: Array, default: () => [] }, // [{ name, value }]
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 逐行注释：声明并初始化当前变量。
  color: ['#3fe0ff', '#7c8cff', '#ffd166'], // 逐行注释：配置当前对象字段。
  tooltip: { // 逐行注释：配置当前对象字段。
    trigger: 'item', // 逐行注释：配置当前对象字段。
    backgroundColor: 'rgba(7,25,50,0.92)', // 逐行注释：配置当前对象字段。
    borderColor: 'rgba(63,224,255,0.4)', // 逐行注释：配置当前对象字段。
    textStyle: { color: '#dbeeff' }, // 逐行注释：配置当前对象字段。
    formatter: (p) => `${p.name}<br/><b>${Number(p.value).toLocaleString()}</b> 套 (${p.percent}%)`, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  legend: { // 逐行注释：配置当前对象字段。
    bottom: 0, // 逐行注释：配置当前对象字段。
    icon: 'circle', // 逐行注释：配置当前对象字段。
    itemWidth: 9, // 逐行注释：配置当前对象字段。
    itemHeight: 9, // 逐行注释：配置当前对象字段。
    textStyle: { color: '#cfe8ff', fontSize: 12 }, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  series: [ // 逐行注释：执行本行前端逻辑。
    { // 逐行注释：执行本行前端逻辑。
      type: 'pie', // 逐行注释：配置当前对象字段。
      radius: ['46%', '70%'], // 逐行注释：配置当前对象字段。
      center: ['50%', '44%'], // 逐行注释：配置当前对象字段。
      avoidLabelOverlap: true, // 逐行注释：配置当前对象字段。
      itemStyle: { borderColor: '#06122b', borderWidth: 2 }, // 逐行注释：配置当前对象字段。
      label: { color: '#cfe8ff', formatter: '{d}%' }, // 逐行注释：配置当前对象字段。
      labelLine: { length: 8, length2: 8 }, // 逐行注释：配置当前对象字段。
      data: props.items, // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
  ], // 逐行注释：结束当前代码块或数据结构。
})) // 逐行注释：执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
