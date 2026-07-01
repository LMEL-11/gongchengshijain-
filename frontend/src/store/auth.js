// 文件功能：维护登录令牌、当前用户、登录状态和退出逻辑。
import { defineStore } from 'pinia' // 导入 { defineStore }，供当前前端模块渲染或交互逻辑使用。
import { ref, computed } from 'vue' // 导入 { ref, computed }，供当前前端模块渲染或交互逻辑使用。
import { login as apiLogin, getMe } from '@/api' // 导入 { login as apiLogin, getMe }，供当前前端模块渲染或交互逻辑使用。

export const useAuthStore = defineStore('auth', () => { // 导出 useAuthStore 方法或状态，供其他页面和组件调用。
  const token = ref(localStorage.getItem('token') || '') // 创建 token，用于保存页面状态、计算结果或接口参数。
  const user = ref(null) // 创建 user，用于保存页面状态、计算结果或接口参数。

  // 函数功能：计算当前是否存在登录令牌。
  const isLoggedIn = computed(() => !!token.value) // 创建 isLoggedIn，用于保存页面状态、计算结果或接口参数。
  // 函数功能：计算当前用户是否为管理员角色。
  const isAdmin = computed(() => user.value?.role === 'admin') // 创建 isAdmin，用于保存页面状态、计算结果或接口参数。

  // 函数功能：提交账号密码并请求登录结果。
  async function login(username, password) { // 定义 login 函数，处理页面交互、数据加载或状态同步。
    const res = await apiLogin(username, password) // 创建 res，用于保存页面状态、计算结果或接口参数。
    token.value = res.token // 更新 token.value 响应式状态，让页面展示与最新数据保持一致。
    user.value = res.user // 更新 user.value 响应式状态，让页面展示与最新数据保持一致。
    localStorage.setItem('token', res.token) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return res // 返回整理后的数据、组件配置或渲染结果。
  } // 结束当前函数、对象、数组或组件配置块。

  // 函数功能：根据本地令牌拉取当前用户，失败时清理登录状态。
  async function fetchUser() { // 定义 fetchUser 函数，处理页面交互、数据加载或状态同步。
    if (!token.value) return // 根据当前页面状态或接口结果决定是否进入该分支。
    try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      user.value = await getMe() // 更新 user.value 响应式状态，让页面展示与最新数据保持一致。
    } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      token.value = '' // 更新 token.value 响应式状态，让页面展示与最新数据保持一致。
      user.value = null // 更新 user.value 响应式状态，让页面展示与最新数据保持一致。
      localStorage.removeItem('token') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。

  // 函数功能：清理登录令牌和当前用户信息。
  function logout() { // 定义 logout 函数，处理页面交互、数据加载或状态同步。
    token.value = '' // 更新 token.value 响应式状态，让页面展示与最新数据保持一致。
    user.value = null // 更新 user.value 响应式状态，让页面展示与最新数据保持一致。
    localStorage.removeItem('token') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  return { token, user, isLoggedIn, isAdmin, login, fetchUser, logout } // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。
