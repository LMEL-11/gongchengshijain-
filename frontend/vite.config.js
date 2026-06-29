// 文件功能：配置 Vite 开发服务器、构建行为和路径别名。
import { fileURLToPath, URL } from 'node:url' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

import { defineConfig } from 'vite' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import vue from '@vitejs/plugin-vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

// https://vitejs.dev/config/
export default defineConfig({ // 导出当前配置或接口方法，供应用其他模块复用。
  plugins: [vue()], // 声明plugins字段，作为组件配置、请求参数或图表数据的一部分。
  resolve: { // 声明resolve字段，作为组件配置、请求参数或图表数据的一部分。
    alias: { // 声明alias字段，作为组件配置、请求参数或图表数据的一部分。
      '@': fileURLToPath(new URL('./src', import.meta.url)), // 声明@字段，作为组件配置、请求参数或图表数据的一部分。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  server: { // 声明server字段，作为组件配置、请求参数或图表数据的一部分。
    port: 5173, // 声明port字段，作为组件配置、请求参数或图表数据的一部分。
    // Proxy API calls to the Flask backend so we avoid CORS during dev.
    proxy: { // 声明proxy字段，作为组件配置、请求参数或图表数据的一部分。
      '/api': { // 声明/api字段，作为组件配置、请求参数或图表数据的一部分。
        target: 'http://127.0.0.1:5000', // 声明target字段，作为组件配置、请求参数或图表数据的一部分。
        changeOrigin: true, // 声明changeOrigin字段，作为组件配置、请求参数或图表数据的一部分。
      }, // 完成当前参数、配置或响应式数据结构的组装。
    }, // 完成当前参数、配置或响应式数据结构的组装。
  }, // 完成当前参数、配置或响应式数据结构的组装。
}) // 完成当前参数、配置或响应式数据结构的组装。
