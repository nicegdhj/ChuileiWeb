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
    class="w-5 h-5"
  >
    <path d="m5 8 6 6"></path>
    <path d="m4 14 6-6 2-3"></path>
    <path d="M2 5h12"></path>
    <path d="M7 2h1"></path>
    <path d="m22 22-5-10-5 10"></path>
    <path d="M14 18h6"></path>
  </svg>
</template>

<script setup lang="ts">
/**
 * 菜单图标组件
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
