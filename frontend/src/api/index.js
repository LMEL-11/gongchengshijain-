// 文件功能：封装前端访问后端城市、房源、统计、认证和管理接口的 API 方法。
import request from './request' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

// --- 城市 / 行政区 ---
// 函数功能：请求城市列表数据。
export const getCities = () => request.get('/cities') // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求指定城市下的区域列表。
export const getCityDistricts = (cityId) => request.get(`/cities/${cityId}/districts`) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求指定区域的周边配套设施。
export const getDistrictFacilities = (districtId) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get(`/districts/${districtId}/facilities`) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

// --- 房源 ---
// 函数功能：按筛选条件请求房源列表。
export const getProperties = (params) => request.get('/properties', { params }) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求单套房源详情。
export const getProperty = (id) => request.get(`/properties/${id}`) // 导出当前配置或接口方法，供应用其他模块复用。

// --- 统计 / 分析 / 预测 ---
// 函数功能：请求总览统计指标。
export const getOverview = () => request.get('/stats/overview') // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求城市区域均价排行数据。
export const getDistrictRanking = (cityId) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get('/stats/district-ranking', { params: { city_id: cityId } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
// 函数功能：请求城市房源价格分布数据。
export const getPriceDistribution = (cityId) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get('/stats/price-distribution', { params: { city_id: cityId } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
// 函数功能：请求城市区域投资潜力排行数据。
export const getInvestmentRanking = (cityId) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get('/stats/investment', { params: { city_id: cityId } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
// 函数功能：请求指定区域的房价趋势数据。
export const getPriceTrend = (districtId) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get('/stats/price-trend', { params: { district_id: districtId } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
// 函数功能：请求指定区域的挂牌画像数据。
export const getListingProfile = (districtId) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get('/stats/listing-profile', { params: { district_id: districtId } }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
// 函数功能：提交房源特征并请求房价预测结果。
export const predictPrice = (payload) => request.post('/stats/predict', payload) // 导出当前配置或接口方法，供应用其他模块复用。

// --- 全国二手房（大屏） ---
// 函数功能：请求全国大屏总览统计。
export const getNationalSummary = () => request.get('/national/summary') // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求省份维度统计数据。
export const getProvinceStats = () => request.get('/national/provinces') // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求指定省份下的城市统计数据。
export const getCityStats = (province) => request.get('/national/cities', { params: { province } }) // 导出当前配置或接口方法，供应用其他模块复用。

// --- 大屏「真实采集数据」模式（基于 Property 表聚合） ---
// 函数功能：请求真实采集数据模式的全国总览统计。
export const getRealSummary = () => request.get('/national/real/summary') // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求真实采集数据模式的省份统计。
export const getRealProvinces = () => request.get('/national/real/provinces') // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求真实采集数据模式的城市统计。
export const getRealCities = (province) => request.get('/national/real/cities', { params: { province } }) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求真实采集数据模式的区域统计。
export const getRealDistricts = (city) => request.get('/national/real/districts', { params: { city } }) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求指定真实区域的房源点位和列表。
export const getRealAreaProperties = (params) => // 导出当前配置或接口方法，供应用其他模块复用。
  request.get('/national/real/area-properties', { params }) // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。

// --- 认证 ---
// 函数功能：提交账号密码并请求登录结果。
export const login = (username, password) => request.post('/auth/login', { username, password }) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求当前登录用户信息。
export const getMe = () => request.get('/auth/me') // 导出当前配置或接口方法，供应用其他模块复用。

// --- 管理后台 ---
// 函数功能：请求后台房源分页列表。
export const adminGetProperties = (params) => request.get('/admin/properties', { params }) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求后台单套房源详情。
export const adminGetProperty = (id) => request.get(`/admin/properties/${id}`) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：提交后台新增房源数据。
export const adminCreateProperty = (data) => request.post('/admin/properties', data) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：提交后台更新房源数据。
export const adminUpdateProperty = (id, data) => request.put(`/admin/properties/${id}`, data) // 导出当前配置或接口方法，供应用其他模块复用。
// 函数功能：请求后台删除指定房源。
export const adminDeleteProperty = (id) => request.delete(`/admin/properties/${id}`) // 导出当前配置或接口方法，供应用其他模块复用。
