<!-- 文件功能：根据历史均价数据生成区域房价趋势折线图。 -->
<script setup>
import { computed } from 'vue'

import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '320px' },
})

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({
  grid: { left: 12, right: 20, top: 24, bottom: 16, containLabel: true },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (v) => `${Number(v).toLocaleString()} 元/㎡`,
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: props.data.map((d) => d.month),
  },
  yAxis: {
    type: 'value',
    scale: true,
    name: '元/㎡',
    axisLabel: { formatter: (v) => v / 10000 + '万' },
  },
  series: [
    {
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: props.data.map((d) => d.avg_unit_price),
      lineStyle: { width: 3, color: '#2563eb' },
      itemStyle: { color: '#2563eb' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(37,99,235,0.35)' },
            { offset: 1, color: 'rgba(37,99,235,0.02)' },
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
