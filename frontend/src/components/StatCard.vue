<!-- 文件功能：展示仪表盘统计指标卡片及其图标、数值和说明。 -->
<script setup>
defineProps({ // 逐行注释：执行本行前端逻辑。
  label: { type: String, required: true }, // 逐行注释：配置当前对象字段。
  value: { type: [String, Number], default: '-' }, // 逐行注释：配置当前对象字段。
  suffix: { type: String, default: '' }, // 逐行注释：配置当前对象字段。
  icon: { type: String, default: 'DataLine' }, // 逐行注释：配置当前对象字段。
  color: { type: String, default: '#2563eb' }, // 逐行注释：配置当前对象字段。
}) // 逐行注释：执行本行前端逻辑。
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
.stat-card { /* 逐行注释：开始当前样式规则块。 */
  background: #fff; /* 逐行注释：设置当前样式属性。 */
  border-radius: var(--card-radius); /* 逐行注释：设置当前样式属性。 */
  box-shadow: var(--shadow); /* 逐行注释：设置当前样式属性。 */
  padding: 20px; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 16px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.icon { /* 逐行注释：开始当前样式规则块。 */
  width: 52px; /* 逐行注释：设置当前样式属性。 */
  height: 52px; /* 逐行注释：设置当前样式属性。 */
  border-radius: 12px; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  justify-content: center; /* 逐行注释：设置当前样式属性。 */
  flex-shrink: 0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.value { /* 逐行注释：开始当前样式规则块。 */
  font-size: 26px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 800; /* 逐行注释：设置当前样式属性。 */
  line-height: 1.1; /* 逐行注释：设置当前样式属性。 */
  color: #0f172a; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.suffix { /* 逐行注释：开始当前样式规则块。 */
  font-size: 14px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 500; /* 逐行注释：设置当前样式属性。 */
  color: #94a3b8; /* 逐行注释：设置当前样式属性。 */
  margin-left: 4px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.label { /* 逐行注释：开始当前样式规则块。 */
  font-size: 13px; /* 逐行注释：设置当前样式属性。 */
  color: #94a3b8; /* 逐行注释：设置当前样式属性。 */
  margin-top: 4px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
