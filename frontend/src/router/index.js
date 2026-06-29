// 文件功能：定义前端页面路由、登录权限守卫和页面标题同步逻辑。
import { createRouter, createWebHistory } from 'vue-router' // 导入本行所需的依赖。
import { useAuthStore } from '@/store/auth' // 导入本行所需的依赖。

const routes = [ // 声明并初始化当前变量。
  { // 执行本行前端逻辑。
    path: '/', // 配置当前对象字段。
    name: 'screen', // 配置当前对象字段。
    component: () => import('@/views/Screen.vue'), // 配置当前对象字段。
    meta: { title: '全国二手房数据大屏' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  { // 执行本行前端逻辑。
    path: '/dashboard', // 配置当前对象字段。
    name: 'dashboard', // 配置当前对象字段。
    component: () => import('@/views/Dashboard.vue'), // 配置当前对象字段。
    meta: { title: '房源总览 · 3D 房价地图' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  { // 执行本行前端逻辑。
    path: '/explore', // 配置当前对象字段。
    name: 'explore', // 配置当前对象字段。
    component: () => import('@/views/Explore.vue'), // 配置当前对象字段。
    meta: { title: '房源探索' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  { // 执行本行前端逻辑。
    path: '/property/:id', // 配置当前对象字段。
    name: 'property-detail', // 配置当前对象字段。
    component: () => import('@/views/PropertyDetail.vue'), // 配置当前对象字段。
    meta: { title: '房源详情' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  { // 执行本行前端逻辑。
    path: '/analysis', // 配置当前对象字段。
    name: 'analysis', // 配置当前对象字段。
    component: () => import('@/views/Analysis.vue'), // 配置当前对象字段。
    meta: { title: '数据分析与预测' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  { // 执行本行前端逻辑。
    path: '/login', // 配置当前对象字段。
    name: 'login', // 配置当前对象字段。
    component: () => import('@/views/Login.vue'), // 配置当前对象字段。
    meta: { title: '登录' }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
  { // 执行本行前端逻辑。
    path: '/admin', // 配置当前对象字段。
    name: 'admin', // 配置当前对象字段。
    component: () => import('@/views/Admin.vue'), // 配置当前对象字段。
    meta: { title: '管理后台', requiresAdmin: true }, // 配置当前对象字段。
  }, // 结束当前代码块或数据结构。
] // 结束当前代码块或数据结构。

const router = createRouter({ // 声明并初始化当前变量。
  history: createWebHistory(), // 配置当前对象字段。
  routes, // 继续声明当前列表项或参数项。
  scrollBehavior: () => ({ top: 0 }), // 配置当前对象字段。
}) // 执行本行前端逻辑。

router.beforeEach(async (to, from, next) => { // 执行路由跳转或路由操作。
  const auth = useAuthStore() // 声明并初始化当前变量。

  // 首次导航时尝试从 token 恢复用户信息
  if (auth.isLoggedIn && !auth.user) { // 根据条件判断是否执行分支。
    await auth.fetchUser() // 等待异步操作完成。
  } // 结束当前代码块或数据结构。

  // 1. 已登录用户访问登录页 → 跳到对应首页
  if (to.name === 'login' && auth.isLoggedIn) { // 根据条件判断是否执行分支。
    next(auth.isAdmin ? '/admin' : '/') // 执行本行前端逻辑。
    return // 返回当前表达式结果。
  } // 结束当前代码块或数据结构。

  // 2. 管理员页面需要 admin 角色
  if (to.meta.requiresAdmin && !auth.isAdmin) { // 根据条件判断是否执行分支。
    next('/login') // 执行本行前端逻辑。
    return // 返回当前表达式结果。
  } // 结束当前代码块或数据结构。

  // 3. 未登录用户只能访问登录页
  if (!auth.isLoggedIn && to.name !== 'login') { // 根据条件判断是否执行分支。
    next('/login') // 执行本行前端逻辑。
    return // 返回当前表达式结果。
  } // 结束当前代码块或数据结构。

  next() // 执行本行前端逻辑。
}) // 执行本行前端逻辑。

router.afterEach((to) => { // 执行路由跳转或路由操作。
  document.title = to.meta.title ? `${to.meta.title} | 智慧房源探索平台` : '智慧房源探索平台' // 赋值或更新当前变量/状态。
}) // 执行本行前端逻辑。

export default router // 导出当前变量、函数或配置。
