<!-- 文件功能：定义应用根布局、顶部导航、登录状态展示和页面切换容器。 -->
<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const navItems = [
  { name: 'screen', label: '数据大屏', icon: 'DataBoard' },
  { name: 'dashboard', label: '房源总览', icon: 'HomeFilled' },
  { name: 'explore', label: '房源探索', icon: 'Search' },
  { name: 'analysis', label: '数据分析', icon: 'TrendCharts' },
]

// 函数功能：根据登录用户角色计算管理员导航项。
const adminNavItem = computed(() => {
  if (!auth.isAdmin) return []
  return [{ name: 'admin', label: '管理后台', icon: 'Setting' }]
})

// 大屏页、登录页为全屏布局，隐藏通用页头/页脚。
// 函数功能：判断当前页面是否使用无导航的全屏布局。
const bare = computed(() => route.name === 'screen' || route.name === 'login')
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
          <router-link
            v-for="item in adminNavItem"
            :key="item.name"
            :to="{ name: item.name }"
            class="nav-link"
            :class="{ active: route.name === item.name }"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </nav>
        <div class="user-area">
          <template v-if="auth.isLoggedIn">
            <span class="user-greeting">{{ auth.user?.username }}</span>
            <el-button text size="small" @click="auth.logout(); router.push('/login')">
              退出
            </el-button>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-link login-link">
              <el-icon><User /></el-icon>
              <span>登录</span>
            </router-link>
          </template>
        </div>
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
      智慧房源探索平台
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

/* ---- user area ---- */
.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-greeting {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.user-area .el-button {
  color: rgba(255, 255, 255, 0.85);
}

.login-link {
  font-size: 14px;
}
</style>
