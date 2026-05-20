<!-- src/pages/network-agent/components/xinLing/AiOptionCard.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores'

interface Props {
  content: Chat.AiOptionContent
}

const props = defineProps<Props>()
const chatStore = useChatStore()

const clickedIndex = ref<number | null>(null)

const handleClick = (option: Chat.AiOption, index: number) => {
  clickedIndex.value = index

  const title = option.title || option.tile || ''

  // action 为 1 或 "1" 时，发送问题给 AI
  if (option.action == 1) {
    // showQuestion: '0' 或 0 表示不展示问题
    const shouldHideQuestion =
      option.showQuestion === '0' || option.showQuestion === 0 || option.showQuestion === false

    chatStore.sendQuestion(title, [], undefined, {
      silent: shouldHideQuestion,
      dataParams: option.dataParams
    })
  }
}
</script>

<template>
  <div class="ai-option-card">
    <div class="option-content font-pingfang">{{ props.content.content }}</div>
    <div class="option-buttons">
      <div
        v-for="(option, index) in props.content.options"
        :key="index"
        class="option-btn font-pingfang"
        :class="{
          'option-btn--primary': option.selected === 1,
          'option-btn--default': option.selected !== 1,
          'option-btn--active': clickedIndex === index
        }"
        :disabled="clickedIndex !== null"
        @click="handleClick(option, index)"
      >
        {{ option.title || option.tile }}
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ai-option-card {
}

.option-content {
  font-size: 14px;
  line-height: 1.6;
  color: #000;
  margin-bottom: 12px;
  font-weight: 500;
}

.option-buttons {
  display: flex;
  gap: 0.5rem;
}

.option-btn {
  flex: 1;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
  border-radius: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  text-align: center;

  &--default {
    background-color: #e8f4ff;
    color: #469aff;
    border-color: #469aff;
  }

  &--primary {
    background-color: #1890ff;
    color: #fff;
    border-color: #1890ff;
  }

  &--disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  &--active {
    opacity: 1;
    box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.25);
  }
}
</style>
