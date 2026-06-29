<!-- 文件功能：实现用户登录页面，提交账号密码并按角色跳转。 -->
<script setup>
import { reactive, ref } from 'vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useRouter } from 'vue-router' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { ElMessage } from 'element-plus' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { Lock, User } from '@element-plus/icons-vue' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。
import { useAuthStore } from '@/store/auth' // 引入组件、状态或工具函数，为当前页面的数据流和交互提供依赖。

const router = useRouter() // 保存router相关业务数据，作为后续计算、渲染或请求的输入。
const auth = useAuthStore() // 保存auth相关业务数据，作为后续计算、渲染或请求的输入。

const formRef = ref(null) // 创建formRef响应式状态，用于驱动页面渲染、表单输入或接口参数。
const form = reactive({ // 创建表单数据模型，用于驱动页面渲染、表单输入或接口参数。
  username: '', // 声明username字段，作为组件配置、请求参数或图表数据的一部分。
  password: '', // 声明password字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。
const loading = ref(false) // 创建加载状态，用于驱动页面渲染、表单输入或接口参数。

const rules = { // 保存rules相关业务数据，作为后续计算、渲染或请求的输入。
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }], // 声明username字段，作为组件配置、请求参数或图表数据的一部分。
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }], // 声明password字段，作为组件配置、请求参数或图表数据的一部分。
} // 完成当前参数、配置或响应式数据结构的组装。

// 函数功能：校验登录表单并提交登录请求。
async function handleLogin() { // 定义函数入口，负责接口请求、状态更新或页面交互处理。
  const valid = await formRef.value.validate().catch(() => false) // 保存valid相关业务数据，作为后续计算、渲染或请求的输入。
  if (!valid) return // 根据当前状态、接口结果或用户输入选择对应交互路径。

  loading.value = true // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  try { // 开始执行可能失败的接口请求或异步页面更新。
    await auth.login(form.username, form.password) // 等待异步接口或资源加载完成，再继续更新页面状态。
    ElMessage.success('登录成功') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    if (auth.isAdmin) { // 根据当前状态、接口结果或用户输入选择对应交互路径。
      router.push('/admin') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } else { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
      router.push('/') // 执行当前前端业务步骤，推动接口数据、状态和视图继续同步。
    } // 完成当前参数、配置或响应式数据结构的组装。
  } catch { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    // Error message already shown by request interceptor
  } finally { // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
    loading.value = false // 更新loading.value对应的页面状态，使界面展示与最新业务数据一致。
  } // 完成当前参数、配置或响应式数据结构的组装。
} // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <div class="login-page">
    <div class="login-card-wrapper">
      <div class="login-header">
        <el-icon :size="36"><OfficeBuilding /></el-icon>
        <h1>智慧房源探索平台</h1>
      </div>
      <el-card class="login-card" shadow="always">
        <h2 class="login-title">用户登录</h2>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.login-page { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  min-height: 100vh; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #60a5fa 100%); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-card-wrapper { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 420px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-header { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin-bottom: 28px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
  color: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-header h1 { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  margin: 8px 0 0; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 24px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 700; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  letter-spacing: 1px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-card { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  border-radius: 12px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-title { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  text-align: center; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  margin: 0 0 24px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  font-size: 20px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #1e3a8a; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */

.login-btn { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 100%; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */

</style>
