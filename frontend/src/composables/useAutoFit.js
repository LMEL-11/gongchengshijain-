// 文件功能：提供大屏自动缩放组合式函数，使固定设计稿适配不同窗口。
import { onBeforeUnmount, onMounted, ref } from 'vue' // 导入 { onBeforeUnmount, onMounted, ref }，供当前前端模块渲染或交互逻辑使用。

// 大屏等比缩放：将固定设计尺寸（默认 1920×1080）的舞台缩放至当前视口。
// 函数功能：创建自动缩放逻辑并返回设计稿容器引用。
export function useAutoFit(designW = 1920, designH = 1080) { // 设置 export function useAutoFit(designW 的值，作为后续渲染、计算或请求的输入。
  const scale = ref(1) // 创建 scale，用于保存页面状态、计算结果或接口参数。
  // 函数功能：根据容器或窗口变化刷新组件尺寸。
  function resize() { // 定义 resize 函数，处理页面交互、数据加载或状态同步。
    scale.value = Math.min(window.innerWidth / designW, window.innerHeight / designH) // 更新 scale.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
  onMounted(() => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    resize() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    window.addEventListener('resize', resize) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }) // 结束当前函数、对象、数组或组件配置块。
  onBeforeUnmount(() => window.removeEventListener('resize', resize)) // 设置 onBeforeUnmount 的值，作为后续渲染、计算或请求的输入。
  return { scale, designW, designH } // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
