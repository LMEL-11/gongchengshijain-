<!-- 文件功能：展示仪表盘统计指标卡片及其图标、数值和说明。 -->
<script setup>
defineProps({ // 展开当前交互逻辑或数据结构，继续组织页面所需数据。
  label: { type: String, required: true }, // 声明label字段，作为组件配置、请求参数或图表数据的一部分。
  value: { type: [String, Number], default: '-' }, // 声明value字段，作为组件配置、请求参数或图表数据的一部分。
  suffix: { type: String, default: '' }, // 声明suffix字段，作为组件配置、请求参数或图表数据的一部分。
  icon: { type: String, default: 'DataLine' }, // 声明icon字段，作为组件配置、请求参数或图表数据的一部分。
  color: { type: String, default: '#2563eb' }, // 声明color字段，作为组件配置、请求参数或图表数据的一部分。
}) // 完成当前参数、配置或响应式数据结构的组装。
</script>

<template>
  <div class="stat-card">
    <div class="icon" :style="{ background: color + '1a', color }">
      <el-icon :size="26"><component :is="icon" /></el-icon>
    </div>
    <div class="body">
      <div class="value">
        {{ value }}<span class="suffix">{{ suffix }}</span>
      </div>
      <div class="label">{{ label }}</div>
    </div>
  </div>
</template>

<style scoped>
.stat-card { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  background: #fff; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  border-radius: var(--card-radius); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  box-shadow: var(--shadow); /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  padding: 20px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  gap: 16px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.icon { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  width: 52px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  height: 52px; /* 设置尺寸与间距，保证信息展示区域稳定且便于阅读。 */
  border-radius: 12px; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  display: flex; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  align-items: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  justify-content: center; /* 控制页面元素的布局方式，保证数据卡片、表格或地图区域正确排列。 */
  flex-shrink: 0; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.value { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 26px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 800; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  line-height: 1.1; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #0f172a; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.suffix { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 14px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  font-weight: 500; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #94a3b8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  margin-left: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
.label { /* 定义该界面区域的样式作用域，控制组件布局和视觉层级。 */
  font-size: 13px; /* 控制文字展示效果，保证指标、标签和表格内容清晰可读。 */
  color: #94a3b8; /* 设置视觉层级和状态反馈，帮助用户区分数据区域和操作区域。 */
  margin-top: 4px; /* 配置当前界面样式，服务于房源数据展示和交互可读性。 */
} /* 收束该样式块，使后续选择器保持独立。 */
</style>
