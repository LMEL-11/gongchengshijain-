// 文件功能：维护登录令牌、当前用户、登录状态和退出逻辑。
import { defineStore } from 'pinia' // 导入本行所需的依赖。
import { ref, computed } from 'vue' // 导入本行所需的依赖。
import { login as apiLogin, getMe } from '@/api' // 导入本行所需的依赖。

export const useAuthStore = defineStore('auth', () => { // 导出当前变量、函数或配置。
  const token = ref(localStorage.getItem('token') || '') // 声明并初始化当前变量。
  const user = ref(null) // 声明并初始化当前变量。

  // 函数功能：计算当前是否存在登录令牌。
  const isLoggedIn = computed(() => !!token.value) // 声明并初始化当前变量。
  // 函数功能：计算当前用户是否为管理员角色。
  const isAdmin = computed(() => user.value?.role === 'admin') // 声明并初始化当前变量。

  // 函数功能：提交账号密码并请求登录结果。
  async function login(username, password) { // 声明当前函数入口。
    const res = await apiLogin(username, password) // 声明并初始化当前变量。
    token.value = res.token // 赋值或更新当前变量/状态。
    user.value = res.user // 赋值或更新当前变量/状态。
    localStorage.setItem('token', res.token) // 执行本行前端逻辑。
    return res // 返回当前表达式结果。
  } // 结束当前代码块或数据结构。

  // 函数功能：根据本地令牌拉取当前用户，失败时清理登录状态。
  async function fetchUser() { // 声明当前函数入口。
    if (!token.value) return // 根据条件判断是否执行分支。
    try { // 开始执行可能失败的逻辑。
      user.value = await getMe() // 赋值或更新当前变量/状态。
    } catch { // 执行本行前端逻辑。
      token.value = '' // 赋值或更新当前变量/状态。
      user.value = null // 赋值或更新当前变量/状态。
      localStorage.removeItem('token') // 执行本行前端逻辑。
    } // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。

  // 函数功能：清理登录令牌和当前用户信息。
  function logout() { // 声明当前函数入口。
    token.value = '' // 赋值或更新当前变量/状态。
    user.value = null // 赋值或更新当前变量/状态。
    localStorage.removeItem('token') // 执行本行前端逻辑。
  } // 结束当前代码块或数据结构。

  return { token, user, isLoggedIn, isAdmin, login, fetchUser, logout } // 返回当前表达式结果。
}) // 执行本行前端逻辑。
