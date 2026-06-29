// 文件功能：定义前端页面路由、登录权限守卫和页面标题同步逻辑。
import { createRouter, createWebHistory } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAuthStore } from '@/store/auth' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const routes = [ // 保存routes相关业务数据，作为后续计算、渲染或请求的输入。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'screen', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/Screen.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '全国二手房数据大屏' }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/dashboard', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'dashboard', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/Dashboard.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '房源总览 · 3D 房价地图' }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/explore', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'explore', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/Explore.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '房源探索' }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/property/:id', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'property-detail', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/PropertyDetail.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '房源详情' }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/analysis', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'analysis', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/Analysis.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '数据分析与预测' }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/login', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'login', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/Login.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '登录' }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    path: '/admin', // 声明path字段，作为组件配置、请求参数或图表数据的一部分。
    name: 'admin', // 声明name字段，作为组件配置、请求参数或图表数据的一部分。
    component: () => import('@/views/Admin.vue'), // 声明component字段，作为组件配置、请求参数或图表数据的一部分。
    meta: { title: '管理后台', requiresAdmin: true }, // 声明meta字段，作为组件配置、请求参数或图表数据的一部分。
  }, // 完成当前参数、配置或响应式数据结构的组装。
] // 完成当前参数、配置或响应式数据结构的组装。

const router = createRouter({ // 保存router相关业务数据，作为后续计算、渲染或请求的输入。
  history: createWebHistory(), // 声明history字段，作为组件配置、请求参数或图表数据的一部分。
  routes, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  scrollBehavior: () => ({ top: 0 }), // 声明scrollBehavior字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

router.beforeEach(async (to, from, next) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
  const auth = useAuthStore() // 保存auth相关业务数据，作为后续计算、渲染或请求的输入。

  // 首次导航时尝试从 token 恢复用户信息
  if (auth.isLoggedIn && !auth.user) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    await auth.fetchUser() // 等待异步接口或资源加载完成，再继续更新页面状态。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 1. 已登录用户访问登录页 → 跳到对应首页
  if (to.name === 'login' && auth.isLoggedIn) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    next(auth.isAdmin ? '/admin' : '/') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 2. 管理员页面需要 admin 角色
  if (to.meta.requiresAdmin && !auth.isAdmin) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    next('/login') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  // 3. 未登录用户只能访问登录页
  if (!auth.isLoggedIn && to.name !== 'login') { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    next('/login') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。

  next() // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
}) // 完成当前参数、配置或响应式数据结构的组装。

router.afterEach((to) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
  document.title = to.meta.title ? `${to.meta.title} | 智慧房源探索平台` : '智慧房源探索平台' // 更新document.title对应的页面状态，使界面展示与最新业务数据一致。
}) // 完成当前参数、配置或响应式数据结构的组装。

export default router // 导出当前配置或接口方法，供应用其他模块复用。
