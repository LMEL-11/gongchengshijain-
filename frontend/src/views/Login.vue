<!-- 文件功能：实现用户登录页面，提交账号密码并按角色跳转。 -->
<script setup>
import { reactive, ref } from 'vue' // 导入 { reactive, ref }，供当前前端模块渲染或交互逻辑使用。
import { useRouter } from 'vue-router' // 导入 { useRouter }，供当前前端模块渲染或交互逻辑使用。
import { ElMessage } from 'element-plus' // 导入 { ElMessage }，供当前前端模块渲染或交互逻辑使用。
import { Lock, User } from '@element-plus/icons-vue' // 导入 { Lock, User }，供当前前端模块渲染或交互逻辑使用。
import { useAuthStore } from '@/store/auth' // 导入 { useAuthStore }，供当前前端模块渲染或交互逻辑使用。

const router = useRouter() // 创建 router，用于保存页面状态、计算结果或接口参数。
const auth = useAuthStore() // 创建 auth，用于保存页面状态、计算结果或接口参数。

const formRef = ref(null) // 创建 formRef，用于保存页面状态、计算结果或接口参数。
const form = reactive({ // 创建 form，用于保存页面状态、计算结果或接口参数。
  username: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  password: '', // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。
const loading = ref(false) // 创建 loading，用于保存页面状态、计算结果或接口参数。

const rules = { // 创建 rules，用于保存页面状态、计算结果或接口参数。
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }], // 执行当前前端代码行，推动页面数据和交互流程继续运行。
} // 结束当前函数、对象、数组或组件配置块。

// 函数功能：校验登录表单并提交登录请求。
async function handleLogin() { // 定义 handleLogin 函数，处理页面交互、数据加载或状态同步。
  const valid = await formRef.value.validate().catch(() => false) // 创建 valid，用于保存页面状态、计算结果或接口参数。
  if (!valid) return // 根据当前页面状态或接口结果决定是否进入该分支。

  loading.value = true // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  try { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    await auth.login(form.username, form.password) // 等待异步接口或资源加载完成，再继续更新页面状态。
    ElMessage.success('登录成功') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    if (auth.isAdmin) { // 根据当前页面状态或接口结果决定是否进入该分支。
      router.push('/admin') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } else { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
      router.push('/') // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    } // 结束当前函数、对象、数组或组件配置块。
  } catch { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    // Error message already shown by request interceptor
  } finally { // 执行当前前端代码行，推动页面数据和交互流程继续运行。
    loading.value = false // 更新 loading.value 响应式状态，让页面展示与最新数据保持一致。
  } // 结束当前函数、对象、数组或组件配置块。
} // 结束当前函数、对象、数组或组件配置块。
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
.login-page { /* 定义当前选择器的样式作用域。 */
  min-height: 100vh; /* 设置元素最小高度。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #60a5fa 100%); /* 设置背景样式。 */
} /* 结束当前样式规则块。 */

.login-card-wrapper { /* 定义当前选择器的样式作用域。 */
  width: 420px; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */

.login-header { /* 定义当前选择器的样式作用域。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  margin-bottom: 28px; /* 设置元素底部外边距。 */
  color: #fff; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */

.login-header h1 { /* 定义当前选择器的样式作用域。 */
  margin: 8px 0 0; /* 设置元素外边距。 */
  font-size: 24px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
  letter-spacing: 1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */

.login-card { /* 定义当前选择器的样式作用域。 */
  border-radius: 12px; /* 设置圆角半径。 */
} /* 结束当前样式规则块。 */

.login-title { /* 定义当前选择器的样式作用域。 */
  text-align: center; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  margin: 0 0 24px; /* 设置元素外边距。 */
  font-size: 20px; /* 设置文字大小。 */
  color: #1e3a8a; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */

.login-btn { /* 定义当前选择器的样式作用域。 */
  width: 100%; /* 设置元素宽度。 */
} /* 结束当前样式规则块。 */

</style>
