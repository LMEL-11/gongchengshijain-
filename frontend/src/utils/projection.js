// 自包含的墨卡托投影（替代 d3-geo，避免外部依赖 / 离线可用）。
// 数学与 d3-geo 的 geoMercator().fitExtent() 完全一致：
//   - 量测尺度固定 150（与 d3 fit 内部一致）
//   - raw(λ,φ) = [λ, ln(tan(π/4 + φ/2))]，投影时 y 取反（屏幕 y 向下）
//   - fitExtent 计算 k、平移，使几何体边界恰好填入给定矩形并居中
//
// 用法：const project = geoMercator().fitExtent([[x0,y0],[x1,y1]], featureCollection)
//       const [x, y] = project([lng, lat])

const DEG = Math.PI / 180
const BASE = 150 // d3 fit 内部使用的基准尺度

// 基准尺度下的投影量测值（含 y 翻转）。
function measure(lng, lat) {
  const lam = lng * DEG
  const phi = lat * DEG
  return [BASE * lam, -BASE * Math.log(Math.tan(Math.PI / 4 + phi / 2))]
}

// 遍历任意 GeoJSON 的所有坐标点。
function walk(coords, cb) {
  if (typeof coords[0] === 'number') {
    cb(coords[0], coords[1])
    return
  }
  for (const c of coords) walk(c, cb)
}
function eachCoord(object, cb) {
  const geoms =
    object.type === 'FeatureCollection'
      ? object.features.map((f) => f.geometry)
      : object.type === 'Feature'
        ? [object.geometry]
        : [object]
  for (const g of geoms) if (g && g.coordinates) walk(g.coordinates, cb)
}

export function geoMercator() {
  let k = 1
  let tx = 0
  let ty = 0

  function projection(point) {
    const [mx, my] = measure(point[0], point[1])
    return [tx + k * mx, ty + k * my]
  }

  projection.fitExtent = function (extent, object) {
    let x0 = Infinity
    let y0 = Infinity
    let x1 = -Infinity
    let y1 = -Infinity
    eachCoord(object, (lng, lat) => {
      const [mx, my] = measure(lng, lat)
      if (mx < x0) x0 = mx
      if (mx > x1) x1 = mx
      if (my < y0) y0 = my
      if (my > y1) y1 = my
    })
    const w = extent[1][0] - extent[0][0]
    const h = extent[1][1] - extent[0][1]
    k = Math.min(w / (x1 - x0), h / (y1 - y0))
    tx = +extent[0][0] + (w - k * (x1 + x0)) / 2
    ty = +extent[0][1] + (h - k * (y1 + y0)) / 2
    return projection
  }

  return projection
}
