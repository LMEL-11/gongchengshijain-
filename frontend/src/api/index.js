// 文件功能：封装前端访问后端城市、房源、统计、认证和管理接口的 API 方法。
import request from './request'

// --- 城市 / 行政区 ---
// 函数功能：请求城市列表数据。
export const getCities = () => request.get('/cities')
// 函数功能：请求指定城市下的区域列表。
export const getCityDistricts = (cityId) => request.get(`/cities/${cityId}/districts`)
// 函数功能：请求指定区域的周边配套设施。
export const getDistrictFacilities = (districtId) =>
  request.get(`/districts/${districtId}/facilities`)

// --- 房源 ---
// 函数功能：按筛选条件请求房源列表。
export const getProperties = (params) => request.get('/properties', { params })
// 函数功能：请求单套房源详情。
export const getProperty = (id) => request.get(`/properties/${id}`)

// --- 统计 / 分析 / 预测 ---
// 函数功能：请求总览统计指标。
export const getOverview = () => request.get('/stats/overview')
// 函数功能：请求城市区域均价排行数据。
export const getDistrictRanking = (cityId) =>
  request.get('/stats/district-ranking', { params: { city_id: cityId } })
// 函数功能：请求城市房源价格分布数据。
export const getPriceDistribution = (cityId) =>
  request.get('/stats/price-distribution', { params: { city_id: cityId } })
// 函数功能：请求城市区域投资潜力排行数据。
export const getInvestmentRanking = (cityId) =>
  request.get('/stats/investment', { params: { city_id: cityId } })
// 函数功能：请求指定区域的房价趋势数据。
export const getPriceTrend = (districtId) =>
  request.get('/stats/price-trend', { params: { district_id: districtId } })
// 函数功能：请求指定区域的挂牌画像数据。
export const getListingProfile = (districtId) =>
  request.get('/stats/listing-profile', { params: { district_id: districtId } })
// 函数功能：提交房源特征并请求房价预测结果。
export const predictPrice = (payload) => request.post('/stats/predict', payload)

// --- 全国二手房（大屏） ---
// 函数功能：请求全国大屏总览统计。
export const getNationalSummary = () => request.get('/national/summary')
// 函数功能：请求省份维度统计数据。
export const getProvinceStats = () => request.get('/national/provinces')
// 函数功能：请求指定省份下的城市统计数据。
export const getCityStats = (province) => request.get('/national/cities', { params: { province } })

// --- 大屏「真实采集数据」模式（基于 Property 表聚合） ---
// 函数功能：请求真实采集数据模式的全国总览统计。
export const getRealSummary = () => request.get('/national/real/summary')
// 函数功能：请求真实采集数据模式的省份统计。
export const getRealProvinces = () => request.get('/national/real/provinces')
// 函数功能：请求真实采集数据模式的城市统计。
export const getRealCities = (province) => request.get('/national/real/cities', { params: { province } })
// 函数功能：请求真实采集数据模式的区域统计。
export const getRealDistricts = (city) => request.get('/national/real/districts', { params: { city } })
// 函数功能：请求指定真实区域的房源点位和列表。
export const getRealAreaProperties = (params) =>
  request.get('/national/real/area-properties', { params })

// --- 认证 ---
// 函数功能：提交账号密码并请求登录结果。
export const login = (username, password) => request.post('/auth/login', { username, password })
// 函数功能：请求当前登录用户信息。
export const getMe = () => request.get('/auth/me')

// --- 管理后台 ---
// 函数功能：请求后台房源分页列表。
export const adminGetProperties = (params) => request.get('/admin/properties', { params })
// 函数功能：请求后台单套房源详情。
export const adminGetProperty = (id) => request.get(`/admin/properties/${id}`)
// 函数功能：提交后台新增房源数据。
export const adminCreateProperty = (data) => request.post('/admin/properties', data)
// 函数功能：提交后台更新房源数据。
export const adminUpdateProperty = (id, data) => request.put(`/admin/properties/${id}`, data)
// 函数功能：请求后台删除指定房源。
export const adminDeleteProperty = (id) => request.delete(`/admin/properties/${id}`)
