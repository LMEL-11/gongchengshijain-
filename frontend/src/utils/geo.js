// 文件功能：提供地图区域名规范化和 DataV GeoJSON 拉取缓存工具。
// 地理工具：区域名规范化 + DataV GeoJSON 拉取（带缓存）。
//
// 名称规范化需与后端 services/national.py 的 normalize_name 保持一致，
// 这样地图区域名（如「山东省」「青岛市」）才能匹配后端返回的数据键（「山东」「青岛」）。

const SPECIAL = { // 创建 SPECIAL，用于保存页面状态、计算结果或接口参数。
  内蒙古自治区: '内蒙古', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  广西壮族自治区: '广西', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  宁夏回族自治区: '宁夏', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  新疆维吾尔自治区: '新疆', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  西藏自治区: '西藏', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  香港特别行政区: '香港', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  澳门特别行政区: '澳门', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：规范化地图区域名称，去除常见行政区后缀。
export function normalizeName(name) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  if (!name) return '' // 根据当前页面状态或接口结果决定是否进入该分支。
  name = String(name).trim() // 设置 name 的值，作为后续渲染、计算或请求的输入。
  if (SPECIAL[name]) return SPECIAL[name] // 根据当前页面状态或接口结果决定是否进入该分支。
  for (const suffix of ['特别行政区', '自治区', '省', '市', '区', '县']) { // 遍历当前数据集合，逐项生成页面需要的数据。
    if (name.endsWith(suffix) && name.length - suffix.length >= 2) { // 根据当前页面状态或接口结果决定是否进入该分支。
      return name.slice(0, -suffix.length) // 返回整理后的数据、组件配置或渲染结果。
    } // 结束当前函数、对象、数组或组件配置块。
  } // 结束当前函数、对象、数组或组件配置块。
  return name // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// adcode -> GeoJSON（_full 含下级区域）。100000 = 全国。
const DATAV = 'https://geo.datav.aliyun.com/areas_v3/bound' // 保存 DataV 行政区边界接口地址，供地图边界数据请求使用。
const cache = new Map() // 创建 cache，用于保存页面状态、计算结果或接口参数。

// 函数功能：拉取并缓存指定行政区的 GeoJSON 数据。
export async function fetchArea(adcode) { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  if (cache.has(adcode)) return cache.get(adcode) // 根据当前页面状态或接口结果决定是否进入该分支。
  const res = await fetch(`${DATAV}/${adcode}_full.json`) // 创建 res，用于保存页面状态、计算结果或接口参数。
  if (!res.ok) throw new Error(`加载地图失败 (${adcode}): ${res.status}`) // 根据当前页面状态或接口结果决定是否进入该分支。
  const data = await res.json() // 创建 data，用于保存页面状态、计算结果或接口参数。
  cache.set(adcode, data) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  return data // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
