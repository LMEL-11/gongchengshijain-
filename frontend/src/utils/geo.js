// 地理工具：区域名规范化 + DataV GeoJSON 拉取（带缓存）。
//
// 名称规范化需与后端 services/national.py 的 normalize_name 保持一致，
// 这样地图区域名（如「山东省」「青岛市」）才能匹配后端返回的数据键（「山东」「青岛」）。

const SPECIAL = {
  内蒙古自治区: '内蒙古',
  广西壮族自治区: '广西',
  宁夏回族自治区: '宁夏',
  新疆维吾尔自治区: '新疆',
  西藏自治区: '西藏',
  香港特别行政区: '香港',
  澳门特别行政区: '澳门',
}

export function normalizeName(name) {
  if (!name) return ''
  name = String(name).trim()
  if (SPECIAL[name]) return SPECIAL[name]
  for (const suffix of ['特别行政区', '自治区', '省', '市', '区', '县']) {
    if (name.endsWith(suffix) && name.length - suffix.length >= 2) {
      return name.slice(0, -suffix.length)
    }
  }
  return name
}

// adcode -> GeoJSON（_full 含下级区域）。100000 = 全国。
const DATAV = 'https://geo.datav.aliyun.com/areas_v3/bound'
const cache = new Map()

export async function fetchArea(adcode) {
  if (cache.has(adcode)) return cache.get(adcode)
  const res = await fetch(`${DATAV}/${adcode}_full.json`)
  if (!res.ok) throw new Error(`加载地图失败 (${adcode}): ${res.status}`)
  const data = await res.json()
  cache.set(adcode, data)
  return data
}
