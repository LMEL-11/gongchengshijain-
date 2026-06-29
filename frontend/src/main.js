// 文件功能：创建 Vue 应用实例并挂载路由、状态管理、Element Plus 和全局样式。
import { createApp } from 'vue' // 导入本行所需的依赖。
import { createPinia } from 'pinia' // 导入本行所需的依赖。
import ElementPlus from 'element-plus' // 导入本行所需的依赖。
import 'element-plus/dist/index.css' // 导入本行所需的依赖。
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 导入本行所需的依赖。

import App from './App.vue' // 导入本行所需的依赖。
import router from './router' // 导入本行所需的依赖。
import './styles/main.css' // 导入本行所需的依赖。

const app = createApp(App) // 声明并初始化当前变量。

app.use(createPinia()) // 执行本行前端逻辑。
app.use(router) // 执行本行前端逻辑。
app.use(ElementPlus) // 执行本行前端逻辑。

// Register all Element Plus icons globally (used in nav, cards, forms).
for (const [name, component] of Object.entries(ElementPlusIconsVue)) { // 遍历集合或范围并逐项处理。
  app.component(name, component) // 执行本行前端逻辑。
} // 结束当前代码块或数据结构。

app.mount('#app') // 执行本行前端逻辑。
