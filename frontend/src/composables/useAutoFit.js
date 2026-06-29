// 文件功能：提供大屏自动缩放组合式函数，使固定设计稿适配不同窗口。
import { onBeforeUnmount, onMounted, ref } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

// 大屏等比缩放：将固定设计尺寸（默认 1920×1080）的舞台缩放至当前视口。
// 函数功能：创建自动缩放逻辑并返回设计稿容器引用。
export function useAutoFit(designW = 1920, designH = 1080) { // 导出当前配置或接口方法，供应用其他模块复用。
  const scale = ref(1) // 创建scale响应式状态，用于驱动页面渲染、表单输入或接口参数。
  // 函数功能：根据容器或窗口变化刷新组件尺寸。
  function resize() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    scale.value = Math.min(window.innerWidth / designW, window.innerHeight / designH) // 更新scale.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
  onMounted(() => { // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
    resize() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    window.addEventListener('resize', resize) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  }) // 完成当前参数、配置或响应式数据结构的组装。
  onBeforeUnmount(() => window.removeEventListener('resize', resize)) // 注册组件生命周期逻辑，负责初始化数据或释放页面资源。
  return { scale, designW, designH } // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
