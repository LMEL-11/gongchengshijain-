// 文件功能：提供大屏自动缩放组合式函数，使固定设计稿适配不同窗口。
import { onBeforeUnmount, onMounted, ref } from 'vue'

// 大屏等比缩放：将固定设计尺寸（默认 1920×1080）的舞台缩放至当前视口。
// 函数功能：创建自动缩放逻辑并返回设计稿容器引用。
export function useAutoFit(designW = 1920, designH = 1080) {
  const scale = ref(1)
  // 函数功能：根据容器或窗口变化刷新组件尺寸。
  function resize() {
    scale.value = Math.min(window.innerWidth / designW, window.innerHeight / designH)
  }
  onMounted(() => {
    resize()
    window.addEventListener('resize', resize)
  })
  onBeforeUnmount(() => window.removeEventListener('resize', resize))
  return { scale, designW, designH }
}
