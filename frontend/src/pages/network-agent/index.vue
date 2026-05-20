<template>
  <view class="container1">
    <view class="app-layout">
      <Menu :isOpen="showMenu" :isPcOpen="showPcMenu" :isMobile="isMobile"></Menu>
      <view
        class="mask"
        :style="{ display: isMobile && showMenu ? 'block' : 'none' }"
        @click.stop="toggleMenu"
      ></view>

      <view class="right-panel">
        <ContentHeader
          :toggleMenu="toggleMenu"
          :togglePcMenu="togglePcMenu"
          :showPcMenu="showPcMenu"
          :isMobile="isMobile"
        ></ContentHeader>
        <WelcomeTitle v-if="!messages.length"></WelcomeTitle>
        <Dialogue v-else />

        <InputModule v-if="initReady" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import Menu from './components/menu.vue'
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useChatStore, useSessionStore } from '@/stores'
import WelcomeTitle from './components/welcomeTitle.vue'
import Dialogue from './components/dialogue.vue'
import ContentHeader from './components/contentHeader.vue'

import InputModule from './components/input-module.vue'

import { request } from '@/utils/http'

const showMenu = ref(false)
const toggleMenu = () => {
  showMenu.value = !showMenu.value
  console.log('菜单状态:', showMenu.value)
}
const showPcMenu = ref(true)
const togglePcMenu = () => {
  showPcMenu.value = !showPcMenu.value
}
const isMobile = ref(false)

const updateViewport = () => {
  isMobile.value = window.innerWidth <= 768
}

watch(
  () => [useSessionStore().currentSessionId],
  (n, o) => {
    console.log('变化了', n, o)
  }
)
const chatStore = useChatStore()
const messages = ref(chatStore.dialogList)

watch(
  () => [chatStore.dialogList],
  () => {
    messages.value = chatStore.dialogList
  }
)

// const useMember = useMemberStore()
const sessionStore = useSessionStore()

/** 是否已完成初始化（token 等），子组件依赖此时机再发请求，避免拿不到 token */
const initReady = ref(true)

onMounted(() => {
  updateViewport()
  window.addEventListener('resize', updateViewport)
  if (sessionStore.token) {
    initReady.value = true
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewport)
})
</script>

<style lang="scss" scoped>
html,
body,
uni-page-body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden; /* 防止页面滚动 */
}
.container1 {
  width: 100%;
  height: 100%;
  min-height: 100%;
  background-color: #ffffff;
  display: flex;
  overflow: hidden;

  .app-layout {
    display: flex;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background-color: #f8fafc;

      .chat-content {
        flex: 1;
        padding: 80rpx 48rpx;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;

        .welcome-section {
          text-align: center;
          max-width: 1200rpx;
          margin: 0 auto;

          .welcome-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 48rpx;
          }

          .welcome-title {
            display: flex;
            align-items: baseline;
            justify-content: center;
            gap: 16rpx;
            margin-bottom: 32rpx;

            .title-text {
              font-size: 48rpx;
              font-weight: 700;
              color: #1e293b;
            }

            .version-text {
              font-size: 24rpx;
              color: #6b7280;
              background-color: #f3f4f6;
              padding: 4rpx 12rpx;
              border-radius: 20rpx;
            }
          }

          .welcome-desc {
            font-size: 32rpx;
            color: #6b7280;
            line-height: 1.6;
            margin-bottom: 80rpx;
          }
        }
      }

      .function-buttons {
        display: flex;
        gap: 32rpx;
        margin-bottom: 80rpx;
        flex-wrap: wrap;
        justify-content: center;

        .function-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16rpx;
          padding: 32rpx 48rpx;
          background-color: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 24rpx;
          cursor: pointer;
          transition: all 0.2s ease;
          min-width: 240rpx;

          &:hover {
            background-color: #f9fafb;
            border-color: #d1d5db;
            transform: translateY(-2rpx);
            box-shadow: 0 8rpx 12rpx -2px rgba(0, 0, 0, 0.1);
          }

          .btn-icon {
            width: 56rpx;
            height: 56rpx;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .btn-text {
            font-size: 28rpx;
            font-weight: 500;
            color: #374151;
          }
        }
      }

      .input-section {
        padding: 40rpx 48rpx;
        background-color: #ffffff;
        border-top: 1px solid #e5e7eb;

        .input-container {
          display: flex;
          align-items: center;
          gap: 24rpx;
          background-color: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 56rpx;
          padding: 16rpx 24rpx;
          transition: all 0.2s ease;

          &:focus-within {
            border-color: #3b82f6;
            box-shadow: 0 0 0 6rpx rgba(59, 130, 246, 0.1);
          }

          .voice-btn,
          .add-btn,
          .send-btn {
            width: 64rpx;
            height: 64rpx;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            border-radius: 50%;
            transition: all 0.2s ease;

            &:hover {
              background-color: #f3f4f6;
            }
          }

          .send-btn {
            color: #3b82f6;
          }

          .message-input {
            flex: 1;
            border: none;
            background: transparent;
            font-size: 32rpx;
            color: #374151;
            outline: none;
            padding: 20rpx 0;

            &::placeholder {
              color: #9ca3af;
            }
          }
        }
      }

      .footer {
        padding: 24rpx 48rpx;
        text-align: center;
        background-color: #ffffff;
        border-top: 1px solid #e5e7eb;

        .footer-text {
          font-size: 24rpx;
          color: #9ca3af;
        }
      }
    }
  }
}
.mask {
  background-color: rgb(0 0 0 / 0.3);
  position: absolute;
  width: 100vw;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 50;
  display: none;
}

.svg-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #3b82f6;
}

@media (max-width: 768px) {
  .container1 {
    .app-layout {
      .right-panel {
        background: #fff;
        width: 100%;

        .function-buttons {
          gap: 24rpx;

          .function-btn {
            min-width: 200rpx;
            padding: 24rpx 32rpx;
          }
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .container1 {
    .app-layout {
      .right-panel {
        .chat-content {
          padding: 48rpx 32rpx;

          .welcome-section {
            .welcome-title {
              flex-direction: column;
              gap: 16rpx;

              .title-text {
                font-size: 40rpx;
              }
            }
          }
        }

        .function-buttons {
          flex-direction: column;
          width: 100%;

          .function-btn {
            min-width: auto;
            flex-direction: row;
            justify-content: flex-start;
          }
        }

        .input-section {
          padding: 24rpx 32rpx;
        }

        .footer {
          padding: 16rpx 32rpx;
        }
      }
    }
  }
}
</style>
