// 文件功能：创建 Vue 应用实例并挂载路由、状态管理、Element Plus 和全局样式。
import { createApp } from 'vue' // 逐行注释：导入本行所需的依赖。
import { createPinia } from 'pinia' // 逐行注释：导入本行所需的依赖。
import ElementPlus from 'element-plus' // 逐行注释：导入本行所需的依赖。
import 'element-plus/dist/index.css' // 逐行注释：导入本行所需的依赖。
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 逐行注释：导入本行所需的依赖。

import App from './App.vue' // 逐行注释：导入本行所需的依赖。
import router from './router' // 逐行注释：导入本行所需的依赖。
import './styles/main.css' // 逐行注释：导入本行所需的依赖。

const app = createApp(App) // 逐行注释：声明并初始化当前变量。

app.use(createPinia()) // 逐行注释：执行本行前端逻辑。
app.use(router) // 逐行注释：执行本行前端逻辑。
app.use(ElementPlus) // 逐行注释：执行本行前端逻辑。

// Register all Element Plus icons globally (used in nav, cards, forms).
for (const [name, component] of Object.entries(ElementPlusIconsVue)) { // 逐行注释：遍历集合或范围并逐项处理。
  app.component(name, component) // 逐行注释：执行本行前端逻辑。
} // 逐行注释：结束当前代码块或数据结构。

app.mount('#app') // 逐行注释：执行本行前端逻辑。
