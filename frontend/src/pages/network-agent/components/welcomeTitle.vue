<script setup lang="ts">
import Agent from '@/components/svg/Agent.vue'
</script>

<template>
  <div class="welcome-content md:px-12 md:pb-8 custom-scrollbar">
    <div class="welcome-wrap">
      <Agent class="w-16 h-16 mb-6" />
      <div class="text-wrap">
        <h1 class="title font-bold text-slate-800 gap-2">
          你好！我是网络运维超级入口<span class="version bg-blue-100 text-blue-600 font-medium"
            >V1.0</span
          >
        </h1>
        <p class="content text-slate-500 text-sm leading-7">
          作为您的网络域智能助手，我致力于利用AI技术深度赋能网络运维，为您提供涵盖故障诊断、性能分析、方案撰写及知识问答的一站式智能服务。
        </p>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.welcome-content {
  flex: 1;
  overflow-y: auto;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  position: relative;
  .welcome-wrap {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 1rem 5rem 1rem;
    .text-wrap {
      margin-bottom: 2rem;
      text-align: center;
      .title {
        font-size: 48rpx;
        line-height: 64rpx;
        margin-bottom: 1rem;
        display: flex;
        justify-content: center;
        align-items: center;
        .version {
          padding: 4rpx 12rpx;
          border-radius: 8rpx;
          font-size: 10px;
        }
        .content {
          font-size: 28rpx;
          line-height: 40rpx;
          max-width: 20rem;
          margin: 0 auto;
          text-align: justify;
        }
      }
    }
  }
}
@media (max-width: 768px) {
  .welcome-content {
    .welcome-wrap {
      .text-wrap {
        .title {
          font-size: 40rpx;
          line-height: 56rpx;
        }
        .content {
          font-size: 24rpx;
          line-height: 36rpx;
        }
      }
    }
  }
}
</style>
