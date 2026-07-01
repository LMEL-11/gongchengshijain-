<!-- 文件功能：定义应用根布局、顶部导航、登录状态展示和页面切换容器。 -->
<script setup>
import { computed } from 'vue' // 导入 { computed }，供当前前端模块渲染或交互逻辑使用。
import { useRoute, useRouter } from 'vue-router' // 导入 { useRoute, useRouter }，供当前前端模块渲染或交互逻辑使用。
import { useAuthStore } from '@/store/auth' // 导入 { useAuthStore }，供当前前端模块渲染或交互逻辑使用。

const route = useRoute() // 创建 route，用于保存页面状态、计算结果或接口参数。
const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。
const auth = useAuthStore() // 创建 auth，用于保存页面状态、计算结果或接口参数。

const navItems = [ // 创建 navItems，用于保存页面状态、计算结果或接口参数。
  { name: 'screen', label: '数据大屏', icon: 'DataBoard' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { name: 'dashboard', label: '房源总览', icon: 'HomeFilled' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { name: 'explore', label: '房源探索', icon: 'Search' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  { name: 'analysis', label: '数据分析', icon: 'TrendCharts' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
] // 结束当前函数、对象、数组或组件配置块。

// 函数功能：根据登录用户角色计算管理员导航项。
const adminNavItem = computed(() => { // 创建 adminNavItem，用于保存页面状态、计算结果或接口参数。
  if (!auth.isAdmin) return [] // 根据当前页面状态或接口结果决定是否进入该分支。
  return [{ name: 'admin', label: '管理后台', icon: 'Setting' }] // 返回整理后的数据、组件配置或渲染结果。
}) // 结束当前函数、对象、数组或组件配置块。

// 大屏页、登录页为全屏布局，隐藏通用页头/页脚。
// 函数功能：判断当前页面是否使用无导航的全屏布局。
const bare = computed(() => route.name === 'screen' || route.name === 'login') // 创建 bare，用于保存页面状态、计算结果或接口参数。
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
.app-shell { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  min-height: 100%; /* 设置元素最小高度。 */
} /* 结束当前样式规则块。 */

.app-header { /* 定义当前选择器的样式作用域。 */
  background: linear-gradient(90deg, #1e3a8a, #2563eb); /* 设置背景样式。 */
  color: #fff; /* 设置文字颜色。 */
  box-shadow: 0 2px 12px rgba(30, 58, 138, 0.25); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  position: sticky; /* 设置元素定位方式。 */
  top: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  z-index: 100; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

.header-inner { /* 定义当前选择器的样式作用域。 */
  max-width: 1280px; /* 设置元素最大宽度。 */
  margin: 0 auto; /* 设置元素外边距。 */
  height: 60px; /* 设置元素高度。 */
  padding: 0 20px; /* 设置元素内边距。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: space-between; /* 设置主轴内容分布方式。 */
} /* 结束当前样式规则块。 */

.brand { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 10px; /* 设置子元素之间的间距。 */
  font-size: 19px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
  letter-spacing: 0.5px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

.nav { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  gap: 6px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */

.nav-link { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 6px; /* 设置子元素之间的间距。 */
  padding: 8px 16px; /* 设置元素内边距。 */
  border-radius: 8px; /* 设置圆角半径。 */
  font-size: 15px; /* 设置文字大小。 */
  opacity: 0.85; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  transition: all 0.2s; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

.nav-link:hover { /* 定义当前选择器的样式作用域。 */
  opacity: 1; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(255, 255, 255, 0.12); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */

.nav-link.active { /* 定义当前选择器的样式作用域。 */
  opacity: 1; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  background: rgba(255, 255, 255, 0.2); /* 设置背景样式。 */
  font-weight: 600; /* 设置文字粗细。 */
} /* 结束当前样式规则块。 */

.app-main { /* 定义当前选择器的样式作用域。 */
  flex: 1; /* 设置弹性布局占比。 */
} /* 结束当前样式规则块。 */

.app-footer { /* 定义当前选择器的样式作用域。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding: 20px; /* 设置元素内边距。 */
  color: #94a3b8; /* 设置文字颜色。 */
  font-size: 13px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */

.fade-enter-active, /* 设置当前样式属性，控制页面布局或视觉展示。 */
.fade-leave-active { /* 定义当前选择器的样式作用域。 */
  transition: opacity 0.18s ease; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

.fade-enter-from, /* 设置当前样式属性，控制页面布局或视觉展示。 */
.fade-leave-to { /* 定义当前选择器的样式作用域。 */
  opacity: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

/* ---- user area ---- */
.user-area { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 12px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */

.user-greeting { /* 定义当前选择器的样式作用域。 */
  color: rgba(255, 255, 255, 0.9); /* 设置文字颜色。 */
  font-size: 14px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */

.user-area .el-button { /* 定义当前选择器的样式作用域。 */
  color: rgba(255, 255, 255, 0.85); /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */

.login-link { /* 定义当前选择器的样式作用域。 */
  font-size: 14px; /* 设置文字大小。 */
} /* 结束当前样式规则块。 */
</style>
