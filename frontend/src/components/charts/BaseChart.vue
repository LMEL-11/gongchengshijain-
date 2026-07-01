<!-- 文件功能：封装 ECharts 基础组件，统一初始化、渲染和尺寸监听。 -->
<script setup>
import * as echarts from 'echarts' // 导入 * as echarts，供当前前端模块渲染或交互逻辑使用。
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue' // 导入 { nextTick, onBeforeUnmount, onMounted, ref, watch }，供当前前端模块渲染或交互逻辑使用。

const props = defineProps({ // 创建 props，用于保存页面状态、计算结果或接口参数。
  option: { type: Object, required: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  height: { type: String, default: '340px' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

const el = ref(null) // 创建 el，用于保存页面状态、计算结果或接口参数。
let chart = null // 创建 chart，用于保存页面状态、计算结果或接口参数。

// 函数功能：根据当前配置渲染或更新 ECharts 图表。
function render() { // 定义 render 函数，处理页面交互、数据加载或状态同步。
  if (!el.value) return // 根据当前页面状态或接口结果决定是否进入该分支。
  if (!chart) chart = echarts.init(el.value) // 根据当前页面状态或接口结果决定是否进入该分支。
  // `true` clears the previous option so removed series don't linger.
  chart.setOption(props.option, true) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据容器或窗口变化刷新组件尺寸。
function resize() { // 定义 resize 函数，处理页面交互、数据加载或状态同步。
  chart?.resize() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

onMounted(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  render() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  window.addEventListener('resize', resize) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

watch( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  () => props.option, // 设置  的值，作为后续渲染、计算或请求的输入。
  () => nextTick(render), // 设置  的值，作为后续渲染、计算或请求的输入。
  { deep: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
) // 结束当前函数、对象、数组或组件配置块。

onBeforeUnmount(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  window.removeEventListener('resize', resize) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  chart?.dispose() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  chart = null // 设置 chart 的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。
</script>

<template>
  <div ref="el" :style="{ width: '100%', height }"></div>
</template>
