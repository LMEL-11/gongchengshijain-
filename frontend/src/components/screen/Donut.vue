<!-- 文件功能：渲染大屏环形占比图组件。 -->
<script setup>
import { computed } from 'vue'

import BaseChart from '@/components/charts/BaseChart.vue'

const props = defineProps({
  items: { type: Array, default: () => [] }, // [{ name, value }]
})

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({
  color: ['#3fe0ff', '#7c8cff', '#ffd166'],
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(7,25,50,0.92)',
    borderColor: 'rgba(63,224,255,0.4)',
    textStyle: { color: '#dbeeff' },
    formatter: (p) => `${p.name}<br/><b>${Number(p.value).toLocaleString()}</b> 套 (${p.percent}%)`,
  },
  legend: {
    bottom: 0,
    icon: 'circle',
    itemWidth: 9,
    itemHeight: 9,
    textStyle: { color: '#cfe8ff', fontSize: 12 },
  },
  series: [
    {
      type: 'pie',
      radius: ['46%', '70%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      itemStyle: { borderColor: '#06122b', borderWidth: 2 },
      label: { color: '#cfe8ff', formatter: '{d}%' },
      labelLine: { length: 8, length2: 8 },
      data: props.items,
    },
  ],
}))
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
