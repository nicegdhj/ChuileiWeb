<script setup lang="ts">
import IdImg from '@/assets/img/icon-id.png'
defineProps<{
  details: jiakuan.UserProfileChartItem[]
}>()
</script>

<template>
  <div v-if="details.length" class="profile-section">
    <div
      class="profile-block"
      v-for="(profileGroup, groupIdx) in details"
      :key="`profile-group-${groupIdx}`"
    >
      <div class="profile-title" v-if="profileGroup.title">{{ profileGroup.title }}</div>
      <div class="profile-list">
        <div
          class="profile-card"
          v-for="(item, itemIdx) in profileGroup.data"
          :key="`${item.id}-${itemIdx}`"
        >
          <div class="profile-head">
            <img
              class="avatar"
              :src="`http://zmcc.zznode.com:8380/${item.avatar}`"
              :alt="item.name || '用户头像'"
            />
            <div class="head-main">
              <div class="name-row">
                <span class="name">{{ item.name || '--' }}</span>
                <span class="post">{{ item.region || '--' }}</span>
              </div>
              <div class="user-profile-id">
                <img :src="IdImg" alt="" class="w-[30rpx] h-[30rpx]" />
                装维工号：{{ item.id || '--' }}
              </div>
            </div>
          </div>
          <div class="profile-grid">
            <div class="field">
              <span class="label">入职时间</span>
              <span class="value">{{ item.entry_date || '--' }}</span>
            </div>
            <div class="field">
              <span class="label">工龄</span>
              <span class="value">{{ item.working_age || '--' }}</span>
            </div>
            <div class="field">
              <span class="label">工组</span>
              <span class="value">{{ item.group_name || '--' }}</span>
            </div>
            <div class="field">
              <span class="label">岗位</span>
              <span class="value">{{ item.post || '--' }}</span>
            </div>
            <div class="field">
              <span class="label">关联班长工号</span>
              <span class="value">{{ item.monitor_id || '--' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.profile-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
}

.profile-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.profile-card {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fff;
}

.profile-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.avatar {
  width: 100rpx;
  height: 150rpx;
  object-fit: cover;
  background: #f3f4f6;
}

.head-main {
  flex: 1;
  min-width: 0;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.name {
  font-size: 32rpx;
  font-weight: 600;
  color: #111827;
}

.post {
  font-size: 12px;
  color: #aaa;
  background: #eee;
  padding: 2px 8px;
}

.user-profile-id {
  display: inline-flex;
  justify-content: flex-start;
  align-items: center;
  color: #3b7f9e;
  background-color: #e5f7ff;
  margin-top: 15rpx;
  font-size: 20rpx;
  padding: 2px 8px;
  border-radius: 5rpx;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.field {
  display: flex;
  gap: 20rpx;
}

.label {
  min-width: 2em;
  font-size: 12px;
  color: #9ca3af;
}

.value {
  font-size: 13px;
  color: #374151;
  font-weight: bold;
  word-break: break-all;
}
</style>
