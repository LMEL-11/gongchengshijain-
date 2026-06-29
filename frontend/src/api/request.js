// 文件功能：配置 Axios 请求实例、登录令牌注入、统一响应解包和错误提示。
import axios from 'axios' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { ElMessage } from 'element-plus' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const request = axios.create({ // 保存request相关业务数据，作为后续计算、渲染或请求的输入。
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 声明baseURL字段，作为组件配置、请求参数或图表数据的一部分。
  timeout: 15000, // 声明timeout字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。

// Attach JWT token from localStorage on every request.
request.interceptors.request.use((config) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
  const token = localStorage.getItem('token') // 保存token相关业务数据，作为后续计算、渲染或请求的输入。
  if (token) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    config.headers.Authorization = `Bearer ${token}` // 更新config.headers.Authorization对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return config // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// Unwrap the standard { code, message, data } envelope so callers get `data`.
request.interceptors.response.use( // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
  (response) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    const body = response.data // 保存body相关业务数据，作为后续计算、渲染或请求的输入。
    if (body && typeof body === 'object' && 'code' in body) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      if (body.code === 0) return body.data // 根据当前状态、接口结果或用户输入选择对应交互路径。
      ElMessage.error(body.message || '请求失败') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      return Promise.reject(new Error(body.message || 'request failed')) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    } // 完成当前参数、配置或响应式数据结构的组装。
    return body // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  }, // 完成当前参数、配置或响应式数据结构的组装。
  (error) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    const msg = error.response?.data?.message || error.message || '网络错误' // 保存msg相关业务数据，作为后续计算、渲染或请求的输入。
    ElMessage.error(msg) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return Promise.reject(error) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  }, // 完成当前参数、配置或响应式数据结构的组装。
) // 完成当前参数、配置或响应式数据结构的组装。

export default request // 导出当前配置或接口方法，供应用其他模块复用。
