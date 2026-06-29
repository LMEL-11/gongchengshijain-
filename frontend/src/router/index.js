// 文件功能：定义前端页面路由、登录权限守卫和页面标题同步逻辑。
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'screen',
    component: () => import('@/views/Screen.vue'),
    meta: { title: '全国二手房数据大屏' },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '房源总览 · 3D 房价地图' },
  },
  {
    path: '/explore',
    name: 'explore',
    component: () => import('@/views/Explore.vue'),
    meta: { title: '房源探索' },
  },
  {
    path: '/property/:id',
    name: 'property-detail',
    component: () => import('@/views/PropertyDetail.vue'),
    meta: { title: '房源详情' },
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: '数据分析与预测' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/Admin.vue'),
    meta: { title: '管理后台', requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // 首次导航时尝试从 token 恢复用户信息
  if (auth.isLoggedIn && !auth.user) {
    await auth.fetchUser()
  }

  // 1. 已登录用户访问登录页 → 跳到对应首页
  if (to.name === 'login' && auth.isLoggedIn) {
    next(auth.isAdmin ? '/admin' : '/')
    return
  }

  // 2. 管理员页面需要 admin 角色
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    next('/login')
    return
  }

  // 3. 未登录用户只能访问登录页
  if (!auth.isLoggedIn && to.name !== 'login') {
    next('/login')
    return
  }

  next()
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} | 智慧房源探索平台` : '智慧房源探索平台'
})

export default router
