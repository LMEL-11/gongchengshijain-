// 文件功能：提供自包含墨卡托投影和 GeoJSON 坐标遍历工具。
// 自包含的墨卡托投影（替代 d3-geo，避免外部依赖 / 离线可用）。
// 数学与 d3-geo 的 geoMercator().fitExtent() 完全一致：
//   - 量测尺度固定 150（与 d3 fit 内部一致）
//   - raw(λ,φ) = [λ, ln(tan(π/4 + φ/2))]，投影时 y 取反（屏幕 y 向下）
//   - fitExtent 计算 k、平移，使几何体边界恰好填入给定矩形并居中
//
// 用法：const project = geoMercator().fitExtent([[x0,y0],[x1,y1]], featureCollection)
//       const [x, y] = project([lng, lat])

const DEG = Math.PI / 180 // 保存DEG相关业务数据，作为后续计算、渲染或请求的输入。
const BASE = 150 // d3 fit 内部使用的基准尺度

// 基准尺度下的投影量测值（含 y 翻转）。
// 函数功能：将经纬度转换为基准墨卡托投影坐标。
function measure(lng, lat) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const lam = lng * DEG // 保存lam相关业务数据，作为后续计算、渲染或请求的输入。
  const phi = lat * DEG // 保存phi相关业务数据，作为后续计算、渲染或请求的输入。
  return [BASE * lam, -BASE * Math.log(Math.tan(Math.PI / 4 + phi / 2))] // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。

// 遍历任意 GeoJSON 的所有坐标点。
// 函数功能：递归遍历 GeoJSON 坐标数组中的每个点。
function walk(coords, cb) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  if (typeof coords[0] === 'number') { // 根据当前状态、接口结果或用户输入选择对应交互路径。
    cb(coords[0], coords[1]) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    return // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  } // 完成当前参数、配置或响应式数据结构的组装。
  for (const c of coords) walk(c, cb) // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
} // 完成当前参数、配置或响应式数据结构的组装。
// 函数功能：遍历 Feature、FeatureCollection 或 Geometry 的所有坐标。
function eachCoord(object, cb) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const geoms = // 保存geoms相关业务数据，作为后续计算、渲染或请求的输入。
    object.type === 'FeatureCollection' // 更新object.type对应的页面状态，使界面展示与最新业务数据一致。
      ? object.features.map((f) => f.geometry) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
      : object.type === 'Feature' // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        ? [object.geometry] // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
        : [object] // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  for (const g of geoms) if (g && g.coordinates) walk(g.coordinates, cb) // 遍历当前数据集合，逐项转换为图表、地图或表单需要的结构。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：创建支持 fitExtent 的墨卡托投影函数。
export function geoMercator() { // 导出当前配置或接口方法，供应用其他模块复用。
  let k = 1 // 保存k相关业务数据，作为后续计算、渲染或请求的输入。
  let tx = 0 // 保存tx相关业务数据，作为后续计算、渲染或请求的输入。
  let ty = 0 // 保存ty相关业务数据，作为后续计算、渲染或请求的输入。

  // 函数功能：按当前缩放和平移参数投影单个经纬度点。
  function projection(point) { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
    const [mx, my] = measure(point[0], point[1]) // 保存[mx相关业务数据，作为后续计算、渲染或请求的输入。
    return [tx + k * mx, ty + k * my] // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  } // 完成当前参数、配置或响应式数据结构的组装。

  projection.fitExtent = function (extent, object) { // 更新projection.fitExtent对应的页面状态，使界面展示与最新业务数据一致。
    let x0 = Infinity // 保存x0相关业务数据，作为后续计算、渲染或请求的输入。
    let y0 = Infinity // 保存y0相关业务数据，作为后续计算、渲染或请求的输入。
    let x1 = -Infinity // 保存x1相关业务数据，作为后续计算、渲染或请求的输入。
    let y1 = -Infinity // 保存y1相关业务数据，作为后续计算、渲染或请求的输入。
    eachCoord(object, (lng, lat) => { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      const [mx, my] = measure(lng, lat) // 保存[mx相关业务数据，作为后续计算、渲染或请求的输入。
      if (mx < x0) x0 = mx // 根据当前状态、接口结果或用户输入选择对应交互路径。
      if (mx > x1) x1 = mx // 根据当前状态、接口结果或用户输入选择对应交互路径。
      if (my < y0) y0 = my // 根据当前状态、接口结果或用户输入选择对应交互路径。
      if (my > y1) y1 = my // 根据当前状态、接口结果或用户输入选择对应交互路径。
    }) // 完成当前参数、配置或响应式数据结构的组装。
    const w = extent[1][0] - extent[0][0] // 保存w相关业务数据，作为后续计算、渲染或请求的输入。
    const h = extent[1][1] - extent[0][1] // 保存h相关业务数据，作为后续计算、渲染或请求的输入。
    k = Math.min(w / (x1 - x0), h / (y1 - y0)) // 更新k对应的页面状态，使界面展示与最新业务数据一致。
    tx = +extent[0][0] + (w - k * (x1 + x0)) / 2 // 更新tx对应的页面状态，使界面展示与最新业务数据一致。
    ty = +extent[0][1] + (h - k * (y1 + y0)) / 2 // 更新ty对应的页面状态，使界面展示与最新业务数据一致。
    return projection // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
  } // 完成当前参数、配置或响应式数据结构的组装。

  return projection // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
} // 完成当前参数、配置或响应式数据结构的组装。
