import { createRouter, createWebHistory } from 'vue-router'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} | 智慧房源探索平台` : '智慧房源探索平台'
})

export default router
