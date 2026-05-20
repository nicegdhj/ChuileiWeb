<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  LineChart,
  PieChart,
  CanvasRenderer
])

const props = defineProps<{
  detail: jiakuan.NormalChartItem
}>()

/** 超过该数量的 x 轴类目时启用横向滚动 + 最小宽度（折线/柱状） */
const X_AXIS_SCROLL_THRESHOLD = 12
/** 每个类目预留像素，避免标签挤在一起（含旋转标签占用） */
const MIN_PX_PER_X_CATEGORY = 44

const isFullScreen = ref(false)
const fullScreenChartRef = ref<InstanceType<typeof VChart> | null>(null)

const baseSeries = computed(() => props.detail.data || [])
const xAxisLabels = computed(() => Object.keys(baseSeries.value[0]?.x || {}))
const hasData = computed(() => xAxisLabels.value.length > 0 && baseSeries.value.length > 0)

const isBarOrLineChart = computed(
  () => props.detail.chart_type === 1 || props.detail.chart_type === 3
)

const needsXScroll = computed(() => {
  if (!isBarOrLineChart.value) return false
  return xAxisLabels.value.length > X_AXIS_SCROLL_THRESHOLD
})

const chartScrollContentWidth = computed(() => {
  const n = xAxisLabels.value.length
  if (!needsXScroll.value || n === 0) return undefined
  return `${Math.max(n * MIN_PX_PER_X_CATEGORY, 480)}px`
})

const scrollSizerStyle = computed(() => {
  const w = chartScrollContentWidth.value
  const base = { height: '100%', boxSizing: 'border-box' as const }
  if (!w) return { ...base, width: '100%', minWidth: '100%' }
  // 宽度不足时占满容器，超出时按最小宽度横向滚动
  return { ...base, width: `max(100%, ${w})`, minWidth: '100%' }
})

const chartOption = computed(() => {
  if (!hasData.value) return {}

  const title = props.detail.title || '数据统计'
  const chartType = props.detail.chart_type

  if (chartType === 2) {
    const firstSeries = baseSeries.value[0]
    const pieData = Object.entries(firstSeries.x || {}).map(([name, value]) => ({
      name,
      value: Number(value)
    }))
    return {
      title: {
        text: title,
        left: 'center',
        top: 6,
        textStyle: { fontSize: 14, fontWeight: 'bold', color: '#333' }
      },
      tooltip: { trigger: 'item' },
      legend: { left: 'center', top: 32, type: 'scroll' },
      series: [
        {
          name: firstSeries.legend || '占比',
          type: 'pie',
          radius: ['30%', '56%'],
          center: ['50%', '64%'],
          data: pieData,
          label: { formatter: '{b}: {d}%' }
        }
      ]
    }
  }

  const seriesType = chartType === 3 ? 'line' : 'bar'
  const series = baseSeries.value.map((item: jiakuan.Chart) => ({
    name: item.legend || '数值',
    type: seriesType,
    data: xAxisLabels.value.map(label => Number(item.x?.[label] ?? 0)),
    smooth: chartType === 3,
    itemStyle: chartType === 1 ? { borderRadius: [4, 4, 0, 0] } : undefined,
    barMaxWidth: chartType === 1 ? 40 : undefined
  }))

  return {
    title: {
      text: title,
      left: 'center',
      top: 6,
      textStyle: { fontSize: 14, fontWeight: 'bold', color: '#333' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: chartType === 1 ? 'shadow' : 'line' }
    },
    legend: { top: 30, left: 'center', type: 'scroll' },
    grid: { left: '3%', right: '4%', bottom: '8%', top: 72, containLabel: true },
    xAxis: {
      type: 'category',
      data: xAxisLabels.value,
      axisLabel: { interval: 0, rotate: 30, fontSize: 10, color: '#666' },
      axisLine: { lineStyle: { color: '#eee' } }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
    },
    series
  }
})

const resizeFullScreenChart = () => {
  fullScreenChartRef.value?.resize()
}

const openFullScreen = () => {
  isFullScreen.value = true
  nextTick(() => {
    resizeFullScreenChart()
    requestAnimationFrame(() => {
      resizeFullScreenChart()
      setTimeout(() => resizeFullScreenChart(), 320)
    })
  })
}

const closeFullScreen = () => {
  isFullScreen.value = false
}
</script>

<template>
  <div v-if="hasData" class="chart-wrapper">
    <button type="button" class="expand-hint" @click.stop="openFullScreen">全屏展示</button>
    <div
      class="chart-scroll"
      :class="{ 'chart-scroll--x': needsXScroll }"
    >
      <div class="chart-scroll-sizer" :style="scrollSizerStyle">
        <v-chart class="chart" :option="chartOption" autoresize />
      </div>
    </div>
  </div>
  <div v-else class="empty-chart">暂无图表数据</div>

  <teleport to="body">
    <transition name="fade">
      <div v-if="isFullScreen" class="fullscreen-overlay" @click.self="closeFullScreen">
        <div class="fullscreen-header">
          <span class="title">{{ detail.title || '图表详情' }}</span>
          <button class="close-btn" @click="closeFullScreen">✕</button>
        </div>
        <div class="fullscreen-chart-container">
          <div
            class="chart-scroll chart-scroll--fullscreen"
            :class="{ 'chart-scroll--x': needsXScroll }"
          >
            <div class="chart-scroll-sizer chart-scroll-sizer--fullscreen" :style="scrollSizerStyle">
              <v-chart
                ref="fullScreenChartRef"
                class="chart chart--fullscreen"
                :option="chartOption"
                autoresize
              />
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<style lang="scss" scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  height: 300px;
  background-color: #fff;
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

  .expand-hint {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 10px;
    color: #999;
    background: rgba(255, 255, 255, 0.9);
    padding: 2px 6px;
    border-radius: 4px;
    z-index: 20;
    cursor: pointer;
    pointer-events: auto;
    border: 1px solid #eee;
    line-height: 1.4;
    font-family: inherit;
  }
}

.chart-scroll {
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  overflow-y: hidden;
}

.chart-scroll--x {
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
}

.chart-scroll-sizer {
  height: 100%;
  box-sizing: border-box;
}

.chart {
  width: 100%;
  height: 100%;
}

.empty-chart {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #fff;
  z-index: 9999;
  display: flex;
  flex-direction: column;
}

.fullscreen-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  border-bottom: 1px solid #eee;
  background-color: #fff;
  flex-shrink: 0;

  .title {
    font-size: 16px;
    font-weight: bold;
    color: #333;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #666;
    padding: 0 10px;
    cursor: pointer;
    line-height: 1;
  }
}

.fullscreen-chart-container {
  flex: 1;
  width: 100%;
  min-height: 0;
  padding: 15px;
  box-sizing: border-box;
  overflow: hidden;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}

.chart-scroll--fullscreen {
  flex: 1;
  width: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.chart-scroll-sizer--fullscreen {
  flex: 1;
  min-height: 0;
  min-width: 0;
}

.chart--fullscreen {
  flex: 1;
  min-height: 0;
  min-width: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
