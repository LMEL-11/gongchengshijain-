// 文件功能：封装前端访问后端城市、房源、统计、认证和管理接口的 API 方法。
import request from './request' // 导入 request，供当前前端模块渲染或交互逻辑使用。

// --- 城市 / 行政区 ---
// 函数功能：请求城市列表数据。
export const getCities = () => request.get('/cities') // 调用后端 GET /cities 接口，获取或提交对应业务数据。
// 函数功能：请求指定城市下的区域列表。
export const getCityDistricts = (cityId) => request.get(`/cities/${cityId}/districts`) // 调用后端 GET /cities/${cityId}/districts 接口，获取或提交对应业务数据。
// 函数功能：请求指定区域的周边配套设施。
export const getDistrictFacilities = (districtId) => // 导出 getDistrictFacilities 方法或状态，供其他页面和组件调用。
  request.get(`/districts/${districtId}/facilities`) // 调用后端 GET /districts/${districtId}/facilities 接口，获取或提交对应业务数据。

// --- 房源 ---
// 函数功能：按筛选条件请求房源列表。
export const getProperties = (params) => request.get('/properties', { params }) // 调用后端 GET /properties 接口，获取或提交对应业务数据。
// 函数功能：请求单套房源详情。
export const getProperty = (id) => request.get(`/properties/${id}`) // 调用后端 GET /properties/${id} 接口，获取或提交对应业务数据。

// --- 统计 / 分析 / 预测 ---
// 函数功能：请求总览统计指标。
export const getOverview = () => request.get('/stats/overview') // 调用后端 GET /stats/overview 接口，获取或提交对应业务数据。
// 函数功能：请求城市区域均价排行数据。
export const getDistrictRanking = (cityId) => // 导出 getDistrictRanking 方法或状态，供其他页面和组件调用。
  request.get('/stats/district-ranking', { params: { city_id: cityId } }) // 调用后端 GET /stats/district-ranking 接口，获取或提交对应业务数据。
// 函数功能：请求城市房源价格分布数据。
export const getPriceDistribution = (cityId) => // 导出 getPriceDistribution 方法或状态，供其他页面和组件调用。
  request.get('/stats/price-distribution', { params: { city_id: cityId } }) // 调用后端 GET /stats/price-distribution 接口，获取或提交对应业务数据。
// 函数功能：请求城市区域投资潜力排行数据。
export const getInvestmentRanking = (cityId) => // 导出 getInvestmentRanking 方法或状态，供其他页面和组件调用。
  request.get('/stats/investment', { params: { city_id: cityId } }) // 调用后端 GET /stats/investment 接口，获取或提交对应业务数据。
// 函数功能：请求指定区域的房价趋势数据。
export const getPriceTrend = (districtId) => // 导出 getPriceTrend 方法或状态，供其他页面和组件调用。
  request.get('/stats/price-trend', { params: { district_id: districtId } }) // 调用后端 GET /stats/price-trend 接口，获取或提交对应业务数据。
// 函数功能：请求指定区域的挂牌画像数据。
export const getListingProfile = (districtId) => // 导出 getListingProfile 方法或状态，供其他页面和组件调用。
  request.get('/stats/listing-profile', { params: { district_id: districtId } }) // 调用后端 GET /stats/listing-profile 接口，获取或提交对应业务数据。
// 函数功能：提交房源特征并请求房价预测结果。
export const predictPrice = (payload) => request.post('/stats/predict', payload) // 调用后端 POST /stats/predict 接口，获取或提交对应业务数据。

// --- 全国二手房（大屏） ---
// 函数功能：请求全国大屏总览统计。
export const getNationalSummary = () => request.get('/national/summary') // 调用后端 GET /national/summary 接口，获取或提交对应业务数据。
// 函数功能：请求省份维度统计数据。
export const getProvinceStats = () => request.get('/national/provinces') // 调用后端 GET /national/provinces 接口，获取或提交对应业务数据。
// 函数功能：请求指定省份下的城市统计数据。
export const getCityStats = (province) => request.get('/national/cities', { params: { province } }) // 调用后端 GET /national/cities 接口，获取或提交对应业务数据。

// --- 大屏「真实采集数据」模式（基于 Property 表聚合） ---
// 函数功能：请求真实采集数据模式的全国总览统计。
export const getRealSummary = () => request.get('/national/real/summary') // 调用后端 GET /national/real/summary 接口，获取或提交对应业务数据。
// 函数功能：请求真实采集数据模式的省份统计。
export const getRealProvinces = () => request.get('/national/real/provinces') // 调用后端 GET /national/real/provinces 接口，获取或提交对应业务数据。
// 函数功能：请求真实采集数据模式的城市统计。
export const getRealCities = (province) => request.get('/national/real/cities', { params: { province } }) // 调用后端 GET /national/real/cities 接口，获取或提交对应业务数据。
// 函数功能：请求真实采集数据模式的区域统计。
export const getRealDistricts = (city) => request.get('/national/real/districts', { params: { city } }) // 调用后端 GET /national/real/districts 接口，获取或提交对应业务数据。
// 函数功能：请求指定真实区域的房源点位和列表。
export const getRealAreaProperties = (params) => // 导出 getRealAreaProperties 方法或状态，供其他页面和组件调用。
  request.get('/national/real/area-properties', { params }) // 调用后端 GET /national/real/area-properties 接口，获取或提交对应业务数据。

// --- 认证 ---
// 函数功能：提交账号密码并请求登录结果。
export const login = (username, password) => request.post('/auth/login', { username, password }) // 调用后端 POST /auth/login 接口，获取或提交对应业务数据。
// 函数功能：请求当前登录用户信息。
export const getMe = () => request.get('/auth/me') // 调用后端 GET /auth/me 接口，获取或提交对应业务数据。

// --- 管理后台 ---
// 函数功能：请求后台房源分页列表。
export const adminGetProperties = (params) => request.get('/admin/properties', { params }) // 调用后端 GET /admin/properties 接口，获取或提交对应业务数据。
// 函数功能：请求后台单套房源详情。
export const adminGetProperty = (id) => request.get(`/admin/properties/${id}`) // 调用后端 GET /admin/properties/${id} 接口，获取或提交对应业务数据。
// 函数功能：提交后台新增房源数据。
export const adminCreateProperty = (data) => request.post('/admin/properties', data) // 调用后端 POST /admin/properties 接口，获取或提交对应业务数据。
// 函数功能：提交后台更新房源数据。
export const adminUpdateProperty = (id, data) => request.put(`/admin/properties/${id}`, data) // 调用后端 PUT /admin/properties/${id} 接口，获取或提交对应业务数据。
// 函数功能：请求后台删除指定房源。
export const adminDeleteProperty = (id) => request.delete(`/admin/properties/${id}`) // 调用后端 DELETE /admin/properties/${id} 接口，获取或提交对应业务数据。
