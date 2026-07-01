// 文件功能：配置 Vite 开发服务器、构建行为和路径别名。
import { fileURLToPath, URL } from 'node:url' // 导入 { fileURLToPath, URL }，供当前前端模块渲染或交互逻辑使用。

import { defineConfig } from 'vite' // 导入 { defineConfig }，供当前前端模块渲染或交互逻辑使用。
import vue from '@vitejs/plugin-vue' // 导入 vue，供当前前端模块渲染或交互逻辑使用。

// https://vitejs.dev/config/
export default defineConfig({ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  plugins: [vue()], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  resolve: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    alias: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      '@': fileURLToPath(new URL('./src', import.meta.url)), // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    }, // 结束当前函数、对象、数组或组件配置块。
  }, // 结束当前函数、对象、数组或组件配置块。
  server: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    port: 5173, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // Proxy API calls to the Flask backend so we avoid CORS during dev.
    proxy: { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      '/api': { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        target: 'http://127.0.0.1:5000', // 把 /api 开头的开发请求代理到 Flask 后端。
        changeOrigin: true, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      }, // 结束当前函数、对象、数组或组件配置块。
    }, // 结束当前函数、对象、数组或组件配置块。
  }, // 结束当前函数、对象、数组或组件配置块。
}) // 结束当前函数、对象、数组或组件配置块。
