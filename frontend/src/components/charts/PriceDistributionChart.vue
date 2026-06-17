<script setup>
import { computed } from 'vue'

import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '340px' },
})

const option = computed(() => ({
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  xAxis: {
    type: 'category',
    data: props.data.map((d) => d.range),
    axisLabel: { rotate: 30 },
  },
  yAxis: { type: 'value', name: '房源套数' },
  series: [
    {
      type: 'bar',
      data: props.data.map((d) => d.count),
      barWidth: '55%',
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#34d399' },
            { offset: 1, color: '#059669' },
          ],
        },
      },
    },
  ],
}))
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
