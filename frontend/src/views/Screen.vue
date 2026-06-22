<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import {
  getRealAreaProperties,
  getRealCities,
  getRealDistricts,
  getRealProvinces,
  getRealSummary,
} from '@/api'
import BaiduPropertyMap from '@/components/screen/BaiduPropertyMap.vue'
import Donut from '@/components/screen/Donut.vue'
import GeoMap3D from '@/components/screen/GeoMap3D.vue'
import RankBar from '@/components/screen/RankBar.vue'
import ScreenPanel from '@/components/screen/ScreenPanel.vue'
import { useAutoFit } from '@/composables/useAutoFit'
import { normalizeName } from '@/utils/geo'

const MUNICIPALITIES = new Set(['北京', '北京市', '上海', '上海市', '天津', '天津市', '重庆', '重庆市'])
const { scale, designW, designH } = useAutoFit()

const mapRef = ref(null)
const summary = ref({})
const rankData = ref([]) // 当前层级行：省份列表 / 某省城市列表
const path = ref([{ adcode: 100000, name: '全国' }])
const clock = ref('')
const baiduVisible = ref(false)
const baiduLoading = ref(false)
const baiduPayload = ref({})
const baiduTitle = ref('')
const baiduAddress = ref('')

const level = computed(() => path.value.length) // 1 全国 / 2 省 / 3 市
const isMunicipalityLevel = computed(
  () => level.value === 2 && MUNICIPALITIES.has(path.value[1]?.name),
)
const isDistrictMapLevel = computed(() => level.value >= 3 || isMunicipalityLevel.value)
const stageStyle = computed(() => ({
  width: designW + 'px',
  height: designH + 'px',
  transform: `translate(-50%, -50%) scale(${scale.value})`,
}))

// 地图着色数据：全国按省、省级按市的「真实房源数」；市级（商圈）无地图边界 -> 自然不匹配走中性色
const dataMap = computed(() => {
  const m = {}
  for (const r of rankData.value) {
    m[r.name] = r.count
    m[normalizeName(r.name)] = r.count
  }
  return m
})

const rankTitle = computed(() => {
  if (level.value === 1) return '省份房源数 TOP'
  if (isMunicipalityLevel.value) return `${path.value[1]?.name} · 行政区房源数 TOP`
  if (level.value === 2) return `${path.value[1]?.name} · 城市房源数 TOP`
  return `${path.value[2]?.name} · 行政区房源数 TOP`
})
const priceTitle = computed(
  () =>
    (level.value === 1 ? '省份' : level.value === 2 && !isMunicipalityLevel.value ? '城市' : '行政区') +
    '均价 TOP（元/㎡）',
)

const roomItems = computed(() => summary.value.room_dist || [])
const countBars = computed(() => rankData.value.map((r) => ({ name: r.name, value: r.count })))
const priceBars = computed(() =>
  [...rankData.value]
    .sort((a, b) => (b.avg_price || 0) - (a.avg_price || 0))
    .map((r) => ({ name: r.name, value: r.avg_price || 0 })),
)
const cityTop = computed(() => summary.value.top_cities || [])
const tableRows = computed(() => rankData.value.slice(0, 14))
const mapHint = computed(() =>
  isDistrictMapLevel.value
    ? '拖拽旋转 · 滚轮缩放 · 点击区县查看百度地图房源点'
    : '拖拽旋转 · 滚轮缩放 · 点击高亮区域下钻（省 → 市）',
)
const leafClickLabel = computed(() => (isDistrictMapLevel.value ? '查看百度地图房源点' : ''))

async function onLevelChange(ctx) {
  path.value = ctx.path
  if (ctx.path.length === 1) {
    rankData.value = await getRealProvinces()
  } else if (ctx.path.length === 2) {
    rankData.value = await getRealCities(ctx.path[1].name)
  } else {
    // 市级下钻：按行政区汇总该市商圈房源数，匹配城市地图边界
    rankData.value = await getRealDistricts(ctx.path[2].name)
  }
}

function crumbTo(i) {
  if (i < path.value.length - 1) mapRef.value?.goToLevel(i)
}

