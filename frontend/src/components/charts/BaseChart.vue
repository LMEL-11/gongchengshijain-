<!-- 文件功能：封装 ECharts 基础组件，统一初始化、渲染和尺寸监听。 -->
<script setup>
import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  option: { type: Object, required: true },
  height: { type: String, default: '340px' },
})

const el = ref(null)
let chart = null

// 函数功能：根据当前配置渲染或更新 ECharts 图表。
function render() {
  if (!el.value) return
  if (!chart) chart = echarts.init(el.value)
  // `true` clears the previous option so removed series don't linger.
  chart.setOption(props.option, true)
}

// 函数功能：根据容器或窗口变化刷新组件尺寸。
function resize() {
  chart?.resize()
}

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

watch(
  () => props.option,
  () => nextTick(render),
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div ref="el" :style="{ width: '100%', height }"></div>
</template>
