// 文件功能：维护登录令牌、当前用户、登录状态和退出逻辑。
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getMe } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  // 函数功能：计算当前是否存在登录令牌。
  const isLoggedIn = computed(() => !!token.value)
  // 函数功能：计算当前用户是否为管理员角色。
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 函数功能：提交账号密码并请求登录结果。
  async function login(username, password) {
    const res = await apiLogin(username, password)
    token.value = res.token
    user.value = res.user
    localStorage.setItem('token', res.token)
    return res
  }

  // 函数功能：根据本地令牌拉取当前用户，失败时清理登录状态。
  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await getMe()
    } catch {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
    }
  }

  // 函数功能：清理登录令牌和当前用户信息。
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isLoggedIn, isAdmin, login, fetchUser, logout }
})
