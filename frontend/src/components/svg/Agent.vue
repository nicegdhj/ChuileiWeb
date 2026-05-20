<template>
  <svg
    viewBox="0 0 100 100"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    :class="className"
    :width="width"
    :height="height"
  >
    <path
      d="M50 5C50 5 58 35 90 50C58 65 50 95 50 95C50 95 42 65 10 50C42 35 50 5 50 5Z"
      :fill="mainColor"
    ></path>
    <path
      d="M82 15C82 15 85 22 92 25C85 28 82 35 82 35C82 35 79 28 72 25C79 22 82 15 82 15Z"
      :fill="accentColor"
      opacity="0.6"
    ></path>
    <path
      d="M18 65C18 65 21 72 28 75C21 78 18 85 18 85C18 85 15 78 8 75C15 72 18 65 18 65Z"
      :fill="accentColor"
      opacity="0.6"
    ></path>
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
