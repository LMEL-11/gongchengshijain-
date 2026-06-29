<!-- 文件功能：定义应用根布局、顶部导航、登录状态展示和页面切换容器。 -->
<script setup>
import { computed } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRoute, useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAuthStore } from '@/store/auth' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const route = useRoute() // 保存route相关业务数据，作为后续计算、渲染或请求的输入。
const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。
const auth = useAuthStore() // 保存auth相关业务数据，作为后续计算、渲染或请求的输入。

const navItems = [ // 保存navItems相关业务数据，作为后续计算、渲染或请求的输入。
  { name: 'screen', label: '数据大屏', icon: 'DataBoard' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { name: 'dashboard', label: '房源总览', icon: 'HomeFilled' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { name: 'explore', label: '房源探索', icon: 'Search' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
  { name: 'analysis', label: '数据分析', icon: 'TrendCharts' }, // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
] // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：根据登录用户角色计算管理员导航项。
const adminNavItem = computed(() => { // 基于响应式数据派生adminNavItem，用于保持界面展示与数据状态同步。
  if (!auth.isAdmin) return [] // 根据当前状态、接口结果或用户输入选择对应交互路径。
  return [{ name: 'admin', label: '管理后台', icon: 'Setting' }] // 返回整理后的数据或视图状态，供调用方继续渲染或处理。
}) // 完成当前参数、配置或响应式数据结构的组装。

// 大屏页、登录页为全屏布局，隐藏通用页头/页脚。
// 函数功能：判断当前页面是否使用无导航的全屏布局。
const bare = computed(() => route.name === 'screen' || route.name === 'login') // 基于响应式数据派生bare，用于保持界面展示与数据状态同步。
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
.app-shell { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-direction: column; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  min-height: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.app-header { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: linear-gradient(90deg, #1e3a8a, #2563eb); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  color: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  box-shadow: 0 2px 12px rgba(30, 58, 138, 0.25); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  position: sticky; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  top: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  z-index: 100; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.header-inner { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  max-width: 1280px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  margin: 0 auto; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 60px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  padding: 0 20px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: space-between; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.brand { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 10px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 19px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  letter-spacing: 0.5px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.nav { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.nav-link { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 6px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  padding: 8px 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-radius: 8px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 15px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  opacity: 0.85; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  transition: all 0.2s; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.nav-link:hover { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  opacity: 1; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(255, 255, 255, 0.12); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.nav-link.active { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  opacity: 1; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  background: rgba(255, 255, 255, 0.2); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-weight: 600; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.app-main { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  flex: 1; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.app-footer { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  padding: 20px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  color: #94a3b8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.fade-enter-active, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
.fade-leave-active { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  transition: opacity 0.18s ease; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.fade-enter-from, /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
.fade-leave-to { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  opacity: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

/* ---- user area ---- */
.user-area { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 12px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.user-greeting { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: rgba(255, 255, 255, 0.9); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  font-size: 14px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.user-area .el-button { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  color: rgba(255, 255, 255, 0.85); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-link { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 14px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
