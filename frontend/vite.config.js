// 文件功能：配置 Vite 开发服务器、构建行为和路径别名。
import { fileURLToPath, URL } from 'node:url' // 导入本行所需的依赖。

import { defineConfig } from 'vite' // 导入本行所需的依赖。
import vue from '@vitejs/plugin-vue' // 导入本行所需的依赖。

// https://vitejs.dev/config/
export default defineConfig({ // 导出当前变量、函数或配置。
  plugins: [vue()], // 配置当前对象字段。
  resolve: { // 配置当前对象字段。
    alias: { // 配置当前对象字段。
      '@': fileURLToPath(new URL('./src', import.meta.url)), // 配置当前对象字段。
    }, // 结束当前代码块或数据结构。
  }, // 结束当前代码块或数据结构。
  server: { // 配置当前对象字段。
    port: 5173, // 配置当前对象字段。
    // Proxy API calls to the Flask backend so we avoid CORS during dev.
    proxy: { // 配置当前对象字段。
      '/api': { // 配置当前对象字段。
        target: 'http://127.0.0.1:5000', // 配置当前对象字段。
        changeOrigin: true, // 配置当前对象字段。
      }, // 结束当前代码块或数据结构。
    }, // 结束当前代码块或数据结构。
  }, // 结束当前代码块或数据结构。
}) // 执行本行前端逻辑。
