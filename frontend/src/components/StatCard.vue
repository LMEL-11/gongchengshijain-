<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '-' },
  suffix: { type: String, default: '' },
  icon: { type: String, default: 'DataLine' },
  color: { type: String, default: '#2563eb' },
})
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
.stat-card {
  background: #fff;
  border-radius: var(--card-radius);
  box-shadow: var(--shadow);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.value {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.1;
  color: #0f172a;
}
.suffix {
  font-size: 14px;
  font-weight: 500;
  color: #94a3b8;
  margin-left: 4px;
}
.label {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
}
</style>
