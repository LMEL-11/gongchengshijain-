<!-- 文件功能：封装 ECharts 基础组件，统一初始化、渲染和尺寸监听。 -->
<script setup>
import * as echarts from 'echarts' // 逐行注释：导入本行所需的依赖。
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue' // 逐行注释：导入本行所需的依赖。

const props = defineProps({ // 逐行注释：声明并初始化当前变量。
  option: { type: Object, required: true }, // 逐行注释：配置当前对象字段。
  height: { type: String, default: '340px' }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。

const el = ref(null) // 逐行注释：声明并初始化当前变量。
let chart = null // 逐行注释：声明并初始化当前变量。

// 函数功能：根据当前配置渲染或更新 ECharts 图表。
function render() { // 逐行注释：声明当前函数入口。
  if (!el.value) return // 逐行注释：根据条件判断是否执行分支。
  if (!chart) chart = echarts.init(el.value) // 逐行注释：根据条件判断是否执行分支。
  // `true` clears the previous option so removed series don't linger.
  chart.setOption(props.option, true) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：根据容器或窗口变化刷新组件尺寸。
function resize() { // 逐行注释：声明当前函数入口。
  chart?.resize() // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

onMounted(() => { // 逐行注释：注册 Vue 生命周期回调。
  render() // 逐行注释：执行本行前端逻辑。
  window.addEventListener('resize', resize) // 逐行注释：执行本行前端逻辑。
}) // 逐行注释：执行本行前端逻辑。

watch( // 逐行注释：监听响应式数据变化。
  () => props.option, // 逐行注释：继续声明当前列表项或参数项。
  () => nextTick(render), // 逐行注释：继续声明当前列表项或参数项。
  { deep: true }, // 逐行注释：配置当前对象字段。
) // 逐行注释：结束当前代码块或数据结构。

onBeforeUnmount(() => { // 逐行注释：注册 Vue 生命周期回调。
  window.removeEventListener('resize', resize) // 逐行注释：执行本行前端逻辑。
  chart?.dispose() // 逐行注释：执行本行前端逻辑。
  chart = null // 逐行注释：赋值或更新当前变量/状态。
}) // 逐行注释：执行本行前端逻辑。
</script>

<template>
  <div ref="el" :style="{ width: '100%', height }"></div>
</template>
