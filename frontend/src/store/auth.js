// 文件功能：维护登录令牌、当前用户、登录状态和退出逻辑。
import { defineStore } from 'pinia' // 逐行注释：导入本行所需的依赖。
import { ref, computed } from 'vue' // 逐行注释：导入本行所需的依赖。
import { login as apiLogin, getMe } from '@/api' // 逐行注释：导入本行所需的依赖。

export const useAuthStore = defineStore('auth', () => { // 逐行注释：导出当前变量、函数或配置。
  const token = ref(localStorage.getItem('token') || '') // 逐行注释：声明并初始化当前变量。
  const user = ref(null) // 逐行注释：声明并初始化当前变量。

  // 函数功能：计算当前是否存在登录令牌。
  const isLoggedIn = computed(() => !!token.value) // 逐行注释：声明并初始化当前变量。
  // 函数功能：计算当前用户是否为管理员角色。
  const isAdmin = computed(() => user.value?.role === 'admin') // 逐行注释：声明并初始化当前变量。

  // 函数功能：提交账号密码并请求登录结果。
  async function login(username, password) { // 逐行注释：声明当前函数入口。
    const res = await apiLogin(username, password) // 逐行注释：声明并初始化当前变量。
    token.value = res.token // 逐行注释：赋值或更新当前变量/状态。
    user.value = res.user // 逐行注释：赋值或更新当前变量/状态。
    localStorage.setItem('token', res.token) // 逐行注释：执行本行前端逻辑。
    return res // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。

  // 函数功能：根据本地令牌拉取当前用户，失败时清理登录状态。
  async function fetchUser() { // 逐行注释：声明当前函数入口。
    if (!token.value) return // 逐行注释：根据条件判断是否执行分支。
    try { // 逐行注释：开始执行可能失败的逻辑。
      user.value = await getMe() // 逐行注释：赋值或更新当前变量/状态。
    } catch { // 逐行注释：执行本行前端逻辑。
      token.value = '' // 逐行注释：赋值或更新当前变量/状态。
      user.value = null // 逐行注释：赋值或更新当前变量/状态。
      localStorage.removeItem('token') // 逐行注释：执行本行前端逻辑。
    } // 逐行注释：结束当前代码块或数据结构。
  } // 逐行注释：结束当前代码块或数据结构。

  // 函数功能：清理登录令牌和当前用户信息。
  function logout() { // 逐行注释：声明当前函数入口。
    token.value = '' // 逐行注释：赋值或更新当前变量/状态。
    user.value = null // 逐行注释：赋值或更新当前变量/状态。
    localStorage.removeItem('token') // 逐行注释：执行本行前端逻辑。
  } // 逐行注释：结束当前代码块或数据结构。

  return { token, user, isLoggedIn, isAdmin, login, fetchUser, logout } // 逐行注释：返回当前表达式结果。
}) // 逐行注释：执行本行前端逻辑。