async function onRegionClick(region) {
  if (!isDistrictMapLevel.value || !region?.name) return
  const cityName = isMunicipalityLevel.value ? path.value[1]?.name : path.value[2]?.name
  const areaPath = path.value.slice(1).map((item) => item.name)
  baiduTitle.value = `${region.name} · 百度地图房源分布`
  baiduAddress.value = `${areaPath.join('')}${region.name}`
  baiduVisible.value = true
  baiduLoading.value = true
  baiduPayload.value = {
    area: region.name,
    property_count: region.value || 0,
    coordinate_count: 0,
    returned_count: 0,
    avg_price: 0,
    items: [],
  }
  try {
    baiduPayload.value = await getRealAreaProperties({
      city: cityName,
      area: region.name,
      limit: 800,
    })
  } catch (e) {
    console.error('加载百度地图房源点失败', e)
  } finally {
    baiduLoading.value = false
  }
}

const fmt = (n) => Number(n || 0).toLocaleString()

let timer
function tick() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  clock.value = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

onMounted(async () => {
  tick()
  timer = setInterval(tick, 1000)
  try {
    summary.value = await getRealSummary()
  } catch (e) {
    console.error('加载概览失败', e)
  }
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="screen-root">
    <div class="stage" :style="stageStyle">
      <!-- 顶栏 -->
      <header class="s-header">
        <div class="s-title">全国二手房数据可视化平台</div>
        <div class="s-meta">
          <span class="s-clock">{{ clock }}</span>
          <nav class="s-nav">
            <RouterLink to="/dashboard">房源总览</RouterLink>
            <RouterLink to="/explore">房源探索</RouterLink>
            <RouterLink to="/analysis">数据分析</RouterLink>
          </nav>
        </div>
      </header>

      <div class="s-body">
        <!-- 左列 -->
        <div class="s-col">
          <ScreenPanel title="全国概览">
            <div class="kpis">
              <div class="kpi">
                <div class="kpi-val">{{ fmt(summary.count) }}<i>套</i></div>
                <div class="kpi-label">真实房源</div>
              </div>
              <div class="kpi">
                <div class="kpi-val">{{ summary.province_count || 0 }}<i>/{{ summary.city_count || 0 }}</i></div>
                <div class="kpi-label">覆盖省 / 城市</div>
              </div>
              <div class="kpi">
                <div class="kpi-val">{{ fmt(summary.district_count) }}<i>个</i></div>
                <div class="kpi-label">覆盖商圈</div>
              </div>
              <div class="kpi">
                <div class="kpi-val">{{ fmt(summary.avg_price) }}<i>元/㎡</i></div>
                <div class="kpi-label">平均单价</div>
              </div>
            </div>
          </ScreenPanel>
          <ScreenPanel title="户型结构">
            <Donut :items="roomItems" />
          </ScreenPanel>
          <ScreenPanel :title="rankTitle">
            <RankBar :data="countBars" :max="8" color="#3fe0ff" />
          </ScreenPanel>
        </div>

        <!-- 中央地图 -->
        <div class="s-center">
          <div class="bar">
            <div class="crumbs">
              <template v-for="(p, i) in path" :key="p.adcode">
                <span
                  class="crumb"
                  :class="{ active: i === path.length - 1, link: i < path.length - 1 }"
                  @click="crumbTo(i)"
                  >{{ p.name }}</span
                >
                <span v-if="i < path.length - 1" class="sep">›</span>
              </template>
            </div>
            <button v-if="path.length > 1" class="back" @click="mapRef?.back()">‹ 返回上级</button>
          </div>
          <div class="map-wrap">
            <GeoMap3D
              ref="mapRef"
              :data-map="dataMap"
              value-label="真实房源数"
              :leaf-click-label="leafClickLabel"
              @levelchange="onLevelChange"
              @regionclick="onRegionClick"
            />
          </div>
          <div class="hint">{{ mapHint }}</div>
        </div>

        <!-- 右列 -->
        <div class="s-col">
          <ScreenPanel title="城市房源数 TOP10（全国）">
            <RankBar :data="cityTop" :max="10" color="#ffd166" />
          </ScreenPanel>
          <ScreenPanel :title="priceTitle">
            <RankBar :data="priceBars" :max="8" color="#7c8cff" />
          </ScreenPanel>
          <ScreenPanel title="数据明细">
            <div class="dtable">
              <div class="dt-head">
                <span class="c-name">名称</span>
                <span>房源</span>
                <span>均价</span>
                <span>商圈</span>
              </div>
              <div class="dt-body">
                <div v-for="r in tableRows" :key="r.name" class="dt-row">
                  <span class="c-name">{{ r.name }}</span>
                  <span>{{ fmt(r.count) }}</span>
                  <span>{{ fmt(r.avg_price) }}</span>
                  <span>{{ r.district_count ? fmt(r.district_count) : '—' }}</span>
                </div>
                <div v-if="!tableRows.length" class="dt-empty">暂无数据</div>
              </div>
            </div>
          </ScreenPanel>
        </div>
      </div>
      <BaiduPropertyMap
        :visible="baiduVisible"
        :title="baiduTitle"
        :address="baiduAddress"
        :payload="baiduPayload"
        :loading="baiduLoading"
        @close="baiduVisible = false"
      />
    </div>
  </div>
</template>

<style scoped>
.screen-root {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background:
    radial-gradient(1200px 700px at 50% 18%, #0a2249 0%, #061634 55%, #030c1e 100%);
  color: #cfe8ff;
}
.stage {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: center center;
  display: flex;
  flex-direction: column;
}

/* 顶栏 */
.s-header {
  position: relative;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, rgba(13, 44, 88, 0.6), rgba(6, 18, 40, 0));
  border-bottom: 1px solid rgba(63, 224, 255, 0.15);
}
.s-title {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 6px;
  background: linear-gradient(180deg, #e8f7ff, #5fd0ff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 2px 16px rgba(63, 224, 255, 0.35);
}
.s-meta {
  position: absolute;
  right: 24px;
  top: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 6px;
}
.s-clock {
  font-size: 14px;
  color: #8fc0e8;
  font-variant-numeric: tabular-nums;
}
.s-nav {
  display: flex;
  gap: 14px;
}
.s-nav a {
  font-size: 13px;
  color: #9fd0f0;
  text-decoration: none;
  padding: 3px 10px;
  border: 1px solid rgba(63, 224, 255, 0.25);
  border-radius: 4px;
  transition: all 0.2s;
}
.s-nav a:hover {
  color: #fff;
  background: rgba(63, 224, 255, 0.15);
}

/* 主体三列 */
.s-body {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 16px;
  padding: 16px;
}
.s-col {
  width: 470px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.s-center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* 面包屑 */
.bar {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 40px;
}
.crumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
}
.crumb.link {
  cursor: pointer;
  color: #8fc0e8;
}
.crumb.link:hover {
  color: #5fe9ff;
}
.crumb.active {
  color: #fff;
  font-weight: 700;
}
.sep {
  color: #4a6f92;
}
.back {
  cursor: pointer;
  background: rgba(63, 224, 255, 0.12);
  border: 1px solid rgba(63, 224, 255, 0.4);
  color: #bfeaff;
  padding: 4px 14px;
  border-radius: 4px;
  font-size: 13px;
  transition: all 0.2s;
}
.back:hover {
  background: rgba(63, 224, 255, 0.25);
  color: #fff;
}
.map-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
}
.hint {
  height: 22px;
  text-align: center;
  font-size: 12px;
  color: #5e84a8;
}

/* KPI */
.kpis {
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.kpi {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(63, 224, 255, 0.05);
  border: 1px solid rgba(63, 224, 255, 0.12);
  border-radius: 4px;
}
.kpi-val {
  font-size: 30px;
  font-weight: 800;
  color: #5fe9ff;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 14px rgba(63, 224, 255, 0.4);
}
.kpi-val i {
  font-size: 13px;
  font-style: normal;
  color: #7fb0d8;
  margin-left: 3px;
}
.kpi-label {
  margin-top: 4px;
  font-size: 13px;
  color: #9fc4e4;
}

/* 明细表 */
.dtable {
  height: 100%;
  display: flex;
  flex-direction: column;
  font-size: 13px;
}
.dt-head,
.dt-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 4px;
  text-align: right;
}
.dt-head {
  color: #7fb0d8;
  padding: 4px 6px;
  border-bottom: 1px solid rgba(63, 224, 255, 0.18);
}
.dt-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.dt-row {
  padding: 5px 6px;
  border-bottom: 1px dashed rgba(63, 224, 255, 0.08);
  color: #cfe8ff;
  font-variant-numeric: tabular-nums;
}
.dt-row:nth-child(odd) {
  background: rgba(63, 224, 255, 0.03);
}
.c-name {
  text-align: left;
  color: #eaf6ff;
}
.dt-empty {
  text-align: center;
  color: #5e84a8;
  padding-top: 20px;
}
.dt-body::-webkit-scrollbar {
  width: 5px;
}
.dt-body::-webkit-scrollbar-thumb {
  background: rgba(63, 224, 255, 0.3);
  border-radius: 3px;
}
</style>
