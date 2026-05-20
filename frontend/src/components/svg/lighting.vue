<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="w-3 h-3"
    :class="props.endNode ? 'fill-green-500 text-green-500' : 'fill-blue-500 text-blue-500'"
  >
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
  </svg>
</template>

<script setup lang="ts">
/**
 * 通用图标组件
 * 提供可自定义的宽度、高度、颜色和类名属性
 */
const props = defineProps({
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
  },
  endNode: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
/* 可以添加一些全局样式 */
</style>
