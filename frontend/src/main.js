// 文件功能：创建 Vue 应用实例并挂载路由、状态管理、Element Plus 和全局样式。
import { createApp } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { createPinia } from 'pinia' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import ElementPlus from 'element-plus' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import 'element-plus/dist/index.css' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import App from './App.vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import router from './router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import './styles/main.css' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const app = createApp(App) // 保存app相关业务数据，作为后续计算、渲染或请求的输入。

app.use(createPinia()) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
app.use(router) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
app.use(ElementPlus) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

// Register all Element Plus icons globally (used in nav, cards, forms).
for (const [name, component] of Object.entries(ElementPlusIconsVue)) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
  app.component(name, component) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

app.mount('#app') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
