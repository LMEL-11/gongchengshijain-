import request from './request'

// --- 城市 / 行政区 ---
export const getCities = () => request.get('/cities')
export const getCityDistricts = (cityId) => request.get(`/cities/${cityId}/districts`)
export const getDistrictFacilities = (districtId) =>
  request.get(`/districts/${districtId}/facilities`)

// --- 房源 ---
export const getProperties = (params) => request.get('/properties', { params })
export const getProperty = (id) => request.get(`/properties/${id}`)

// --- 统计 / 分析 / 预测 ---
export const getOverview = () => request.get('/stats/overview')
export const getDistrictRanking = (cityId) =>
  request.get('/stats/district-ranking', { params: { city_id: cityId } })
export const getPriceDistribution = (cityId) =>
  request.get('/stats/price-distribution', { params: { city_id: cityId } })
export const getInvestmentRanking = (cityId) =>
  request.get('/stats/investment', { params: { city_id: cityId } })
export const getPriceTrend = (districtId) =>
  request.get('/stats/price-trend', { params: { district_id: districtId } })
export const getListingProfile = (districtId) =>
  request.get('/stats/listing-profile', { params: { district_id: districtId } })
export const predictPrice = (payload) => request.post('/stats/predict', payload)

// --- 全国二手房（大屏） ---
export const getNationalSummary = () => request.get('/national/summary')
export const getProvinceStats = () => request.get('/national/provinces')
export const getCityStats = (province) => request.get('/national/cities', { params: { province } })

// --- 大屏「真实采集数据」模式（基于 Property 表聚合） ---
export const getRealSummary = () => request.get('/national/real/summary')
export const getRealProvinces = () => request.get('/national/real/provinces')
export const getRealCities = (province) => request.get('/national/real/cities', { params: { province } })
export const getRealDistricts = (city) => request.get('/national/real/districts', { params: { city } })
export const getRealAreaProperties = (params) =>
  request.get('/national/real/area-properties', { params })

// --- 认证 ---
export const login = (username, password) => request.post('/auth/login', { username, password })
export const getMe = () => request.get('/auth/me')

// --- 管理后台 ---
export const adminGetProperties = (params) => request.get('/admin/properties', { params })
export const adminGetProperty = (id) => request.get(`/admin/properties/${id}`)
export const adminCreateProperty = (data) => request.post('/admin/properties', data)
export const adminUpdateProperty = (id, data) => request.put(`/admin/properties/${id}`, data)
export const adminDeleteProperty = (id) => request.delete(`/admin/properties/${id}`)
