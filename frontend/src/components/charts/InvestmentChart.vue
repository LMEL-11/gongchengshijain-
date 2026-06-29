<!-- 文件功能：根据投资潜力排行数据生成雷达和柱状分析图配置。 -->
<script setup>
import { computed } from 'vue'

import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  height: { type: String, default: '400px' },
})

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => {
  const scores = props.data.map((d) => d.score)
  const min = scores.length ? Math.min(...scores) : 0
  const max = scores.length ? Math.max(...scores) : 100
  return {
    grid: { left: 12, right: 70, top: 30, bottom: 40, containLabel: true },
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        const [
          price,
          heat,
          count,
          name,
          score,
          valueScore,
          facilityScore,
          safetyScore,
          freshnessScore,
          categoryCount,
        ] = p.value
        return `<b>${name}</b><br/>投资评分：<b>${score}</b><br/>均价：${price.toLocaleString()} 元/㎡<br/>热度/配套指数：${heat}<br/>房源样本：${count} 套<br/>价格洼地：${valueScore}<br/>配套评分：${facilityScore}<br/>交易安全：${safetyScore}<br/>挂牌新鲜度：${freshnessScore}<br/>配套类别：${categoryCount} 类`
      },
    },
    xAxis: {
      type: 'value',
      name: '均价(元/㎡)',
      scale: true,
      axisLabel: { formatter: (v) => v / 10000 + '万' },
    },
    yAxis: { type: 'value', name: '热度/配套', min: 0, max: 100 },
    visualMap: {
      min,
      max,
      dimension: 4, // 第 5 个分量：投资评分
      calculable: true,
      text: ['评分高', '评分低'],
      right: 0,
      top: 'center',
      itemHeight: 140,
      inRange: { color: ['#cbd5e1', '#60a5fa', '#1d4ed8'] },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (val) => 12 + Math.min(Math.sqrt(Math.max(val[2], 1)) * 2.2, 52),
        data: props.data.map((d) => [
          d.avg_unit_price,
          d.heat_index,
          d.property_count,
          d.name,
          d.score,
          d.value_score,
          d.facility_score,
          d.safety_score,
          d.freshness_score,
          d.facility_category_count,
        ]),
        label: {
          show: true,
          position: 'top',
          formatter: (p) => p.value[3],
          fontSize: 11,
          color: '#475569',
        },
        itemStyle: { opacity: 0.85, borderColor: '#fff', borderWidth: 1 },
        emphasis: { focus: 'self', scale: 1.2 },
      },
    ],
  }
})
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
