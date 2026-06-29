<!-- 文件功能：定义应用根布局、顶部导航、登录状态展示和页面切换容器。 -->
<script setup>
import { computed } from 'vue' // 导入本行所需的依赖。
import { useRoute, useRouter } from 'vue-router' // 导入本行所需的依赖。
import { useAuthStore } from '@/store/auth' // 导入本行所需的依赖。

const route = useRoute() // 声明并初始化当前变量。
const router = useRouter() // 声明并初始化当前变量。
const auth = useAuthStore() // 声明并初始化当前变量。

const navItems = [ // 声明并初始化当前变量。
  { name: 'screen', label: '数据大屏', icon: 'DataBoard' }, // 配置当前对象字段。
  { name: 'dashboard', label: '房源总览', icon: 'HomeFilled' }, // 配置当前对象字段。
  { name: 'explore', label: '房源探索', icon: 'Search' }, // 配置当前对象字段。
  { name: 'analysis', label: '数据分析', icon: 'TrendCharts' }, // 配置当前对象字段。
] // 结束当前代码块或数据结构。

// 函数功能：根据登录用户角色计算管理员导航项。
const adminNavItem = computed(() => { // 声明并初始化当前变量。
  if (!auth.isAdmin) return [] // 根据条件判断是否执行分支。
  return [{ name: 'admin', label: '管理后台', icon: 'Setting' }] // 返回当前表达式结果。
}) // 执行本行前端逻辑。

// 大屏页、登录页为全屏布局，隐藏通用页头/页脚。
// 函数功能：判断当前页面是否使用无导航的全屏布局。
const bare = computed(() => route.name === 'screen' || route.name === 'login') // 声明并初始化当前变量。
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
.app-shell { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  flex-direction: column; /* 设置当前样式属性。 */
  min-height: 100%; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.app-header { /* 开始当前样式规则块。 */
  background: linear-gradient(90deg, #1e3a8a, #2563eb); /* 设置当前样式属性。 */
  color: #fff; /* 设置当前样式属性。 */
  box-shadow: 0 2px 12px rgba(30, 58, 138, 0.25); /* 设置当前样式属性。 */
  position: sticky; /* 设置当前样式属性。 */
  top: 0; /* 设置当前样式属性。 */
  z-index: 100; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.header-inner { /* 开始当前样式规则块。 */
  max-width: 1280px; /* 设置当前样式属性。 */
  margin: 0 auto; /* 设置当前样式属性。 */
  height: 60px; /* 设置当前样式属性。 */
  padding: 0 20px; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: space-between; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.brand { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 10px; /* 设置当前样式属性。 */
  font-size: 19px; /* 设置当前样式属性。 */
  font-weight: 700; /* 设置当前样式属性。 */
  letter-spacing: 0.5px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.nav { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  gap: 6px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.nav-link { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 6px; /* 设置当前样式属性。 */
  padding: 8px 16px; /* 设置当前样式属性。 */
  border-radius: 8px; /* 设置当前样式属性。 */
  font-size: 15px; /* 设置当前样式属性。 */
  opacity: 0.85; /* 设置当前样式属性。 */
  transition: all 0.2s; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.nav-link:hover { /* 开始当前样式规则块。 */
  opacity: 1; /* 设置当前样式属性。 */
  background: rgba(255, 255, 255, 0.12); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.nav-link.active { /* 开始当前样式规则块。 */
  opacity: 1; /* 设置当前样式属性。 */
  background: rgba(255, 255, 255, 0.2); /* 设置当前样式属性。 */
  font-weight: 600; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.app-main { /* 开始当前样式规则块。 */
  flex: 1; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.app-footer { /* 开始当前样式规则块。 */
  text-align: center; /* 设置当前样式属性。 */
  padding: 20px; /* 设置当前样式属性。 */
  color: #94a3b8; /* 设置当前样式属性。 */
  font-size: 13px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.fade-enter-active, /* 声明当前样式规则。 */
.fade-leave-active { /* 开始当前样式规则块。 */
  transition: opacity 0.18s ease; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.fade-enter-from, /* 声明当前样式规则。 */
.fade-leave-to { /* 开始当前样式规则块。 */
  opacity: 0; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

/* ---- user area ---- */
.user-area { /* 开始当前样式规则块。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 12px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.user-greeting { /* 开始当前样式规则块。 */
  color: rgba(255, 255, 255, 0.9); /* 设置当前样式属性。 */
  font-size: 14px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.user-area .el-button { /* 开始当前样式规则块。 */
  color: rgba(255, 255, 255, 0.85); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-link { /* 开始当前样式规则块。 */
  font-size: 14px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
</style>
