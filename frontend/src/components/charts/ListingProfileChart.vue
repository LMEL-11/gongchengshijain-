<script setup>
import { computed } from 'vue'

import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '280px' },
})

function priceLabel(value) {
  if (!value) return '暂无'
  return `${Number(value).toLocaleString()} 元/㎡`
}

const option = computed(() => ({
  color: ['#10b981', '#f59e0b'],
  grid: { left: 12, right: 56, top: 42, bottom: 20, containLabel: true },
  legend: {
    top: 0,
    right: 0,
    data: ['挂牌套数', '挂牌均价'],
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    formatter: (params) => {
      const month = params[0]?.axisValue || ''
      const lines = params
        .map((item) => {
          const value =
            item.seriesName === '挂牌均价'
              ? priceLabel(item.value)
              : `${Number(item.value || 0).toLocaleString()} 套`
          return `${item.marker}${item.seriesName}：${value}`
        })
        .join('<br/>')
      return `<b>${month}</b><br/>${lines}`
    },
  },
  xAxis: {
    type: 'category',
    data: props.data.map((d) => d.month),
    axisLabel: { rotate: 35 },
  },
  yAxis: [
    { type: 'value', name: '房源套数', minInterval: 1 },
    {
      type: 'value',
      name: '元/㎡',
      scale: true,
      axisLabel: { formatter: (v) => `${(v / 10000).toFixed(1)}万` },
    },
  ],
  series: [
    {
      name: '挂牌套数',
      type: 'bar',
      barWidth: '48%',
      data: props.data.map((d) => d.count),
      itemStyle: { borderRadius: [6, 6, 0, 0] },
    },
    {
      name: '挂牌均价',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: props.data.map((d) => d.avg_unit_price),
      lineStyle: { width: 3 },
    },
  ],
}))
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
