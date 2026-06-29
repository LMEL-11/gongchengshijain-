// 文件功能：提供自包含墨卡托投影和 GeoJSON 坐标遍历工具。
// 自包含的墨卡托投影（替代 d3-geo，避免外部依赖 / 离线可用）。
// 数学与 d3-geo 的 geoMercator().fitExtent() 完全一致：
//   - 量测尺度固定 150（与 d3 fit 内部一致）
//   - raw(λ,φ) = [λ, ln(tan(π/4 + φ/2))]，投影时 y 取反（屏幕 y 向下）
//   - fitExtent 计算 k、平移，使几何体边界恰好填入给定矩形并居中
//
// 用法：const project = geoMercator().fitExtent([[x0,y0],[x1,y1]], featureCollection)
//       const [x, y] = project([lng, lat])

const DEG = Math.PI / 180 // 逐行注释：声明并初始化当前变量。
const BASE = 150 // d3 fit 内部使用的基准尺度

// 基准尺度下的投影量测值（含 y 翻转）。
// 函数功能：将经纬度转换为基准墨卡托投影坐标。
function measure(lng, lat) { // 逐行注释：声明当前函数入口。
  const lam = lng * DEG // 逐行注释：声明并初始化当前变量。
  const phi = lat * DEG // 逐行注释：声明并初始化当前变量。
  return [BASE * lam, -BASE * Math.log(Math.tan(Math.PI / 4 + phi / 2))] // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。

// 遍历任意 GeoJSON 的所有坐标点。
// 函数功能：递归遍历 GeoJSON 坐标数组中的每个点。
function walk(coords, cb) { // 逐行注释：声明当前函数入口。
  if (typeof coords[0] === 'number') { // 逐行注释：根据条件判断是否执行分支。
    cb(coords[0], coords[1]) // 逐行注释：执行本行前端逻辑。
    return // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。
  for (const c of coords) walk(c, cb) // 逐行注释：遍历集合或范围并逐项处理。
} // 逐行注释：结束当前代码块或数据结构。
// 函数功能：遍历 Feature、FeatureCollection 或 Geometry 的所有坐标。
function eachCoord(object, cb) { // 逐行注释：声明当前函数入口。
  const geoms = // 逐行注释：声明并初始化当前变量。
    object.type === 'FeatureCollection' // 逐行注释：执行本行前端逻辑。
      ? object.features.map((f) => f.geometry) // 逐行注释：执行本行前端逻辑。
      : object.type === 'Feature' // 逐行注释：执行本行前端逻辑。
        ? [object.geometry] // 逐行注释：执行本行前端逻辑。
        : [object] // 逐行注释：执行本行前端逻辑。
  for (const g of geoms) if (g && g.coordinates) walk(g.coordinates, cb) // 逐行注释：遍历集合或范围并逐项处理。
} // 逐行注释：结束当前代码块或数据结构。

// 函数功能：创建支持 fitExtent 的墨卡托投影函数。
export function geoMercator() { // 逐行注释：导出当前变量、函数或配置。
  let k = 1 // 逐行注释：声明并初始化当前变量。
  let tx = 0 // 逐行注释：声明并初始化当前变量。
  let ty = 0 // 逐行注释：声明并初始化当前变量。

  // 函数功能：按当前缩放和平移参数投影单个经纬度点。
  function projection(point) { // 逐行注释：声明当前函数入口。
    const [mx, my] = measure(point[0], point[1]) // 逐行注释：声明并初始化当前变量。
    return [tx + k * mx, ty + k * my] // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。

  projection.fitExtent = function (extent, object) { // 逐行注释：赋值或更新当前变量/状态。
    let x0 = Infinity // 逐行注释：声明并初始化当前变量。
    let y0 = Infinity // 逐行注释：声明并初始化当前变量。
    let x1 = -Infinity // 逐行注释：声明并初始化当前变量。
    let y1 = -Infinity // 逐行注释：声明并初始化当前变量。
    eachCoord(object, (lng, lat) => { // 逐行注释：执行本行前端逻辑。
      const [mx, my] = measure(lng, lat) // 逐行注释：声明并初始化当前变量。
      if (mx < x0) x0 = mx // 逐行注释：根据条件判断是否执行分支。
      if (mx > x1) x1 = mx // 逐行注释：根据条件判断是否执行分支。
      if (my < y0) y0 = my // 逐行注释：根据条件判断是否执行分支。
      if (my > y1) y1 = my // 逐行注释：根据条件判断是否执行分支。
    }) // 逐行注释：执行本行前端逻辑。
    const w = extent[1][0] - extent[0][0] // 逐行注释：声明并初始化当前变量。
    const h = extent[1][1] - extent[0][1] // 逐行注释：声明并初始化当前变量。
    k = Math.min(w / (x1 - x0), h / (y1 - y0)) // 逐行注释：赋值或更新当前变量/状态。
    tx = +extent[0][0] + (w - k * (x1 + x0)) / 2 // 逐行注释：赋值或更新当前变量/状态。
    ty = +extent[0][1] + (h - k * (y1 + y0)) / 2 // 逐行注释：赋值或更新当前变量/状态。
    return projection // 逐行注释：返回当前表达式结果。
  } // 逐行注释：结束当前代码块或数据结构。

  return projection // 逐行注释：返回当前表达式结果。
} // 逐行注释：结束当前代码块或数据结构。
