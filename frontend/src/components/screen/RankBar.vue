<!-- 文件功能：渲染大屏排行条形图组件。 -->
<script setup>
import { computed } from 'vue'

import BaseChart from '@/components/charts/BaseChart.vue'

const props = defineProps({
  data: { type: Array, default: () => [] }, // [{ name, value }]
  max: { type: Number, default: 8 },
  color: { type: String, default: '#3fe0ff' },
})

// 函数功能：格式化排行图中的数值。
function fmtNum(v) {
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : String(v)
}

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => {
  const d = [...props.data].slice(0, props.max).reverse()
  return {
    grid: { left: 6, right: 48, top: 6, bottom: 6, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(7,25,50,0.92)',
      borderColor: 'rgba(63,224,255,0.4)',
      textStyle: { color: '#dbeeff' },
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(63,224,255,0.08)' } },
      axisLabel: { color: '#6f9cc4', formatter: fmtNum },
      axisLine: { show: false },
    },
    yAxis: {
      type: 'category',
      data: d.map((x) => x.name),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(63,224,255,0.2)' } },
      axisLabel: { color: '#cfe8ff' },
    },
    series: [
      {
        type: 'bar',
        data: d.map((x) => x.value),
        barWidth: '52%',
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: 'rgba(63,224,255,0.18)' },
              { offset: 1, color: props.color },
            ],
          },
        },
        label: { show: true, position: 'right', color: '#cfe8ff', formatter: (p) => fmtNum(p.value) },
      },
    ],
  }
})
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
