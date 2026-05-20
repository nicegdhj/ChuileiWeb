<!-- src/pages/network-agent/components/dialogue.vue -->
<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import MessageItem from './Message/message_item.vue'
import SwimlaneChartPopup from './xinLing/SwimlaneChartPopup.vue'
import { useChatStore } from '@/stores'

const chatStore = useChatStore()
const messages = ref<Chat.ChatItem[]>(chatStore.dialogList)
const dialogueContainer = ref<HTMLElement>()
const isAtBottom = ref(true) // 标记是否在底部

// 泳道图弹窗：监听 store 中的 xinLing 数据
const showSwimlaneChart = ref(false)
const swimlaneChartRawData = ref<any>(null)

watch(
  () => chatStore.swimlaneChartData,
  (val) => {
    if (val) {
      swimlaneChartRawData.value = val
      showSwimlaneChart.value = true
    }
  }
)

const closeSwimlaneChart = () => {
  showSwimlaneChart.value = false
  swimlaneChartRawData.value = null
  chatStore.clearSwimlaneChart()
}

watch(
  () => [chatStore.dialogList],
  () => {
    messages.value = chatStore.dialogList
  }
)

// 滚动到底部的函数
const scrollToBottom = async () => {
  await nextTick()
  if (dialogueContainer.value && isAtBottom.value) {
    dialogueContainer.value.scrollTop = dialogueContainer.value.scrollHeight
  }
}

// 检测是否在底部
const checkIsAtBottom = () => {
  if (!dialogueContainer.value) return
  const { scrollTop, scrollHeight, clientHeight } = dialogueContainer.value
  // 容忍误差：距离底部小于 10px 视为在底部
  isAtBottom.value = scrollTop + clientHeight >= scrollHeight - 10
}
// 监听滚动事件
const handleScroll = () => {
  checkIsAtBottom()
}

// 监听消息变化，自动滚动到底部
watch(
  () => messages.value.length,
  () => {
    scrollToBottom()
  }
)

// 监听消息内容变化，处理流式输出时的滚动
watch(
  () => messages.value.map(msg => msg.content),
  () => {
    scrollToBottom()
  },
  { deep: true }
)

onMounted(() => {
  // 初始滚动到底部
  scrollToBottom()
  // 添加滚动监听
  if (dialogueContainer.value) {
    dialogueContainer.value.addEventListener('scroll', handleScroll)
  }
})

// 组件卸载时移除监听
onUnmounted(() => {
  if (dialogueContainer.value) {
    dialogueContainer.value.removeEventListener('scroll', handleScroll)
  }
})
</script>

<template>
  <div ref="dialogueContainer" class="dialogue-container custom-scrollbar">
    <div class="dialogue-content">
      <div v-for="(message, index) in messages" :key="message.id" class="message-wrapper">
        <MessageItem :message="message" />
      </div>

      <!-- 滚动到底部的空白区域 -->
      <div class="scroll-bottom-spacer"></div>
    </div>

    <!-- 泳道图弹窗（由 xinLing 类型 SSE 数据触发） -->
    <SwimlaneChartPopup
      :visible="showSwimlaneChart"
      :chartData="swimlaneChartRawData"
      @close="closeSwimlaneChart"
    />
  </div>
</template>

<style lang="scss" scoped>
.dialogue-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  .dialogue-content {
    max-width: 56rem;
    margin: 0 auto;
    padding: 1rem 0;
    width: 100%;
    flex: 1;
  }
}

.scroll-bottom-spacer {
  height: 1rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
@media (min-width: 768px) {
  .dialogue-container {
    padding: 1rem 3rem 2rem 3rem;
  }
}
</style>
