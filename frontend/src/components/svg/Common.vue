<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="width"
    :height="height"
    viewBox="0 0 24 24"
    fill="none"
    :stroke="color"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    :class="className"
  >
    <rect width="16" height="16" x="4" y="4" rx="2"></rect>
    <rect width="6" height="6" x="9" y="9" rx="1"></rect>
    <path d="M15 2v2"></path>
    <path d="M15 20v2"></path>
    <path d="M2 15h2"></path>
    <path d="M2 9h2"></path>
    <path d="M20 15h2"></path>
    <path d="M20 9h2"></path>
    <path d="M9 2v2"></path>
    <path d="M9 20v2"></path>
  </svg>
</template>

<script setup lang="ts">
/**
 * 通用图标组件
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
