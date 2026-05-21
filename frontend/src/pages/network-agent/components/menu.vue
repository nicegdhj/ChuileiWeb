<script setup lang="ts">
import MenuIcon from '@/components/svg/Menu.vue'
import Setting from '@/components/svg/Setting.vue'
import Folder from '@/components/svg/Folder.vue'
import Agent from '@/components/svg/Agent.vue'
import Add from '@/components/svg/Add.vue'
import Dialogue from '@/components/svg/Dialogue.vue'
import { computed, watch, ref } from 'vue'
import { useChatStore, useSessionStore } from '@/stores'
import { v4 as uuidv4 } from 'uuid'
import dayjs from 'dayjs'

const sessionStore = useSessionStore()
const chatStore = useChatStore()
interface Props {
  isOpen?: boolean
  isPcOpen?: boolean
  isMobile?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  isOpen: false
})
interface Conversation {
  sessionId?: string
  title: string
  latestCreateTime?: string
}

const conversationList = ref<Conversation[]>([])

watch(
  () => [chatStore.sessionList, sessionStore.currentSessionId],
  (n, o) => {
    let index = chatStore.sessionList.findIndex(v => v.sessionId == sessionStore.currentSessionId)
    if (index == -1 && !chatStore.sessionList.length) {
      conversationList.value = [
        {
          sessionId: sessionStore.currentSessionId,
          title: '新对话',
          latestCreateTime: dayjs().format()
        }
      ]
    } else {
      conversationList.value = chatStore.sessionList
    }
  },
  { immediate: true }
)

// [{
//   sessionId: '1',
//   title: '2025年Q3全省5G网络覆盖分析报告',
//   time: '今天 14:30'
// },
// {
//   sessionId: '2',
//   title: '关于防范电信诈骗治理工作的汇报...',
//   time: '昨天 16:45'
// },
// {
//   sessionId: '3',
//   title: '核心网容灾演练方案（拟定稿）',
//   time: '昨天 10:15'
// },
// {
//   sessionId: '4',
//   title: '省内重要客户专线保障情况通报',
//   time: '前天 09:30'
// },
// {
//   sessionId: '5',
//   title: '本月网络安全攻防演练复盘',
//   time: '3天前'
// },
// {
//   sessionId: '6',
//   title: '各分市公司网络满意度KPI排名',
//   time: '一周前'
// }]

function handleNewChat() {
  let id = uuidv4()
  sessionStore.changeSelectedSessionId(id)
  chatStore.cleanDialog()
  if (chatStore.sessionList[0].title != '新对话') {
    chatStore.sessionList.unshift({
      sessionId: id,
      title: '新对话',
      latestCreateTime: dayjs().format()
    })
  }

  // console.log('新建对话')
}

async function handleDeleteConversation(item: Conversation) {
  if (!item.sessionId) return
  await chatStore.deleteSession(item.sessionId)
  conversationList.value = chatStore.sessionList
}

function handleSelectConversation(item: Conversation) {
  console.log('🚀 ~ handleSelectConversation ~ item:', item.sessionId)
  console.log(
    '🚀 ~ handleSelectConversation ~ sessionStore.currentSessionId:',
    sessionStore.currentSessionId
  )
  if (item.sessionId != sessionStore.currentSessionId) {
    sessionStore.changeSelectedSessionId(item.sessionId!)
    chatStore.getDialogList(item.sessionId)
  }

  // sessionStore.changeSelectedSessionId(55555)
  // console.log('选择会话:', item)
}

const panelClass = computed(() => ({
  'left-panel': true,
  open: (props.isMobile && props.isOpen) || (!props.isMobile && props.isPcOpen),
  'pc-collapsed': !props.isMobile && !props.isPcOpen
}))
</script>

<template>
  <view :class="panelClass">
    <view class="left-header">
      <view class="logo">
        <img src="@/assets/img/cmobile-logo.png" class="logo-icon" />
        <text class="logo-text">网络垂类大模型</text>
      </view>
    </view>

    <!-- <view class="menu-list">
      <view class="menu-item">
        <Setting class="menu-icon" />
        <text class="menu-text">个人配置</text>
      </view>
      <view class="menu-item">
        <Folder class="menu-icon" />
        <text class="menu-text">个人知识管理</text>
      </view>
    </view> -->

    <view class="new-chat">
      <button
        class="new-chat-btn shadow-lg shadow-blue-600/20 hover:shadow-blue-600/30 transform hover:-translate-y-0.5"
        @click="handleNewChat"
      >
        <Add class="svg-img" />
        <span class="btn-text">新建对话</span>
      </button>
    </view>
    <div class="px-6 mb-2 mt-2">
      <span class="text-xs font-semibold text-[rgb(148,163,184)] uppercase tracking-wider"
        >会话记录</span
      >
    </div>

    <view class="conversation-section">
      <view class="conversation-list space-y-1">
        <view
          class="conversation-item group transition-colors border border-transparent"
          v-for="(item, index) in conversationList"
          :key="index"
          @click="handleSelectConversation(item)"
        >
          <div class="flex items-start gap-2.5">
            <div
              class="mt-0.5 text-[rgb(148,163,184)] group-hover:text-[rgb(59,130,246)] transition-colors scale-90"
            >
              <Dialogue class="w-[30rpx] h-[30rpx]" />
            </div>
            <div class="flex-1 min-w-0">
              <p
                class="text-sm text-[rgb(71,85,105)] truncate group-hover:text-[rgb(15,23,42)] leading-tight"
              >
                {{ item.title }}
              </p>
              <p class="text-[10px] text-[rgb(148,163,184)] mt-1.5">
                {{ dayjs(item.latestCreateTime).format('YYYY-MM-DD HH:mm') }}
              </p>
            </div>
            <button
              class="delete-session-btn"
              @click.stop="handleDeleteConversation(item)"
              title="删除对话"
            >×</button>
          </div>
        </view>
      </view>
    </view>
    <!-- <div class="flex-1"></div> -->
    <!-- <div class="upgrade-section">
      <div class="upgrade-content">
        <div class="text-xs text-[rgb(30,64,175)] font-medium mb-[8rpx]">升级专业版</div>
        <div class="upgrade-desc text-[10px]">解锁更多高级模型与数据权限</div>
      </div>
    </div> -->
  </view>
