<script setup lang="ts">
import MenuIcon from '@/components/svg/Menu.vue'
import Agent from '@/components/svg/Agent.vue'
import Avatar from '@/components/svg/Avatar.vue'
// import { useMemberStore } from '@/stores'
import Left from '@/components/svg/Left.vue'
import RightDouble from '@/components/svg/RightDouble.vue'
import LeftDouble from '@/components/svg/LeftDouble.vue'
const props = defineProps<{
  toggleMenu: () => void
  togglePcMenu: () => void
  showPcMenu: boolean
  isMobile: boolean
}>()

// const useMember = useMemberStore()
const backPage = () => {
  const topWin = window.top as any
  const bridge = topWin?.PDAJsBridge || (window as any).PDAJsBridge

  if (bridge?.close) {
    bridge.close().catch(() => {})
    return
  }

  // 兜底：桥不存在时回退
  uni.navigateBack({ delta: 1 })
}
</script>

<template>
  <header class="header-container">
    <div class="mobile-container">
      <div class="mobile-left">
        <Left @click.stop="backPage" />
        <MenuIcon @click.stop="props.toggleMenu" />
        <div class="mobile-icon bg-slate-100">
          <Agent class="agent-icon" />
        </div>
        <span class="font-bold text-slate-800 text-lg">网络运维超级入口</span>
      </div>
      <div class="mobile-right shadow-sm">
        <Avatar />
      </div>
    </div>
    <div class="dividing-line"></div>
    <div class="pc-container">
      <view class="switch_menu"
        ><LeftDouble v-if="showPcMenu" @click.stop="props.togglePcMenu" />
        <RightDouble v-else @click.stop="props.togglePcMenu" />
      </view>
      <div class="pc-wrap">
        <div class="text-right text-sm font-bold text-slate-700">
          {{ '' }}
        </div>
        <div class="pc-avatar">
          <img src="@/assets/img/pc-avatar.png" alt="avatar" />
          <!-- <Avatar /> -->
        </div>
      </div>
    </div>
  </header>
</template>

<style lang="scss" scoped>
.header-container {
  height: 112rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
  position: relative;
  .switch_menu {
    display: none;
    position: absolute;
    top: 20rpx;
    left: 30rpx;
    cursor: pointer;
    background-color: #fff;
    border-radius: 50%;
    box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.1);
  }
  .mobile-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    .mobile-left {
      gap: 24rpx;
      display: flex;
      align-items: center;
      .mobile-icon {
        width: 64rpx;
        height: 64rpx;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #f1f5f9;
        border-radius: 50%;
        .agent-icon {
          width: 40rpx;
          height: 40rpx;
        }
      }
    }
    .mobile-right {
      width: 64rpx;
      height: 64rpx;
      background-color: #f1f5f9;
      border: 1px solid #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      border-radius: 50%;
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }
  .dividing-line {
    display: none;
    flex: 1;
  }
  .pc-container {
    display: none;
    align-items: center;
    gap: 32rpx;
    .pc-wrap {
      gap: 24rpx;
      padding-left: 16rpx;
      display: flex;
      align-items: center;
      cursor: pointer;
    }
    .pc-avatar {
      width: 72rpx;
      height: 72rpx;
      background-color: #f1f5f9;
      border: 1px solid #fff;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      border-radius: 50%;
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }
}

@media (min-width: 768px) {
  .header-container {
    height: 128rpx;
    padding: 0 48rpx;
    .mobile-container {
      display: none;
    }
    .dividing-line {
      display: flex;
    }
    .switch_menu {
      display: block;
    }
    .pc-container {
      display: flex;
    }
  }
}
</style>
