// 文件功能：定义前端页面路由、登录权限守卫和页面标题同步逻辑。
import { createRouter, createWebHistory } from 'vue-router' // 导入 { createRouter, createWebHistory }，供当前前端模块渲染或交互逻辑使用。
import { useAuthStore } from '@/store/auth' // 导入 { useAuthStore }，供当前前端模块渲染或交互逻辑使用。

const routes = [ // 创建 routes，用于保存页面状态、计算结果或接口参数。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'screen', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/Screen.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '全国二手房数据大屏' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/dashboard', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'dashboard', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/Dashboard.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '房源总览 · 3D 房价地图' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/explore', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'explore', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/Explore.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '房源探索' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/property/:id', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'property-detail', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/PropertyDetail.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '房源详情' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/analysis', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'analysis', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/Analysis.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '数据分析与预测' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/login', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'login', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/Login.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '登录' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
  { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    path: '/admin', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    name: 'admin', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    component: () => import('@/views/Admin.vue'), // 设置 component:  的值，作为后续渲染、计算或请求的输入。
    meta: { title: '管理后台', requiresAdmin: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  }, // 结束当前函数、对象、数组或组件配置块。
] // 结束当前函数、对象、数组或组件配置块。

const router = createRouter({ // 创建 router，用于保存页面状态、计算结果或接口参数。
  history: createWebHistory(), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  routes, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  scrollBehavior: () => ({ top: 0 }), // 设置 scrollBehavior:  的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。

router.beforeEach(async (to, from, next) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  const auth = useAuthStore() // 创建 auth，用于保存页面状态、计算结果或接口参数。

  // 首次导航时尝试从 token 恢复用户信息
  if (auth.isLoggedIn && !auth.user) { // 根据当前页面状态或接口结果决定是否进入该分支。
    await auth.fetchUser() // 等待异步接口或资源加载完成，再继续更新页面状态。
  } // 结束当前函数、对象、数组或组件配置块。

  // 1. 已登录用户访问登录页 → 跳到对应首页
  if (to.name === 'login' && auth.isLoggedIn) { // 根据当前页面状态或接口结果决定是否进入该分支。
    next(auth.isAdmin ? '/admin' : '/') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  // 2. 管理员页面需要 admin 角色
  if (to.meta.requiresAdmin && !auth.isAdmin) { // 根据当前页面状态或接口结果决定是否进入该分支。
    next('/login') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  // 3. 未登录用户只能访问登录页
  if (!auth.isLoggedIn && to.name !== 'login') { // 根据当前页面状态或接口结果决定是否进入该分支。
    next('/login') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。

  next() // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

router.afterEach((to) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  document.title = to.meta.title ? `${to.meta.title} | 智慧房源探索平台` : '智慧房源探索平台' // 设置 document.title 的值，作为后续渲染、计算或请求的输入。
}) // 结束当前函数、对象、数组或组件配置块。

export default router // 执行当前前端代码行，推动页面数据和交互流程继续运行。
