<!-- 文件功能：渲染大屏环形占比图组件。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import BaseChart from '@/components/charts/BaseChart.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  items: { type: Array, default: () => [] }, // [{ name, value }]
}) // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据输入数据计算当前图表的 ECharts 配置。
const option = computed(() => ({ // 基于响应式数据派生option，用于保持界面展示与数据状态同步。
  color: ['#3fe0ff', '#7c8cff', '#ffd166'], // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
  tooltip: { // 声明tooltip字段，作为组件配置、请求参数或图表数据的一部分。
    trigger: 'item', // 声明trigger字段，作为组件配置、请求参数或图表数据的一部分。
    backgroundColor: 'rgba(7,25,50,0.92)', // 声明backgroundColor字段，作为组件配置、请求参数或图表数据的一部分。
    borderColor: 'rgba(63,224,255,0.4)', // 声明borderColor字段，作为组件配置、请求参数或图表数据的一部分。
    textStyle: { color: '#dbeeff' }, // 声明textStyle字段，作为组件配置、请求参数或图表数据的一部分。
    formatter: (p) => `${p.name}<br/><b>${Number(p.value).toLocaleString()}</b> 套 (${p.percent}%)`, // 声明formatter字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  legend: { // 声明legend字段，作为组件配置、请求参数或图表数据的一部分。
    bottom: 0, // 声明bottom字段，作为组件配置、请求参数或图表数据的一部分。
    icon: 'circle', // 声明icon字段，作为组件配置、请求参数或图表数据的一部分。
    itemWidth: 9, // 声明itemWidth字段，作为组件配置、请求参数或图表数据的一部分。
    itemHeight: 9, // 声明itemHeight字段，作为组件配置、请求参数或图表数据的一部分。
    textStyle: { color: '#cfe8ff', fontSize: 12 }, // 声明textStyle字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  series: [ // 声明series字段，作为组件配置、请求参数或图表数据的一部分。
    { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      type: 'pie', // 声明type字段，作为组件配置、请求参数或图表数据的一部分。
      radius: ['46%', '70%'], // 声明radius字段，作为组件配置、请求参数或图表数据的一部分。
      center: ['50%', '44%'], // 声明center字段，作为组件配置、请求参数或图表数据的一部分。
      avoidLabelOverlap: true, // 声明avoidLabelOverlap字段，作为组件配置、请求参数或图表数据的一部分。
      itemStyle: { borderColor: '#06122b', borderWidth: 2 }, // 声明itemStyle字段，作为组件配置、请求参数或图表数据的一部分。
      label: { color: '#cfe8ff', formatter: '{d}%' }, // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
      labelLine: { length: 8, length2: 8 }, // 声明labelLine字段，作为组件配置、请求参数或图表数据的一部分。
      data: props.items, // 声明data字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  ], // 完成当前参数、配置或响应式数据结构的组装。
})) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
</script>

<template>
  <BaseChart :option="option" height="100%" />
</template>
