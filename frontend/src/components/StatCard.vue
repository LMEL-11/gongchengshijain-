<!-- 文件功能：展示仪表盘统计指标卡片及其图标、数值和说明。 -->
<script setup>
defineProps({ // 执行本行前端逻辑。
  label: { type: String, required: true }, // 配置当前对象字段。
  value: { type: [String, Number], default: '-' }, // 配置当前对象字段。
  suffix: { type: String, default: '' }, // 配置当前对象字段。
  icon: { type: String, default: 'DataLine' }, // 配置当前对象字段。
  color: { type: String, default: '#2563eb' }, // 配置当前对象字段。
}) // 执行本行前端逻辑。
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
.stat-card { /* 开始当前样式规则块。 */
  background: #fff; /* 设置当前样式属性。 */
  border-radius: var(--card-radius); /* 设置当前样式属性。 */
  box-shadow: var(--shadow); /* 设置当前样式属性。 */
  padding: 20px; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  gap: 16px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.icon { /* 开始当前样式规则块。 */
  width: 52px; /* 设置当前样式属性。 */
  height: 52px; /* 设置当前样式属性。 */
  border-radius: 12px; /* 设置当前样式属性。 */
  display: flex; /* 设置当前样式属性。 */
  align-items: center; /* 设置当前样式属性。 */
  justify-content: center; /* 设置当前样式属性。 */
  flex-shrink: 0; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.value { /* 开始当前样式规则块。 */
  font-size: 26px; /* 设置当前样式属性。 */
  font-weight: 800; /* 设置当前样式属性。 */
  line-height: 1.1; /* 设置当前样式属性。 */
  color: #0f172a; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.suffix { /* 开始当前样式规则块。 */
  font-size: 14px; /* 设置当前样式属性。 */
  font-weight: 500; /* 设置当前样式属性。 */
  color: #94a3b8; /* 设置当前样式属性。 */
  margin-left: 4px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
.label { /* 开始当前样式规则块。 */
  font-size: 13px; /* 设置当前样式属性。 */
  color: #94a3b8; /* 设置当前样式属性。 */
  margin-top: 4px; /* 设置当前样式属性。 */
} /* 结束当前样式规则块。 */
</style>
