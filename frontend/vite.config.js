// 文件功能：配置 Vite 开发服务器、构建行为和路径别名。
import { fileURLToPath, URL } from 'node:url' // 逐行注释：导入本行所需的依赖。

import { defineConfig } from 'vite' // 逐行注释：导入本行所需的依赖。
import vue from '@vitejs/plugin-vue' // 逐行注释：导入本行所需的依赖。

// https://vitejs.dev/config/
export default defineConfig({ // 逐行注释：导出当前变量、函数或配置。
  plugins: [vue()], // 逐行注释：配置当前对象字段。
  resolve: { // 逐行注释：配置当前对象字段。
    alias: { // 逐行注释：配置当前对象字段。
      '@': fileURLToPath(new URL('./src', import.meta.url)), // 逐行注释：配置当前对象字段。
    }, // 逐行注释：结束当前代码块或数据结构。
  }, // 逐行注释：结束当前代码块或数据结构。
  server: { // 逐行注释：配置当前对象字段。
    port: 5173, // 逐行注释：配置当前对象字段。
    // Proxy API calls to the Flask backend so we avoid CORS during dev.
    proxy: { // 逐行注释：配置当前对象字段。
      '/api': { // 逐行注释：配置当前对象字段。
        target: 'http://127.0.0.1:5000', // 逐行注释：配置当前对象字段。
        changeOrigin: true, // 逐行注释：配置当前对象字段。
      }, // 逐行注释：结束当前代码块或数据结构。
    }, // 逐行注释：结束当前代码块或数据结构。
  }, // 逐行注释：结束当前代码块或数据结构。
}) // 逐行注释：执行本行前端逻辑。
