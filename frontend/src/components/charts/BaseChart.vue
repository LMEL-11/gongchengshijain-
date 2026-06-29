<!-- 文件功能：封装 ECharts 基础组件，统一初始化、渲染和尺寸监听。 -->
<script setup>
import * as echarts from 'echarts' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const props = defineProps({ // 保存props相关业务数据，作为后续计算、渲染或请求的输入。
  option: { type: Object, required: true }, // 声明option字段，作为组件配置、请求参数或图表数据的一部分。
  height: { type: String, default: '340px' }, // 声明height字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

const el = ref(null) // 创建el响应式状态，用于驱动页面渲染、表单输入或接口参数。
let chart = null // 保存chart相关业务数据，作为后续计算、渲染或请求的输入。

// 函数功能：根据当前配置渲染或更新 ECharts 图表。
function render() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (!el.value) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
  if (!chart) chart = echarts.init(el.value) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  // `true` clears the previous option so removed series don't linger.
  chart.setOption(props.option, true) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据容器或窗口变化刷新组件尺寸。
function resize() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  chart?.resize() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

onMounted(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  render() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  window.addEventListener('resize', resize) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
}) // 完成当前参数、配置或响应式数据结构的组装。

watch( // 监听响应式数据变化，并在变化后同步关联选项或视图状态。
  () => props.option, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  () => nextTick(render), // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { deep: true }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
) // 完成当前参数、配置或响应式数据结构的组装。

onBeforeUnmount(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  window.removeEventListener('resize', resize) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  chart?.dispose() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  chart = null // 更新chart对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <div ref="el" :style="{ width: '100%', height }"></div>
</template>
