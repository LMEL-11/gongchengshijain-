// 文件功能：提供地图区域名规范化和 DataV GeoJSON 拉取缓存工具。
// 地理工具：区域名规范化 + DataV GeoJSON 拉取（带缓存）。
//
// 名称规范化需与后端 services/national.py 的 normalize_name 保持一致，
// 这样地图区域名（如「山东省」「青岛市」）才能匹配后端返回的数据键（「山东」「青岛」）。

const SPECIAL = { // 声明并初始化当前变量。
  内蒙古自治区: '内蒙古', // 配置当前对象字段。
  广西壮族自治区: '广西', // 配置当前对象字段。
  宁夏回族自治区: '宁夏', // 配置当前对象字段。
  新疆维吾尔自治区: '新疆', // 配置当前对象字段。
  西藏自治区: '西藏', // 配置当前对象字段。
  香港特别行政区: '香港', // 配置当前对象字段。
  澳门特别行政区: '澳门', // 配置当前对象字段。
} // 结束当前代码块或数据结构。

// 函数功能：规范化地图区域名称，去除常见行政区后缀。
export function normalizeName(name) { // 导出当前变量、函数或配置。
  if (!name) return '' // 根据条件判断是否执行分支。
  name = String(name).trim() // 赋值或更新当前变量/状态。
  if (SPECIAL[name]) return SPECIAL[name] // 根据条件判断是否执行分支。
  for (const suffix of ['特别行政区', '自治区', '省', '市', '区', '县']) { // 遍历集合或范围并逐项处理。
    if (name.endsWith(suffix) && name.length - suffix.length >= 2) { // 根据条件判断是否执行分支。
      return name.slice(0, -suffix.length) // 返回当前表达式结果。
    } // 结束当前代码块或数据结构。
  } // 结束当前代码块或数据结构。
  return name // 返回当前表达式结果。
} // 结束当前代码块或数据结构。

// adcode -> GeoJSON（_full 含下级区域）。100000 = 全国。
const DATAV = 'https://geo.datav.aliyun.com/areas_v3/bound' // 声明并初始化当前变量。
const cache = new Map() // 声明并初始化当前变量。

// 函数功能：拉取并缓存指定行政区的 GeoJSON 数据。
export async function fetchArea(adcode) { // 导出当前变量、函数或配置。
  if (cache.has(adcode)) return cache.get(adcode) // 根据条件判断是否执行分支。
  const res = await fetch(`${DATAV}/${adcode}_full.json`) // 声明并初始化当前变量。
  if (!res.ok) throw new Error(`加载地图失败 (${adcode}): ${res.status}`) // 根据条件判断是否执行分支。
  const data = await res.json() // 声明并初始化当前变量。
  cache.set(adcode, data) // 执行本行前端逻辑。
  return data // 返回当前表达式结果。
} // 结束当前代码块或数据结构。
