<!-- 文件功能：根据投资潜力排行数据生成雷达和柱状分析图配置。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from './BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  data: { type: Array, default: () => [] }, // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '400px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => { // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  const scores = props.data.map((d) => d.score) // 保存scores相关业务数据，作为后续计算、渲染或请求的输入。
  const min = scores.length ? Math.min(...scores) : 0 // 保存min相关业务数据，作为后续计算、渲染或请求的输入。
  const max = scores.length ? Math.max(...scores) : 100 // 保存max相关业务数据，作为后续计算、渲染或请求的输入。
  return { // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    grid: { left: 12, right: 70, top: 30, bottom: 40, containLabel: true }, // 声明grid字段，作为组件配置、请求参数或图表数据的一部分。
    tooltip: { // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
      trigger: 'item', // 声明trigger字段，作为组件配置、请求参数或图表数据的一部分。
      formatter: (p) => { // 声明formatter字段，作为组件配置、请求参数或图表数据的一部分。
        const [ // 保存[相关业务数据，作为后续计算、渲染或请求的输入。
          price, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          heat, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          count, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          name, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          score, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          valueScore, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          facilityScore, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          safetyScore, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          freshnessScore, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          categoryCount, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        ] = p.value // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        return `<b>${name}</b><br/>投资评分：<b>${score}</b><br/>均价：${price.toLocaleString()} 元/㎡<br/>热度/配套指数：${heat}<br/>房源样本：${count} 套<br/>价格洼地：${valueScore}<br/>配套评分：${facilityScore}<br/>交易安全：${safetyScore}<br/>挂牌新鲜度：${freshnessScore}<br/>配套类别：${categoryCount} 类` // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
      }, // 完成当前参数、配置或响应式数据结构的组装。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    xAxis: { // 声明xAxis字段，作为组件配置、请求参数或图表数据的一部分。
      type: 'value', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      name: '均价(元/㎡)', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
      scale: true, // 声明scale字段，作为组件配置、请求参数或图表数据的一部分。
      axisLabel: { formatter: (v) => v / 10000 + '万' }, // 声明axisLabel字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    yAxis: { type: 'value', name: '热度/配套', min: 0, max: 100 }, // 声明yAxis字段，作为组件配置、请求参数或图表数据的一部分。
    visualMap: { // 声明visualMap字段，作为组件配置、请求参数或图表数据的一部分。
      min, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      max, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      dimension: 4, // 第 5 个分量：投资评分
      calculable: true, // 声明calculable字段，作为组件配置、请求参数或图表数据的一部分。
      text: ['评分高', '评分低'], // 声明text字段，作为组件配置、请求参数或图表数据的一部分。
      right: 0, // 声明right字段，作为组件配置、请求参数或图表数据的一部分。
      top: 'center', // 声明top字段，作为组件配置、请求参数或图表数据的一部分。
      itemHeight: 140, // 声明itemHeight字段，作为组件配置、请求参数或图表数据的一部分。
      inRange: { color: ['#cbd5e1', '#60a5fa', '#1d4ed8'] }, // 声明inRange字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
    series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
      { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
        type: 'scatter', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
        symbolSize: (val) => 12 + Math.min(Math.sqrt(Math.max(val[2], 1)) * 2.2, 52), // 声明symbolSize字段，作为组件配置、请求参数或图表数据的一部分。
        data: props.data.map((d) => [ // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
          d.avg_unit_price, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.heat_index, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.property_count, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.name, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.score, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.value_score, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.facility_score, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.safety_score, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.freshness_score, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
          d.facility_category_count, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        ]), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        label: { // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
          show: true, // 声明show字段，作为组件配置、请求参数或图表数据的一部分。
          position: 'top', // 声明position字段，作为组件配置、请求参数或图表数据的一部分。
          formatter: (p) => p.value[3], // 声明formatter字段，作为组件配置、请求参数或图表数据的一部分。
          fontSize: 11, // 声明fontSize字段，作为组件配置、请求参数或图表数据的一部分。
          color: '#475569', // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
        }, // 完成当前参数、配置或响应式数据结构的组装。
        itemStyle: { opacity: 0.85, borderColor: '#fff', borderWidth: 1 }, // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
        emphasis: { focus: 'self', scale: 1.2 }, // 声明emphasis字段，作为组件配置、请求参数或图表数据的一部分。
      }, // 完成当前参数、配置或响应式数据结构的组装。
    ], // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <BaseChart :option="option" :height="height" />
</template>
