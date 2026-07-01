// 文件功能：配置 Axios 请求实例、登录令牌注入、统一响应解包和错误提示。
import axios from 'axios' // 导入 axios，供当前前端模块渲染或交互逻辑使用。
import { ElMessage } from 'element-plus' // 导入 { ElMessage }，供当前前端模块渲染或交互逻辑使用。

const request = axios.create({ // 创建 request，用于保存页面状态、计算结果或接口参数。
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  timeout: 15000, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。

// Attach JWT token from localStorage on every request.
request.interceptors.request.use((config) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
  const token = localStorage.getItem('token') // 创建 token，用于保存页面状态、计算结果或接口参数。
  if (token) { // 根据当前页面状态或接口结果决定是否进入该分支。
    config.headers.Authorization = `Bearer ${token}` // 设置 config.headers.Authorization 的值，作为后续渲染、计算或请求的输入。
  } // 结束当前函数、对象、数组或组件配置块。
  return config // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// Unwrap the standard { code, message, data } envelope so callers get `data`.
request.interceptors.response.use( // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  (response) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    const body = response.data // 创建 body，用于保存页面状态、计算结果或接口参数。
    if (body && typeof body === 'object' && 'code' in body) { // 根据当前页面状态或接口结果决定是否进入该分支。
      if (body.code === 0) return body.data // 根据当前页面状态或接口结果决定是否进入该分支。
      ElMessage.error(body.message || '请求失败') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      return Promise.reject(new Error(body.message || 'request failed')) // 返回整理后的数据、组件配置或渲染结果。
    } // 结束当前函数、对象、数组或组件配置块。
    return body // 返回整理后的数据、组件配置或渲染结果。
  }, // 结束当前函数、对象、数组或组件配置块。
  (error) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
    const msg = error.response?.data?.message || error.message || '网络错误' // 创建 msg，用于保存页面状态、计算结果或接口参数。
    ElMessage.error(msg) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return Promise.reject(error) // 返回整理后的数据、组件配置或渲染结果。
  }, // 结束当前函数、对象、数组或组件配置块。
) // 结束当前函数、对象、数组或组件配置块。

export default request // 执行当前前端代码行，推动页面数据和交互流程继续运行。
