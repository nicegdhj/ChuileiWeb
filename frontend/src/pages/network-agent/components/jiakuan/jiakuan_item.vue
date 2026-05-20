<script setup lang="ts">
import { computed, ref } from 'vue'
import JiakuanChartCard from './jiakuan_chart_card.vue'
import JiakuanPieGroup from './jiakuan_pie_group.vue'
import JiakuanProfileGroup from './jiakuan_profile_group.vue'
import { useChatStore } from '@/stores';

const props = defineProps<{
  content: jiakuan.jiakuanProps
}>()

const chartDetails = computed(
  () =>
    (props.content.query_chat_details || []).filter(
      item => item.chart_type === 1 || item.chart_type === 2 || item.chart_type === 3
    ) as jiakuan.NormalChartItem[]
)

const pieDetails = computed(() => chartDetails.value.filter(item => item.chart_type === 2))
const otherChartDetails = computed(() =>
  chartDetails.value.filter(item => item.chart_type === 1 || item.chart_type === 3)
)
// 用户画像数据
const ProfileDetails = computed(
  () =>
    (props.content.query_chat_details || []).filter(
      item => item.chart_type === 5
    ) as jiakuan.UserProfileChartItem[]
)
// excel表格相关的数据
const execlDetails = computed(() => props.content.query_chat_excel || [])

const isExcelDrawerOpen = ref(false)
const activeExcelName = ref<string>('')

const activeExcel = computed(
  () => execlDetails.value.find(item => item.name === activeExcelName.value) || execlDetails.value[0]
)
const activeHeaders = computed(() => activeExcel.value?.th || [])
const activeRows = computed(() => activeExcel.value?.td || [])

const openExcelDrawer = (name: string) => {
  activeExcelName.value = name
  isExcelDrawerOpen.value = true
}

const closeExcelDrawer = () => {
  isExcelDrawerOpen.value = false
}

const getCellValue = (row: Record<string, any>, en: string) => {
  const value = row?.[en]
  if (value === null || value === undefined || value === '') return '--'
  return String(value)
}

/** 问答数据 */
const recommendDetail = computed(()=> props.content.query_recommend_questions || [])

const chatStore = useChatStore()
const fillInput = (item: string)=> {
  console.log("🚀 ~ fillInput ~ item:", item)
  chatStore.setInputValue(item)
  
}
</script>

<template>
  <div class="jiakuan-container">
    <!-- 文本描述 -->
    <div class="chat-text" v-if="props.content.chat">
      {{ props.content.chat }}
    </div>
    <!-- 饼图 -->
    <div v-if="pieDetails.length" class="chart-list">
      <div class="flex justify-center font-bold text-2xl">{{ pieDetails[0]?.title || '' }}</div>
      <JiakuanPieGroup :details="pieDetails" />
    </div>
    <!-- 柱状图和折线图 -->
    <div v-if="otherChartDetails.length" class="chart-list">
      <JiakuanChartCard
        v-for="(detail, index) in otherChartDetails"
        :key="`${detail.title}-${detail.chart_type}-${index}`"
        :detail="detail"
      />
    </div>
    <!-- 用户画像 -->
    <JiakuanProfileGroup :details="ProfileDetails" />
    <!-- excel表格 -->
    <div v-if="execlDetails.length" class="excel-list">
      <div class="excel-row" v-for="item in execlDetails" :key="item.name">
        <div class="excel-name">{{ item.name }}：</div>
        <button class="preview-btn" @click="openExcelDrawer(item.name)">数据预览</button>
      </div>
    </div>
    <!-- 表格 -->
    <teleport to="body">
      <transition name="drawer-fade">
        <div v-if="isExcelDrawerOpen" class="drawer-mask" @click.self="closeExcelDrawer">
          <div class="excel-drawer">
            <div class="drawer-header">
              <div class="drawer-title">数据预览：{{ activeExcel?.name || '--' }}</div>
              <button class="drawer-close-btn" @click="closeExcelDrawer">关闭</button>
            </div>

            <div class="table-scroll-wrap">
              <table class="excel-table">
                <thead>
                  <tr>
                    <th v-for="(h, hIdx) in activeHeaders" :key="`h-${h.en}-${hIdx}`">
                      {{ h.zh || h.en }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rIdx) in activeRows" :key="`r-${rIdx}`">
                    <td v-for="(h, hIdx) in activeHeaders" :key="`c-${rIdx}-${h.en}-${hIdx}`">
                      {{ getCellValue(row as Record<string, any>, h.en) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
    <!-- 问答 -->
     <div class="recommend" v-if="recommendDetail.length">
      <div class="recommend-item" v-for="(item,index) in recommendDetail" :key="index" @click="fillInput(item)">
        {{ item }}
      </div>

     </div>
  </div>
</template>

<style lang="scss" scoped>
.jiakuan-container {
  width: 100%;
  padding: 10px 0;
}

.chat-text {
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.chart-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.excel-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.excel-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.excel-name {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.preview-btn {
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  line-height: 1.4;
}

.drawer-mask {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(15, 23, 42, 0.35);
  display: flex;
  justify-content: center;
  align-items: stretch;
}

.excel-drawer {
  width: 100%;
  height: 100vh;
  background: #f8fafc;
  border-radius: 0;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
}

.drawer-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.drawer-close-btn {
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #4b5563;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
}

.table-scroll-wrap {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 14px 16px 18px;
  box-sizing: border-box;
}

.excel-table {
  width: max(100%, 1120px);
  border-collapse: collapse;
  table-layout: auto;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);

  th,
  td {
    border: 1px solid #dbe3ee;
    padding: 9px 12px;
    font-size: 12px;
    color: #374151;
    text-align: left;
    white-space: nowrap;
  }

  thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #eef2f7;
    color: #111827;
    font-weight: 600;
  }

  tbody tr {
    background: #ffffff;
  }

  tbody tr:nth-child(even) {
    background: #f6f9ff;
  }

  tbody tr:hover {
    background: #edf4ff;
  }
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}
.recommend {
  margin-top: 10rpx;
  .recommend-item {
    background-color: #f5f5f5;
    color: #666;
    padding: 5rpx 10rpx;
    margin-bottom: 15rpx;
  }
}

</style>
