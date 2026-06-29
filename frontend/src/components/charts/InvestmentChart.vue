<!-- 文件功能：根据投资潜力排行数据生成雷达和柱状分析图配置。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。

import BaseChart from './BaseChart.vue' // 导入本行所需的依赖。

const props = defineProps({ // 声明并初始化当前变量。
  data: { type: Array, default: () => [] }, // 配置当前对象字段。
  height: { type: String, default: '400px' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 声明并初始化当前变量。
  const scores = props.data.map((d) => d.score) // 声明并初始化当前变量。
  const min = scores.length ? Math.min(...scores) : 0 // 声明并初始化当前变量。
  const max = scores.length ? Math.max(...scores) : 100 // 声明并初始化当前变量。
  return { // 返回当前表达式结果。
    grid: { left: 12, right: 70, top: 30, bottom: 40, containLabel: true }, // 配置当前对象字段。
    tooltip: { // 配置当前对象字段。
      trigger: 'item', // 配置当前对象字段。
      formatter: (p) => { // 配置当前对象字段。
        const [ // 声明并初始化当前变量。
          price, // 继续声明当前列表项或参数项。
          heat, // 继续声明当前列表项或参数项。
          count, // 继续声明当前列表项或参数项。
          name, // 继续声明当前列表项或参数项。
          score, // 继续声明当前列表项或参数项。
          valueScore, // 继续声明当前列表项或参数项。
          facilityScore, // 继续声明当前列表项或参数项。
          safetyScore, // 继续声明当前列表项或参数项。
          freshnessScore, // 继续声明当前列表项或参数项。
          categoryCount, // 继续声明当前列表项或参数项。
        ] = p.value // 赋值或更新当前变量/状态。
        return `<b>${name}</b><br/>投资评分：<b>${score}</b><br/>均价：${price.toLocaleString()} 元/㎡<br/>热度/配套指数：${heat}<br/>房源样本：${count} 套<br/>价格洼地：${valueScore}<br/>配套评分：${facilityScore}<br/>交易安全：${safetyScore}<br/>挂牌新鲜度：${freshnessScore}<br/>配套类别：${categoryCount} 类` // 返回当前表达式结果。
      }, // 结束当前代码块或数据结构。
    }, // 结束当前代码块或数据结构。
    xAxis: { // 配置当前对象字段。
      type: 'value', // 配置当前对象字段。
      name: '均价(元/㎡)', // 配置当前对象字段。
      scale: true, // 配置当前对象字段。
      axisLabel: { formatter: (v) => v / 10000 + '万' }, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
    yAxis: { type: 'value', name: '热度/配套', min: 0, max: 100 }, // 配置当前对象字段。
    visualMap: { // 配置当前对象字段。
      min, // 继续声明当前列表项或参数项。
      max, // 继续声明当前列表项或参数项。
      dimension: 4, // 第 5 个分量：投资评分
      calculable: true, // 配置当前对象字段。
      text: ['评分高', '评分低'], // 配置当前对象字段。
      right: 0, // 配置当前对象字段。
      top: 'center', // 配置当前对象字段。
      itemHeight: 140, // 配置当前对象字段。
      inRange: { color: ['#cbd5e1', '#60a5fa', '#1d4ed8'] }, // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
    series: [ // 执行本行前端逻辑。
      { // 执行本行前端逻辑。
        type: 'scatter', // 配置当前对象字段。
        symbolSize: (val) => 12 + Math.min(Math.sqrt(Math.max(val[2], 1)) * 2.2, 52), // 配置当前对象字段。
        data: props.data.map((d) => [ // 执行本行前端逻辑。
          d.avg_unit_price, // 继续声明当前列表项或参数项。
          d.heat_index, // 继续声明当前列表项或参数项。
          d.property_count, // 继续声明当前列表项或参数项。
          d.name, // 继续声明当前列表项或参数项。
          d.score, // 继续声明当前列表项或参数项。
          d.value_score, // 继续声明当前列表项或参数项。
          d.facility_score, // 继续声明当前列表项或参数项。
          d.safety_score, // 继续声明当前列表项或参数项。
          d.freshness_score, // 继续声明当前列表项或参数项。
          d.facility_category_count, // 继续声明当前列表项或参数项。
        ]), // 继续声明当前列表项或参数项。
        label: { // 配置当前对象字段。
          show: true, // 配置当前对象字段。
          position: 'top', // 配置当前对象字段。
          formatter: (p) => p.value[3], // 配置当前对象字段。
          fontSize: 11, // 配置当前对象字段。
          color: '#475569', // 配置当前对象字段。
        }, // 结束当前代码块或数据结构。
        itemStyle: { opacity: 0.85, borderColor: '#fff', borderWidth: 1 }, // 配置当前对象字段。
        emphasis: { focus: 'self', scale: 1.2 }, // 配置当前对象字段。
      }, // 结束当前代码块或数据结构。
    ], // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
