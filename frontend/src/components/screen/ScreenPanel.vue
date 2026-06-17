<script setup>
defineProps({ title: { type: String, default: '' } })
</script>

<template>
  <section class="panel">
    <header class="panel-hd">
      <span class="hd-dot"></span>
      <span class="hd-title">{{ title }}</span>
      <span class="hd-extra"><slot name="extra" /></span>
    </header>
    <div class="panel-bd">
      <slot />
    </div>
    <i class="corner tl"></i>
    <i class="corner tr"></i>
    <i class="corner bl"></i>
    <i class="corner br"></i>
  </section>
</template>

<style scoped>
.panel {
  position: relative;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  padding: 12px 14px 10px;
  background: linear-gradient(180deg, rgba(10, 32, 64, 0.55), rgba(6, 20, 42, 0.4));
  border: 1px solid rgba(63, 224, 255, 0.18);
  border-radius: 4px;
  backdrop-filter: blur(2px);
}
.panel-hd {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  margin-bottom: 6px;
  border-bottom: 1px solid rgba(63, 224, 255, 0.12);
}
.hd-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3fe0ff;
  box-shadow: 0 0 8px #3fe0ff;
}
.hd-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #d6f1ff;
}
.hd-extra {
  margin-left: auto;
  font-size: 12px;
  color: #7fb0d8;
}
.panel-bd {
  position: relative;
  flex: 1;
  min-height: 0;
}
.corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border-color: #3fe0ff;
  border-style: solid;
  border-width: 0;
}
.corner.tl {
  top: -1px;
  left: -1px;
  border-top-width: 2px;
  border-left-width: 2px;
}
.corner.tr {
  top: -1px;
  right: -1px;
  border-top-width: 2px;
  border-right-width: 2px;
}
.corner.bl {
  bottom: -1px;
  left: -1px;
  border-bottom-width: 2px;
  border-left-width: 2px;
}
.corner.br {
  bottom: -1px;
  right: -1px;
  border-bottom-width: 2px;
  border-right-width: 2px;
}
</style>
