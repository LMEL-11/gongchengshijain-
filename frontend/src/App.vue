<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const navItems = [
  { name: 'screen', label: '数据大屏', icon: 'DataBoard' },
  { name: 'dashboard', label: '房源总览', icon: 'HomeFilled' },
  { name: 'explore', label: '房源探索', icon: 'Search' },
  { name: 'analysis', label: '数据分析', icon: 'TrendCharts' },
]
const route = useRoute()
// 大屏页为全屏深色独立布局，隐藏通用页头/页脚。
const bare = computed(() => route.name === 'screen')
</script>

<template>
  <div class="app-shell">
    <header v-if="!bare" class="app-header">
      <div class="header-inner">
        <router-link to="/" class="brand">
          <el-icon :size="24"><OfficeBuilding /></el-icon>
          <span>智慧房源探索平台</span>
        </router-link>
        <nav class="nav">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="{ name: item.name }"
            class="nav-link"
            :class="{ active: route.name === item.name }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
      </div>
    </header>

    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer v-if="!bare" class="app-footer">
      智慧房源探索平台 · Flask + Vue 3 + Three.js · 数据为合成演示数据
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.app-header {
  background: linear-gradient(90deg, #1e3a8a, #2563eb);
  color: #fff;
  box-shadow: 0 2px 12px rgba(30, 58, 138, 0.25);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.nav {
  display: flex;
  gap: 6px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 15px;
  opacity: 0.85;
  transition: all 0.2s;
}

.nav-link:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.12);
}

.nav-link.active {
  opacity: 1;
  background: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.app-main {
  flex: 1;
}

.app-footer {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 13px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
