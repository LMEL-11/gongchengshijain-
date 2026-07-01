// 文件功能：创建 Vue 应用实例并挂载路由、状态管理、Element Plus 和全局样式。
import { createApp } from 'vue' // 导入 { createApp }，供当前前端模块渲染或交互逻辑使用。
import { createPinia } from 'pinia' // 导入 { createPinia }，供当前前端模块渲染或交互逻辑使用。
import ElementPlus from 'element-plus' // 导入 ElementPlus，供当前前端模块渲染或交互逻辑使用。
import 'element-plus/dist/index.css' // 导入 'element-plus/dist/index.css'，供当前前端模块渲染或交互逻辑使用。
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 导入 * as ElementPlusIconsVue，供当前前端模块渲染或交互逻辑使用。

import App from './App.vue' // 导入 App，供当前前端模块渲染或交互逻辑使用。
import router from './router' // 导入 router，供当前前端模块渲染或交互逻辑使用。
import './styles/main.css' // 导入 './styles/main.css'，供当前前端模块渲染或交互逻辑使用。

const app = createApp(App) // 创建 app，用于保存页面状态、计算结果或接口参数。

app.use(createPinia()) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
app.use(router) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
app.use(ElementPlus) // 执行当前前端代码行，推动页面数据和交互流程继续运行。

// Register all Element Plus icons globally (used in nav, cards, forms).
for (const [name, component] of Object.entries(ElementPlusIconsVue)) { // 遍历当前数据集合，逐项生成页面需要的数据。
  app.component(name, component) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

app.mount('#app') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
