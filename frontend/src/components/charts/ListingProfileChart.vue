<!-- 文件功能：展示区域挂牌走势、交易属性分布和税费标签画像。 -->
<script setup>
import { computed } from 'vue' // 逐行注释：导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 逐行注释：配置当前对象字段。
  height: { type: String, default: '280px' }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。

// 函数功能：格式化挂牌画像中的价格展示文本。
function priceLabel(value) { // 逐行注释：声明当前函数入口。
  if (!value) return '暂无' // 逐行注释：根据条件判断是否执行分支。
  return `${Number(value).toLocaleString()} 元/㎡` // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 逐行注释：声明并初始化当前变量。
  color: ['#10b981', '#f59e0b'], // 逐行注释：配置当前对象字段。
  grid: { left: 12, right: 56, top: 42, bottom: 20, containLabel: true }, // 逐行注释：配置当前对象字段。
  legend: { // 逐行注释：配置当前对象字段。
    top: 0, // 逐行注释：配置当前对象字段。
    right: 0, // 逐行注释：配置当前对象字段。
    data: ['挂牌套数', '挂牌均价'], // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  tooltip: { // 逐行注释：配置当前对象字段。
    trigger: 'axis', // 逐行注释：配置当前对象字段。
    axisPointer: { type: 'cross' }, // 逐行注释：配置当前对象字段。
    formatter: (params) => { // 逐行注释：配置当前对象字段。
      const month = params[0]?.axisValue || '' // 逐行注释：声明并初始化当前变量。
      const lines = params // 逐行注释：声明并初始化当前变量。
        .map((item) => { // 逐行注释：执行本行前端逻辑。
          const value = // 逐行注释：声明并初始化当前变量。
            item.seriesName === '挂牌均价' // 逐行注释：执行本行前端逻辑。
              ? priceLabel(item.value) // 逐行注释：执行本行前端逻辑。
              : `${Number(item.value || 0).toLocaleString()} 套` // 逐行注释：执行本行前端逻辑。
          return `${item.marker}${item.seriesName}：${value}` // 逐行注释：返回当前表达式结果。
        }) // 逐行注释：执行本行前端逻辑。
        .join('<br/>') // 逐行注释：执行本行前端逻辑。
      return `<b>${month}</b><br/>${lines}` // 逐行注释：返回当前表达式结果。
    }, // 逐行注释：结束当前代码块或数据结构。
  }, // 逐行注释：结束当前代码块或数据结构。
  xAxis: { // 逐行注释：配置当前对象字段。
    type: 'category', // 逐行注释：配置当前对象字段。
    data: props.data.map((d) => d.month), // 逐行注释：配置当前对象字段。
    axisLabel: { rotate: 35 }, // 逐行注释：配置当前对象字段。
  }, // 逐行注释：结束当前代码块或数据结构。
  yAxis: [ // 逐行注释：执行本行前端逻辑。
    { type: 'value', name: '房源套数', minInterval: 1 }, // 逐行注释：配置当前对象字段。
    { // 逐行注释：执行本行前端逻辑。
      type: 'value', // 逐行注释：配置当前对象字段。
      name: '元/㎡', // 逐行注释：配置当前对象字段。
      scale: true, // 逐行注释：配置当前对象字段。
      axisLabel: { formatter: (v) => `${(v / 10000).toFixed(1)}万` }, // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
  ], // 逐行注释：结束当前代码块或数据结构。
  series: [ // 逐行注释：执行本行前端逻辑。
    { // 逐行注释：执行本行前端逻辑。
      name: '挂牌套数', // 逐行注释：配置当前对象字段。
      type: 'bar', // 逐行注释：配置当前对象字段。
      barWidth: '48%', // 逐行注释：配置当前对象字段。
      data: props.data.map((d) => d.count), // 逐行注释：配置当前对象字段。
      itemStyle: { borderRadius: [6, 6, 0, 0] }, // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
    { // 逐行注释：执行本行前端逻辑。
      name: '挂牌均价', // 逐行注释：配置当前对象字段。
      type: 'line', // 逐行注释：配置当前对象字段。
      yAxisIndex: 1, // 逐行注释：配置当前对象字段。
      smooth: true, // 逐行注释：配置当前对象字段。
      symbol: 'circle', // 逐行注释：配置当前对象字段。
      symbolSize: 6, // 逐行注释：配置当前对象字段。
      data: props.data.map((d) => d.avg_unit_price), // 逐行注释：配置当前对象字段。
      lineStyle: { width: 3 }, // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
  ], // 逐行注释：结束当前代码块或数据结构。
})) // 逐行注释：执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
