<script setup lang="ts">
import { computed } from 'vue'

interface FileInfo {
  name: string
  path: string
  size: number
}

const props = defineProps<{
  images: string[]
  files?: FileInfo[]
}>()

const emit = defineEmits<{
  (e: 'remove', index: number): void
  (e: 'remove-file', index: number): void
}>()

const hasPreview = computed(() => props.images.length > 0 || (props.files && props.files.length > 0))

/** 根据文件名获取扩展名标签 */
const getFileExt = (name: string) => {
  const ext = name.split('.').pop()?.toUpperCase() || 'FILE'
  return ext
}

/** 格式化文件大小 */
const formatSize = (size: number) => {
  if (size < 1024) return size + 'B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + 'KB'
  return (size / (1024 * 1024)).toFixed(1) + 'MB'
}
</script>

<template>
  <view class="image-preview-area" :class="{ 'preview-visible': hasPreview }">
    <scroll-view scroll-x class="preview-scroll">
      <view class="preview-list">
        <!-- 文件预览 -->
        <view v-for="(file, fIndex) in files" :key="'f'+fIndex" class="preview-item file-item" @click="emit('remove-file', fIndex)">
          <view class="file-icon-badge">
            <text class="file-ext-text">{{ getFileExt(file.name) }}</text>
          </view>
          <view class="file-info">
            <text class="file-name-text">{{ file.name }}</text>
            <text class="file-size-text">{{ formatSize(file.size) }}</text>
          </view>
          <view class="delete-badge">
            <text class="delete-text">×</text>
          </view>
        </view>
        <!-- 图片预览 -->
        <view
          v-for="(img, index) in images"
          :key="index"
          class="preview-item"
          @click="emit('remove', index)"
        >
          <image :src="img" class="preview-image" mode="aspectFill" />
          <view class="delete-badge">
            <text class="delete-text">×</text>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style lang="scss" scoped>
.image-preview-area {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, opacity 0.25s ease, padding 0.3s ease;
  padding: 0 24rpx;

  &.preview-visible {
    max-height: 200rpx;
    opacity: 1;
    padding: 16rpx 24rpx;
  }

  .preview-scroll {
    width: 100%;
    white-space: nowrap;
  }

  .preview-list {
    display: flex;
    gap: 16rpx;
  }

  .preview-item {
    position: relative;
    flex-shrink: 0;
    width: 120rpx;
    height: 120rpx;
    border-radius: 16rpx;
    overflow: hidden;

    .preview-image {
      width: 100%;
      height: 100%;
    }

    .delete-badge {
      position: absolute;
      top: 0;
      right: 0;
      width: 36rpx;
      height: 36rpx;
      background-color: rgba(0, 0, 0, 0.5);
      border-radius: 0 16rpx 0 12rpx;
      display: flex;
      align-items: center;
      justify-content: center;

      .delete-text {
        color: #fff;
        font-size: 24rpx;
        line-height: 1;
      }
    }
  }

  .file-item {
    width: auto;
    min-width: 200rpx;
    max-width: 320rpx;
    height: 120rpx;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 12rpx;
    padding: 16rpx;
    overflow: hidden;

    .file-icon-badge {
      flex-shrink: 0;
      width: 56rpx;
      height: 56rpx;
      border-radius: 12rpx;
      background-color: #3b82f6;
      display: flex;
      align-items: center;
      justify-content: center;

      .file-ext-text {
        color: #fff;
        font-size: 20rpx;
        font-weight: 600;
      }
    }

    .file-info {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 4rpx;
    }

    .file-name-text {
      flex: 1;
      font-size: 22rpx;
      color: #334155;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      min-width: 0;
    }

    .file-size-text {
      flex-shrink: 0;
      font-size: 20rpx;
      color: #94a3b8;
    }
  }
}
</style>
