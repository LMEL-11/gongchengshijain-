// 文件功能：提供地图区域名规范化和 DataV GeoJSON 拉取缓存工具。
// 地理工具：区域名规范化 + DataV GeoJSON 拉取（带缓存）。
//
// 名称规范化需与后端 services/national.py 的 normalize_name 保持一致，
// 这样地图区域名（如「山东省」「青岛市」）才能匹配后端返回的数据键（「山东」「青岛」）。

const SPECIAL = { // 保存SPECIAL相关业务数据，作为后续计算、渲染或请求的输入。
  内蒙古自治区: '内蒙古', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  广西壮族自治区: '广西', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  宁夏回族自治区: '宁夏', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  新疆维吾尔自治区: '新疆', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  西藏自治区: '西藏', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  香港特别行政区: '香港', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  澳门特别行政区: '澳门', // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：规范化地图区域名称，去除常见行政区后缀。
export function normalizeName(name) { // 导出当前配置或接口方法，供应用其他模块复用。
  if (!name) return '' // 根据当前状态、接口结果或用户输入选择对应交互路径。
  name = String(name).trim() // 更新name对应的页面状态，使界面展示与最新业务数据一致。
  if (SPECIAL[name]) return SPECIAL[name] // 根据当前状态、接口结果或用户输入选择对应交互路径。
  for (const suffix of ['特别行政区', '自治区', '省', '市', '区', '县']) { // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
    if (name.endsWith(suffix) && name.length - suffix.length >= 2) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      return name.slice(0, -suffix.length) // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } // 完成当前参数、配置或响应式数据结构的组装。
  return name // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// adcode -> GeoJSON（_full 含下级区域）。100000 = 全国。
const DATAV = 'https://geo.datav.aliyun.com/areas_v3/bound' // 保存DATAV相关业务数据，作为后续计算、渲染或请求的输入。
const cache = new Map() // 保存cache相关业务数据，作为后续计算、渲染或请求的输入。

// 函数功能：拉取并缓存指定行政区的 GeoJSON 数据。
export async function fetchArea(adcode) { // 导出当前配置或接口方法，供应用其他模块复用。
  if (cache.has(adcode)) return cache.get(adcode) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const res = await fetch(`${DATAV}/${adcode}_full.json`) // 保存res相关业务数据，作为后续计算、渲染或请求的输入。
  if (!res.ok) throw new Error(`加载地图失败 (${adcode}): ${res.status}`) // 根据当前状态、接口结果或用户输入选择对应交互路径。
  const data = await res.json() // 保存data相关业务数据，作为后续计算、渲染或请求的输入。
  cache.set(adcode, data) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  return data // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
