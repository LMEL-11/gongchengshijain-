<!-- 文件功能：实现用户登录页面，提交账号密码并按角色跳转。 -->
<script setup>
import { reactive, ref } from 'vue' // 导入本行所需的依赖。
import { useRouter } from 'vue-router' // 导入本行所需的依赖。
import { ElMessage } from 'element-plus' // 导入本行所需的依赖。
import { Lock, User } from '@element-plus/icons-vue' // 导入本行所需的依赖。
import { useAuthStore } from '@/store/auth' // 导入本行所需的依赖。

const router = useRouter() // 声明并初始化当前变量。
const auth = useAuthStore() // 声明并初始化当前变量。

const formRef = ref(null) // 声明并初始化当前变量。
const form = reactive({ // 声明并初始化当前变量。
  username: '', // 配置当前对象字段。
  password: '', // 配置当前对象字段。
}) // 执行本行前端逻辑。
const loading = ref(false) // 声明并初始化当前变量。

const rules = { // 声明并初始化当前变量。
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }], // 配置当前对象字段。
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }], // 配置当前对象字段。
} // 结束当前代码块或数据结构。

// 函数功能：校验登录表单并提交登录请求。
async function handleLogin() { // 声明当前函数入口。
  const valid = await formRef.value.validate().catch(() => false) // 声明并初始化当前变量。
  if (!valid) return // 根据条件判断是否执行分支。

  loading.value = true // 赋值或更新当前变量/状态。
  try { // 开始执行可能失败的逻辑。
    await auth.login(form.username, form.password) // 等待异步操作完成。
    ElMessage.success('登录成功') // 执行本行前端逻辑。
    if (auth.isAdmin) { // 根据条件判断是否执行分支。
      router.push('/admin') // 执行路由跳转或路由操作。
    } else { // 执行本行前端逻辑。
      router.push('/') // 执行路由跳转或路由操作。
    } // 结束当前代码块或数据结构。
  } catch { // 执行本行前端逻辑。
    // Error message already shown by request interceptor
  } finally { // 执行本行前端逻辑。
    loading.value = false // 赋值或更新当前变量/状态。
  } // 结束当前代码块或数据结构。
} // 结束当前代码块或数据结构。
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
.login-page { /* 开始当前样式规则块。 */
  min-height: 100vh; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: center; /* 设置当前样式属性。 */
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #60a5fa 100%); /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-card-wrapper { /* 开始当前样式规则块。 */
  width: 420px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-header { /* 开始当前样式规则块。 */
  text-align: center; /* 设置当前样式属性。 */
  margin-bottom: 28px; /* 设置当前样式属性。 */
  color: #fff; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-header h1 { /* 开始当前样式规则块。 */
  margin: 8px 0 0; /* 设置当前样式属性。 */
  font-size: 24px; /* 设置当前样式属性。 */
  font-weight: 700; /* 设置当前样式属性。 */
  letter-spacing: 1px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-card { /* 开始当前样式规则块。 */
  border-radius: 12px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-title { /* 开始当前样式规则块。 */
  text-align: center; /* 设置当前样式属性。 */
  margin: 0 0 24px; /* 设置当前样式属性。 */
  font-size: 20px; /* 设置当前样式属性。 */
  color: #1e3a8a; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

.login-btn { /* 开始当前样式规则块。 */
  width: 100%; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */

</style>
