// 文件功能：配置 Axios 请求实例、登录令牌注入、统一响应解包和错误提示。
import axios from 'axios' // 导入本行所需的依赖。
import { ElMessage } from 'element-plus' // 导入本行所需的依赖。

const request = axios.create({ // 声明并初始化当前变量。
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 配置当前对象字段。
  timeout: 15000, // 配置当前对象字段。
}) // 执行本行前端逻辑。

// Attach JWT token from localStorage on every request.
request.interceptors.request.use((config) => { // 执行本行前端逻辑。
  const token = localStorage.getItem('token') // 声明并初始化当前变量。
  if (token) { // 根据条件判断是否执行分支。
    config.headers.Authorization = `Bearer ${token}` // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
  return config // 返回当前表达式结果。
}) // 执行本行前端逻辑。

// Unwrap the standard { code, message, data } envelope so callers get `data`.
request.interceptors.response.use( // 执行本行前端逻辑。
  (response) => { // 执行本行前端逻辑。
    const body = response.data // 声明并初始化当前变量。
    if (body && typeof body === 'object' && 'code' in body) { // 根据条件判断是否执行分支。
      if (body.code === 0) return body.data // 根据条件判断是否执行分支。
      ElMessage.error(body.message || '请求失败') // 执行本行前端逻辑。
      return Promise.reject(new Error(body.message || 'request failed')) // 返回当前表达式结果。
    } // 结束当前代码块或数据结构。
    return body // 返回当前表达式结果。
  }, // 结束当前代码块或数据结构。
  (error) => { // 执行本行前端逻辑。
    const msg = error.response?.data?.message || error.message || '网络错误' // 声明并初始化当前变量。
    ElMessage.error(msg) // 执行本行前端逻辑。
    return Promise.reject(error) // 返回当前表达式结果。
  }, // 结束当前代码块或数据结构。
) // 结束当前代码块或数据结构。

export default request // 导出当前变量、函数或配置。
