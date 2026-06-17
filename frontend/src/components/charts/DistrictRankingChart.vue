<script setup>
import { computed } from 'vue'

import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '360px' },
})

const option = computed(() => {
  // 真实城市可能有数十个商圈，仅取均价最高的前 N 个，避免条形图过密。
  const LIMIT = 18
  const top = [...props.data]
    .sort((a, b) => b.avg_unit_price - a.avg_unit_price)
    .slice(0, LIMIT)
  // Show ascending so the highest bar sits on top of the horizontal chart.
  const sorted = top.sort((a, b) => a.avg_unit_price - b.avg_unit_price)
  return {
    grid: { left: 12, right: 60, top: 16, bottom: 16, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      valueFormatter: (v) => `${v.toLocaleString()} 元/㎡`,
    },
    xAxis: { type: 'value', axisLabel: { formatter: (v) => v / 10000 + '万' } },
    yAxis: { type: 'category', data: sorted.map((d) => d.name) },
    series: [
      {
        type: 'bar',
        data: sorted.map((d) => d.avg_unit_price),
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: (p) => (p.value / 10000).toFixed(1) + '万',
          color: '#475569',
        },
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#60a5fa' },
              { offset: 1, color: '#1d4ed8' },
            ],
          },
        },
      },
    ],
  }
})
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