</template>

<style lang="scss" scoped>
.left-panel {
  width: 530rpx;
  min-width: 530rpx;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.28s ease, min-width 0.28s ease, border-color 0.28s ease;

  > * {
    transition: opacity 0.2s ease, transform 0.28s ease;
  }

  .left-header {
    padding: 48rpx;

    .logo {
      display: flex;
      align-items: center;
      gap: 24rpx;

      .logo-icon {
        width: 80rpx;
        height: 80rpx;
        object-fit: contain;
      }

      .logo-text {
        font-size: 40rpx;
        line-height: 56rpx;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: rgb(30, 41, 59);
      }
    }
  }

  .menu-list {
    padding: 0 32rpx;
    margin-bottom: 48rpx;

    .menu-item {
      display: flex;
      align-items: center;
      gap: 24rpx;
      padding: 20rpx 24rpx;
      cursor: pointer;
      transition: all 0.2s ease;
      border-radius: 24rpx;
      color: #374151;

      &:nth-of-type(2) {
        margin-top: 16rpx;
      }

      &:hover {
        background-color: rgb(248, 250, 252);
        color: rgb(15, 23, 42);
      }

      .menu-icon {
        width: 40rpx;
        height: 40rpx;
      }

      .menu-text {
        font-size: 28rpx;
      }
    }
  }

  .new-chat {
    padding: 0 32rpx;
    margin-bottom: 32rpx;

    .new-chat-btn {
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16rpx;
      padding: 24rpx;
      color: #fff;
      background-color: rgb(37, 99, 235);
      border-radius: 24rpx;
      font-size: 28rpx;
      line-height: 40rpx;

      .svg-img {
        width: 40rpx;
        height: 40rpx;
        fill: #fff;
      }

      &:hover {
        background-color: rgb(29, 78, 216);
      }
    }
  }

  .conversation-section {
    padding: 0 16rpx 32rpx;
    flex: 1;
    overflow-y: auto;

    .conversation-list {
      display: flex;
      flex-direction: column;
      gap: 8rpx;

      .conversation-item {
        display: flex;
        flex-direction: column;
        padding: 20rpx 24rpx;
        cursor: pointer;
        border-radius: 16rpx;

        gap: 24rpx;
        padding: 24rpx;
        border-radius: 16rpx;

        transition: all 0.2s ease;

        &:hover {
          border-color: #f1f5f9;
          background-color: rgb(248 250 252 / 1);
        }

        .delete-session-btn {
          opacity: 0;
          flex-shrink: 0;
          width: 20px;
          height: 20px;
          line-height: 18px;
          text-align: center;
          border-radius: 50%;
          font-size: 16px;
          color: #94a3b8;
          transition: all 0.15s ease;
          &:hover {
            background-color: #fee2e2;
            color: #ef4444;
          }
        }
        &:hover .delete-session-btn {
          opacity: 1;
        }

        .checkbox {
          width: 32rpx;
          height: 32rpx;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-top: 4rpx;
          flex-shrink: 0;
        }

        .conversation-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 8rpx;
          min-width: 0;

          .conversation-title {
            font-size: 28rpx;
            color: #374151;
            font-weight: 500;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .conversation-time {
            font-size: 24rpx;
            color: #9ca3af;
          }
        }
      }
    }
  }

  .upgrade-section {
    padding: 32rpx;
    border-top: 1px solid rgb(241, 245, 249);
    .upgrade-content {
      padding: 24rpx;
      border-radius: 24rpx;
      border: 1rpx solid rgb(219 234 254 / 0.5);
      background-image: linear-gradient(to bottom right, #eef2ff, #eff6ff);
      .upgrade-desc {
        font-size: 24rpx;
        color: rgb(37 99 235 / 0.7);
        line-height: 1.4;
      }
    }
  }
}

@media (min-width: 769px) {
  .left-panel.pc-collapsed {
    width: 0;
    min-width: 0;
    border-right-color: transparent;
    pointer-events: none;

    > * {
      opacity: 0;
      transform: translateX(-12rpx);
    }
  }
}

@media (max-width: 768px) {
  .left-panel {
    width: 75%;
    max-width: 640rpx;
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    z-index: 100;
    transform: translateX(-100%);
    transition: transform 0.3s ease;

    &.open {
      transform: translateX(0);
    }
  }

  // .right-panel {
  //   background: #fff;
  //   width: 100%;

  //   .function-buttons {
  //     gap: 24rpx;

  //     .function-btn {
  //       min-width: 200rpx;
  //       padding: 24rpx 32rpx;
  //     }
  //   }
  // }
}
</style>
