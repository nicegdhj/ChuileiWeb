<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
    <!-- Icon from Remix Icon by Remix Design - https://github.com/Remix-Design/RemixIcon/blob/master/License -->
    <path
      fill="#000000"
      d="m19.164 12l-6.207-6.207l-1.414 1.414L16.336 12l-4.793 4.793l1.414 1.414zm-5.65 0L7.307 5.793L5.893 7.207L10.686 12l-4.793 4.793l1.414 1.414z"
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
