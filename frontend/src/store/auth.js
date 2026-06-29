// 文件功能：维护登录令牌、当前用户、登录状态和退出逻辑。
import { defineStore } from 'pinia' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { ref, computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { login as apiLogin, getMe } from '@/api' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

export const useAuthStore = defineStore('auth', () => { // 导出当前配置或接口方法，供应用其他模块复用。
  const token = ref(localStorage.getItem('token') || '') // 创建token响应式状态，用于驱动页面渲染、表单输入或接口参数。
  const user = ref(null) // 创建user响应式状态，用于驱动页面渲染、表单输入或接口参数。

  // 函数功能：计算当前是否存在登录令牌。
  const isLoggedIn = computed(() => !!token.value) // 基于响应式数据派生isLoggedIn，用于保持界面展示与数据状态同步。
  // 函数功能：计算当前用户是否为管理员角色。
  const isAdmin = computed(() => user.value?.role === 'admin') // 基于响应式数据派生isAdmin，用于保持界面展示与数据状态同步。

  // 函数功能：提交账号密码并请求登录结果。
  async function login(username, password) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    const res = await apiLogin(username, password) // 保存res相关业务数据，作为后续计算、渲染或请求的输入。
    token.value = res.token // 更新token.value对应的页面状态，使界面展示与最新业务数据一致。
    user.value = res.user // 更新user.value对应的页面状态，使界面展示与最新业务数据一致。
    localStorage.setItem('token', res.token) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return res // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 函数功能：根据本地令牌拉取当前用户，失败时清理登录状态。
  async function fetchUser() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    if (!token.value) return // 根据当前状态、接口结果或用户输入选择对应交互路径。
    try { // 开始执行可能失败的接口请求或异步页面更新。
      user.value = await getMe() // 等待异步接口或资源加载完成，再继续更新页面状态。
    } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      token.value = '' // 更新token.value对应的页面状态，使界面展示与最新业务数据一致。
      user.value = null // 更新user.value对应的页面状态，使界面展示与最新业务数据一致。
      localStorage.removeItem('token') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 函数功能：清理登录令牌和当前用户信息。
  function logout() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    token.value = '' // 更新token.value对应的页面状态，使界面展示与最新业务数据一致。
    user.value = null // 更新user.value对应的页面状态，使界面展示与最新业务数据一致。
    localStorage.removeItem('token') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  return { token, user, isLoggedIn, isAdmin, login, fetchUser, logout } // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。
