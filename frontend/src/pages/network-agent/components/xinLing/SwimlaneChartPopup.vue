<!-- src/pages/network-agent/components/xinLing/SwimlaneChartPopup.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import SwimlaneChart from './SwimlaneChart.vue'
import Fullscreen from '@/components/svg/Fullscreen.vue'
import ExitFullscreen from '@/components/svg/ExitFullscreen.vue'

interface Props {
  visible: boolean
  chartData: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const isFullscreen = ref(false)

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const close = () => {
  isFullscreen.value = false
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible && chartData" class="chart-popup-overlay" @click.self="close">
      <div class="chart-popup-container" :class="{ 'chart-popup-fullscreen': isFullscreen }">
        <div class="chart-popup-header">
          <span class="chart-popup-title">泳道图</span>
          <div class="chart-popup-actions">
            <button
              class="chart-popup-btn"
              @click="toggleFullscreen"
              :title="isFullscreen ? '退出全屏' : '全屏'"
            >
              <ExitFullscreen v-if="isFullscreen" />
              <Fullscreen v-else />
            </button>
            <button class="chart-popup-close" @click="close">&times;</button>
          </div>
        </div>
        <div class="chart-popup-body">
          <SwimlaneChart :chartData="chartData" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style lang="scss" scoped>
.chart-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.chart-popup-container {
  background: #fff;
  border-radius: 12px;
  width: 90vw;
  max-width: 1200px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transition: all 0.3s ease;
}

.chart-popup-fullscreen {
  width: 100vw;
  max-width: 100vw;
  height: 100vh;
  border-radius: 0;
}

.chart-popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.chart-popup-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.chart-popup-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.chart-popup-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 6px;
  line-height: 1;
  display: flex;
  align-items: center;
  &:hover {
    color: #475569;
  }
}

.chart-popup-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  &:hover {
    color: #475569;
  }
}

.chart-popup-body {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}
</style>
