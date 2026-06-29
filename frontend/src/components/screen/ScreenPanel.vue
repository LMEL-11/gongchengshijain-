<!-- 文件功能：封装数据大屏面板容器的标题、装饰和插槽布局。 -->
<script setup>
defineProps({ title: { type: String, default: '' } }) // 逐行注释：执行本行前端逻辑。
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
.panel { /* 逐行注释：开始当前样式规则块。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  flex-direction: column; /* 逐行注释：设置当前样式属性。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
  padding: 12px 14px 10px; /* 逐行注释：设置当前样式属性。 */
  background: linear-gradient(180deg, rgba(10, 32, 64, 0.55), rgba(6, 20, 42, 0.4)); /* 逐行注释：设置当前样式属性。 */
  border: 1px solid rgba(63, 224, 255, 0.18); /* 逐行注释：设置当前样式属性。 */
  border-radius: 4px; /* 逐行注释：设置当前样式属性。 */
  backdrop-filter: blur(2px); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.panel-hd { /* 逐行注释：开始当前样式规则块。 */
  display: flex; /* 逐行注释：设置当前样式属性。 */
  align-items: center; /* 逐行注释：设置当前样式属性。 */
  gap: 8px; /* 逐行注释：设置当前样式属性。 */
  padding-bottom: 8px; /* 逐行注释：设置当前样式属性。 */
  margin-bottom: 6px; /* 逐行注释：设置当前样式属性。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.12); /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hd-dot { /* 逐行注释：开始当前样式规则块。 */
  width: 8px; /* 逐行注释：设置当前样式属性。 */
  height: 8px; /* 逐行注释：设置当前样式属性。 */
  border-radius: 50%; /* 逐行注释：设置当前样式属性。 */
  background: #3fe0ff; /* 逐行注释：设置当前样式属性。 */
  box-shadow: 0 0 8px #3fe0ff; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hd-title { /* 逐行注释：开始当前样式规则块。 */
  font-size: 16px; /* 逐行注释：设置当前样式属性。 */
  font-weight: 700; /* 逐行注释：设置当前样式属性。 */
  letter-spacing: 1px; /* 逐行注释：设置当前样式属性。 */
  color: #d6f1ff; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.hd-extra { /* 逐行注释：开始当前样式规则块。 */
  margin-left: auto; /* 逐行注释：设置当前样式属性。 */
  font-size: 12px; /* 逐行注释：设置当前样式属性。 */
  color: #7fb0d8; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.panel-bd { /* 逐行注释：开始当前样式规则块。 */
  position: relative; /* 逐行注释：设置当前样式属性。 */
  flex: 1; /* 逐行注释：设置当前样式属性。 */
  min-height: 0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.corner { /* 逐行注释：开始当前样式规则块。 */
  position: absolute; /* 逐行注释：设置当前样式属性。 */
  width: 10px; /* 逐行注释：设置当前样式属性。 */
  height: 10px; /* 逐行注释：设置当前样式属性。 */
  border-color: #3fe0ff; /* 逐行注释：设置当前样式属性。 */
  border-style: solid; /* 逐行注释：设置当前样式属性。 */
  border-width: 0; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.corner.tl { /* 逐行注释：开始当前样式规则块。 */
  top: -1px; /* 逐行注释：设置当前样式属性。 */
  left: -1px; /* 逐行注释：设置当前样式属性。 */
  border-top-width: 2px; /* 逐行注释：设置当前样式属性。 */
  border-left-width: 2px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.corner.tr { /* 逐行注释：开始当前样式规则块。 */
  top: -1px; /* 逐行注释：设置当前样式属性。 */
  right: -1px; /* 逐行注释：设置当前样式属性。 */
  border-top-width: 2px; /* 逐行注释：设置当前样式属性。 */
  border-right-width: 2px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.corner.bl { /* 逐行注释：开始当前样式规则块。 */
  bottom: -1px; /* 逐行注释：设置当前样式属性。 */
  left: -1px; /* 逐行注释：设置当前样式属性。 */
  border-bottom-width: 2px; /* 逐行注释：设置当前样式属性。 */
  border-left-width: 2px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
.corner.br { /* 逐行注释：开始当前样式规则块。 */
  bottom: -1px; /* 逐行注释：设置当前样式属性。 */
  right: -1px; /* 逐行注释：设置当前样式属性。 */
  border-bottom-width: 2px; /* 逐行注释：设置当前样式属性。 */
  border-right-width: 2px; /* 逐行注释：设置当前样式属性。 */
} /* 逐行注释：结束当前样式规则块。 */
</style>
