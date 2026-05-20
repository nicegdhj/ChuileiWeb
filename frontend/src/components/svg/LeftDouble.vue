<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
    <!-- Icon from Remix Icon by Remix Design - https://github.com/Remix-Design/RemixIcon/blob/master/License -->
    <path
      fill="#000000"
      d="m4.836 12l6.207 6.207l1.414-1.414L7.664 12l4.793-4.793l-1.414-1.414zm5.65 0l6.207 6.207l1.414-1.414L13.314 12l4.793-4.793l-1.414-1.414z"
    />
  </svg>
</template>

<script setup lang="ts">
/**
 * 添加图标组件
 * 提供可自定义的宽度、高度、颜色和类名属性
 */
defineProps({
  // 宽度
  width: {
    type: String,
    default: '24'
  },
  // 高度
  height: {
    type: String,
    default: '24'
  },
  // 颜色
  color: {
    type: String,
    default: 'currentColor'
  },
  // 额外类名
  className: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
/* 可以添加一些全局样式 */
</style>
