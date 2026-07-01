<!-- 文件功能：展示仪表盘统计指标卡片及其图标、数值和说明。 -->
<script setup>
defineProps({ // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  label: { type: String, required: true }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  value: { type: [String, Number], default: '-' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  suffix: { type: String, default: '' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  icon: { type: String, default: 'DataLine' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
  color: { type: String, default: '#2563eb' }, // 执行当前前端代码行，推动页面数据和交互流程继续运行。
}) // 结束当前函数、对象、数组或组件配置块。
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
.stat-card { /* 定义当前选择器的样式作用域。 */
  background: #fff; /* 设置背景样式。 */
  border-radius: var(--card-radius); /* 设置圆角半径。 */
  box-shadow: var(--shadow); /* 设置当前样式属性，控制页面布局或视觉展示。 */
  padding: 20px; /* 设置元素内边距。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 16px; /* 设置子元素之间的间距。 */
} /* 结束当前样式规则块。 */
.icon { /* 定义当前选择器的样式作用域。 */
  width: 52px; /* 设置元素宽度。 */
  height: 52px; /* 设置元素高度。 */
  border-radius: 12px; /* 设置圆角半径。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  justify-content: center; /* 设置主轴内容分布方式。 */
  flex-shrink: 0; /* 控制弹性布局中元素是否收缩。 */
} /* 结束当前样式规则块。 */
.value { /* 定义当前选择器的样式作用域。 */
  font-size: 26px; /* 设置文字大小。 */
  font-weight: 800; /* 设置文字粗细。 */
  line-height: 1.1; /* 设置文本行高。 */
  color: #0f172a; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.suffix { /* 定义当前选择器的样式作用域。 */
  font-size: 14px; /* 设置文字大小。 */
  font-weight: 500; /* 设置文字粗细。 */
  color: #94a3b8; /* 设置文字颜色。 */
  margin-left: 4px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.label { /* 定义当前选择器的样式作用域。 */
  font-size: 13px; /* 设置文字大小。 */
  color: #94a3b8; /* 设置文字颜色。 */
  margin-top: 4px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
</style>
