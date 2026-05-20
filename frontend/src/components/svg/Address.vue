<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="w-3 h-3"
  >
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path>
    <circle cx="12" cy="10" r="3"></circle>
  </svg>
</template>

<script setup lang="ts">
/**
 * Agent图标组件
 * 提供可自定义的宽度、高度、颜色和类名属性
 */
defineProps({
  // 宽度
  width: {
    type: String,
    default: '100'
  },
  // 高度
  height: {
    type: String,
    default: '100'
  },
  // 主颜色
  mainColor: {
    type: String,
    default: '#2563EB'
  },
  //  accent 颜色
  accentColor: {
    type: String,
    default: '#3B82F6'
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
