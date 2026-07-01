// 文件功能：提供自包含墨卡托投影和 GeoJSON 坐标遍历工具。
// 自包含的墨卡托投影（替代 d3-geo，避免外部依赖 / 离线可用）。
// 数学与 d3-geo 的 geoMercator().fitExtent() 完全一致：
//   - 量测尺度固定 150（与 d3 fit 内部一致）
//   - raw(λ,φ) = [λ, ln(tan(π/4 + φ/2))]，投影时 y 取反（屏幕 y 向下）
//   - fitExtent 计算 k、平移，使几何体边界恰好填入给定矩形并居中
//
// 用法：const project = geoMercator().fitExtent([[x0,y0],[x1,y1]], featureCollection)
//       const [x, y] = project([lng, lat])

const DEG = Math.PI / 180 // 创建 DEG，用于保存页面状态、计算结果或接口参数。
const BASE = 150 // 创建 BASE，用于保存页面状态、计算结果或接口参数。

// 基准尺度下的投影量测值（含 y 翻转）。
// 函数功能：将经纬度转换为基准墨卡托投影坐标。
function measure(lng, lat) { // 定义 measure 函数，处理页面交互、数据加载或状态同步。
  const lam = lng * DEG // 创建 lam，用于保存页面状态、计算结果或接口参数。
  const phi = lat * DEG // 创建 phi，用于保存页面状态、计算结果或接口参数。
  return [BASE * lam, -BASE * Math.log(Math.tan(Math.PI / 4 + phi / 2))] // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。

// 遍历任意 GeoJSON 的所有坐标点。
// 函数功能：递归遍历 GeoJSON 坐标数组中的每个点。
function walk(coords, cb) { // 定义 walk 函数，处理页面交互、数据加载或状态同步。
  if (typeof coords[0] === 'number') { // 根据当前页面状态或接口结果决定是否进入该分支。
    cb(coords[0], coords[1]) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    return // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  } // 结束当前函数、对象、数组或组件配置块。
  for (const c of coords) walk(c, cb) // 遍历当前数据集合，逐项生成页面需要的数据。
} // 结束当前函数、对象、数组或组件配置块。
// 函数功能：遍历 Feature、FeatureCollection 或 Geometry 的所有坐标。
function eachCoord(object, cb) { // 定义 eachCoord 函数，处理页面交互、数据加载或状态同步。
  const geoms = // 创建 geoms，用于保存页面状态、计算结果或接口参数。
    object.type === 'FeatureCollection' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      ? object.features.map((f) => f.geometry) // 设置 ? object.features.map((f 的值，作为后续渲染、计算或请求的输入。
      : object.type === 'Feature' // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        ? [object.geometry] // 执行当前前端代码行，推动页面数据和交互流程继续运行。
        : [object] // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  for (const g of geoms) if (g && g.coordinates) walk(g.coordinates, cb) // 遍历当前数据集合，逐项生成页面需要的数据。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：创建支持 fitExtent 的墨卡托投影函数。
export function geoMercator() { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  let k = 1 // 创建 k，用于保存页面状态、计算结果或接口参数。
  let tx = 0 // 创建 tx，用于保存页面状态、计算结果或接口参数。
  let ty = 0 // 创建 ty，用于保存页面状态、计算结果或接口参数。

  // 函数功能：按当前缩放和平移参数投影单个经纬度点。
  function projection(point) { // 定义 projection 函数，处理页面交互、数据加载或状态同步。
    const [mx, my] = measure(point[0], point[1]) // 创建 [mx, my]，用于保存页面状态、计算结果或接口参数。
    return [tx + k * mx, ty + k * my] // 返回整理后的数据、组件配置或渲染结果。
  } // 结束当前函数、对象、数组或组件配置块。

  projection.fitExtent = function (extent, object) { // 设置 projection.fitExtent 的值，作为后续渲染、计算或请求的输入。
    let x0 = Infinity // 创建 x0，用于保存页面状态、计算结果或接口参数。
    let y0 = Infinity // 创建 y0，用于保存页面状态、计算结果或接口参数。
    let x1 = -Infinity // 创建 x1，用于保存页面状态、计算结果或接口参数。
    let y1 = -Infinity // 创建 y1，用于保存页面状态、计算结果或接口参数。
    eachCoord(object, (lng, lat) => { // 定义箭头函数回调，处理异步结果、事件或响应式变化。
      const [mx, my] = measure(lng, lat) // 创建 [mx, my]，用于保存页面状态、计算结果或接口参数。
      if (mx < x0) x0 = mx // 根据当前页面状态或接口结果决定是否进入该分支。
      if (mx > x1) x1 = mx // 根据当前页面状态或接口结果决定是否进入该分支。
      if (my < y0) y0 = my // 根据当前页面状态或接口结果决定是否进入该分支。
      if (my > y1) y1 = my // 根据当前页面状态或接口结果决定是否进入该分支。
    }) // 结束当前函数、对象、数组或组件配置块。
    const w = extent[1][0] - extent[0][0] // 创建 w，用于保存页面状态、计算结果或接口参数。
    const h = extent[1][1] - extent[0][1] // 创建 h，用于保存页面状态、计算结果或接口参数。
    k = Math.min(w / (x1 - x0), h / (y1 - y0)) // 设置 k 的值，作为后续渲染、计算或请求的输入。
    tx = +extent[0][0] + (w - k * (x1 + x0)) / 2 // 设置 tx 的值，作为后续渲染、计算或请求的输入。
    ty = +extent[0][1] + (h - k * (y1 + y0)) / 2 // 设置 ty 的值，作为后续渲染、计算或请求的输入。
    return projection // 返回整理后的数据、组件配置或渲染结果。
  } // 结束当前函数、对象、数组或组件配置块。

  return projection // 返回整理后的数据、组件配置或渲染结果。
} // 结束当前函数、对象、数组或组件配置块。
