<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { generatePreviewTableData, type PreviewTableData } from '@/mock/previewTableData'
import { useChatStore } from '@/stores'

const chatStore = useChatStore()
const showPopup = ref(false)
const animating = ref(false)
const tableData = ref<PreviewTableData | null>(null)

const openPopup = (type?: string) => {
  // 优先使用流式响应中的真实 data-params 数据
  const realData = type ? chatStore.dataParams[type] : undefined
  if (realData) {
    tableData.value = {
      title: realData.name || '数据明细',
      columns: (realData.th || []).map(h => ({ key: h.en, label: h.zh })),
      rows: realData.td || []
    }
  } else {
    tableData.value = generatePreviewTableData(type)
  }
  showPopup.value = true
  setTimeout(() => {
    animating.value = true
  }, 10)
}

const closePopup = () => {
  animating.value = false
  setTimeout(() => {
    showPopup.value = false
    tableData.value = null
  }, 300)
}

// 点击弹窗背景（非表格区域）关闭
const handleBgClick = () => {
  closePopup()
}

const handleShowPreview = (e: Event) => {
  const customEvent = e as CustomEvent
  const type = customEvent.detail?.type || 'default'
  openPopup(type)
}

onMounted(() => {
  window.addEventListener('show-preview-popup', handleShowPreview)
})

onUnmounted(() => {
  window.removeEventListener('show-preview-popup', handleShowPreview)
})
</script>

<template>
  <view v-if="showPopup" class="preview-overlay fixed inset-0 z-50" @click="handleBgClick">
    <view
      class="preview-wrapper absolute inset-0 bg-white flex flex-col"
      :class="{ 'slide-up': animating }"
    >
      <!-- 标题栏 -->
      <view class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <text class="text-base font-medium text-gray-800">{{
          tableData?.title || '数据明细'
        }}</text>
        <view @click="closePopup" class="w-8 h-8 flex items-center justify-center">
          <text class="text-xl text-gray-500">&times;</text>
        </view>
      </view>

      <!-- 表格区域 -->
      <scroll-view scroll-y class="flex-1 p-4" v-if="tableData">
        <view class="overflow-x-auto" @click.stop>
          <table border="1" style="width: 100%; border-collapse: collapse; font-size: 14px">
            <tr style="background-color: #f3f4f6">
              <th
                v-for="col in tableData.columns"
                :key="col.key"
                style="
                  padding: 8px 12px;
                  text-align: left;
                  white-space: nowrap;
                  border: 1px solid #e5e7eb;
                  color: #374151;
                  font-weight: 500;
                "
              >
                {{ col.label }}
              </th>
            </tr>
            <tr v-for="(row, rowIndex) in tableData.rows" :key="rowIndex">
              <td
                v-for="col in tableData.columns"
                :key="col.key"
                style="
                  padding: 6px 12px;
                  white-space: nowrap;
                  border: 1px solid #e5e7eb;
                  color: #374151;
                "
              >
                {{ (row as any)[col.key] }}
              </td>
            </tr>
          </table>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.preview-overlay {
  background-color: rgba(0, 0, 0, 0.3);
  animation: fadeIn 0.2s ease-out;
}

.preview-wrapper {
  transform: translateY(100%);
  transition: transform 0.3s ease-out;

  &.slide-up {
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
