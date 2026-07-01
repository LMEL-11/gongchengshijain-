<!-- 文件功能：封装数据大屏面板容器的标题、装饰和插槽布局。 -->
<script setup>
defineProps({ title: { type: String, default: '' } }) // 执行当前前端代码行，推动页面数据和交互流程继续运行。
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
.panel { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  display: flex; /* 设置元素布局模式。 */
  flex-direction: column; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-height: 0; /* 设置元素最小高度。 */
  padding: 12px 14px 10px; /* 设置元素内边距。 */
  background: linear-gradient(180deg, rgba(10, 32, 64, 0.55), rgba(6, 20, 42, 0.4)); /* 设置背景样式。 */
  border: 1px solid rgba(63, 224, 255, 0.18); /* 设置边框样式。 */
  border-radius: 4px; /* 设置圆角半径。 */
  backdrop-filter: blur(2px); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.panel-hd { /* 定义当前选择器的样式作用域。 */
  display: flex; /* 设置元素布局模式。 */
  align-items: center; /* 设置交叉轴对齐方式。 */
  gap: 8px; /* 设置子元素之间的间距。 */
  padding-bottom: 8px; /* 设置元素底部内边距。 */
  margin-bottom: 6px; /* 设置元素底部外边距。 */
  border-bottom: 1px solid rgba(63, 224, 255, 0.12); /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.hd-dot { /* 定义当前选择器的样式作用域。 */
  width: 8px; /* 设置元素宽度。 */
  height: 8px; /* 设置元素高度。 */
  border-radius: 50%; /* 设置圆角半径。 */
  background: #3fe0ff; /* 设置背景样式。 */
  box-shadow: 0 0 8px #3fe0ff; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.hd-title { /* 定义当前选择器的样式作用域。 */
  font-size: 16px; /* 设置文字大小。 */
  font-weight: 700; /* 设置文字粗细。 */
  letter-spacing: 1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  color: #d6f1ff; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.hd-extra { /* 定义当前选择器的样式作用域。 */
  margin-left: auto; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  font-size: 12px; /* 设置文字大小。 */
  color: #7fb0d8; /* 设置文字颜色。 */
} /* 结束当前样式规则块。 */
.panel-bd { /* 定义当前选择器的样式作用域。 */
  position: relative; /* 设置元素定位方式。 */
  flex: 1; /* 设置弹性布局占比。 */
  min-height: 0; /* 设置元素最小高度。 */
} /* 结束当前样式规则块。 */
.corner { /* 定义当前选择器的样式作用域。 */
  position: absolute; /* 设置元素定位方式。 */
  width: 10px; /* 设置元素宽度。 */
  height: 10px; /* 设置元素高度。 */
  border-color: #3fe0ff; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-style: solid; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-width: 0; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.corner.tl { /* 定义当前选择器的样式作用域。 */
  top: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-top-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-left-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.corner.tr { /* 定义当前选择器的样式作用域。 */
  top: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  right: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-top-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-right-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.corner.bl { /* 定义当前选择器的样式作用域。 */
  bottom: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  left: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-bottom-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-left-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
.corner.br { /* 定义当前选择器的样式作用域。 */
  bottom: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  right: -1px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-bottom-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
  border-right-width: 2px; /* 设置当前样式属性，控制页面布局或视觉展示。 */
} /* 结束当前样式规则块。 */
</style>
