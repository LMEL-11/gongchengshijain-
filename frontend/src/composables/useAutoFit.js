// 文件功能：提供大屏自动缩放组合式函数，使固定设计稿适配不同窗口。
import { onBeforeUnmount, onMounted, ref } from 'vue' // 导入本行所需的依赖。

// 大屏等比缩放：将固定设计尺寸（默认 1920×1080）的舞台缩放至当前视口。
// 函数功能：创建自动缩放逻辑并返回设计稿容器引用。
export function useAutoFit(designW = 1920, designH = 1080) { // 导出当前变量、函数或配置。
  const scale = ref(1) // 声明并初始化当前变量。
  // 函数功能：根据容器或窗口变化刷新组件尺寸。
  function resize() { // 声明当前函数入口。
    scale.value = Math.min(window.innerWidth / designW, window.innerHeight / designH) // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
  onMounted(() => { // 注册 Vue 生命周期回调。
    resize() // 执行本行前端逻辑。
    window.addEventListener('resize', resize) // 执行本行前端逻辑。
  }) // 执行本行前端逻辑。
  onBeforeUnmount(() => window.removeEventListener('resize', resize)) // 注册 Vue 生命周期回调。
  return { scale, designW, designH } // 返回当前表达式结果。
} // 结束当前代码块或数据结构。
