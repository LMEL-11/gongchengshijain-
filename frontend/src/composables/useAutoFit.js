import { onBeforeUnmount, onMounted, ref } from 'vue'

// 大屏等比缩放：将固定设计尺寸（默认 1920×1080）的舞台缩放至当前视口。
export function useAutoFit(designW = 1920, designH = 1080) {
  const scale = ref(1)
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
