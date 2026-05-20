<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TitleComponent, TooltipComponent, PieChart, CanvasRenderer])

const props = defineProps<{
  details: jiakuan.NormalChartItem[]
}>()

/** 单饼宽度（px），半径按像素算，避免多饼共用一个 canvas 时 % 半径相对整图导致重叠 */
const PIE_ITEM_WIDTH = 220
const PIE_ITEM_HEIGHT = 300

/**
 * 一条 chart_type=2 的项里，data[] 每一项（不同 legend）对应一个独立饼图；
 * 多条 query_chat_details 也会依次展开。
 */
function pieTitleForSlice(
  detail: jiakuan.NormalChartItem,
  chart: jiakuan.Chart,
  sliceIndex: number
) {
  const base = detail.title?.trim() || '数据统计'
  const charts = detail.data || []
  if (charts.length <= 1) return base
  const leg = chart.legend?.trim()
  return leg
}

function buildSinglePieOption(title: string, chart: jiakuan.Chart) {
  const pieData = Object.entries(chart.x || {}).map(([name, value]) => ({
    name,
    value: Number(value)
  }))

  return {
    title: {
      text: title,
      textStyle: { fontSize: 13, fontWeight: 'bold', color: '#333' },
      textAlign: 'center'
    },
    tooltip: {
      trigger: 'item',
      confine: true
    },
    legend: { show: false },
    series: [
      {
        name: chart.legend || title || '占比',
        type: 'pie',
        radius: [52, 78],
        center: ['50%', '58%'],
        data: pieData,
        label: { formatter: '{b}', fontSize: 10 },
        labelLine: { length: 6, length2: 4 },
        minAngle: 3
      }
    ]
  }
}

const pieItems = computed(() => {
  const out: { key: string; option: ReturnType<typeof buildSinglePieOption> }[] = []
  props.details.forEach((detail, dIdx) => {
    const charts = detail.data?.length ? detail.data : []
    charts.forEach((chart, cIdx) => {
      const title = pieTitleForSlice(detail, chart, cIdx)
      out.push({
        key: `${detail.title}-${dIdx}-${chart.legend}-${cIdx}`,
        option: buildSinglePieOption(title, chart)
      })
    })
  })
  return out
})

const scrollInnerWidth = computed(() => {
  const n = pieItems.value.length
  if (n <= 0) return '100%'
  return `${n * PIE_ITEM_WIDTH + Math.max(0, n - 1) * 12}px`
})
</script>

<template>
  <div v-if="pieItems.length" class="pie-scroll-wrapper">
    <div class="pie-scroll-inner" :style="{ width: scrollInnerWidth, minWidth: '100%' }">
      <div
        v-for="(item, idx) in pieItems"
        :key="`${item.key}-${idx}`"
        class="pie-item"
        :style="{ width: `${PIE_ITEM_WIDTH}px`, height: `${PIE_ITEM_HEIGHT}px` }"
      >
        <v-chart class="pie-chart" :option="item.option" autoresize />
      </div>
    </div>
  </div>
  <div v-else class="pie-empty">暂无饼图数据</div>
</template>

<style lang="scss" scoped>
.pie-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
}

.pie-scroll-inner {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: stretch;
  gap: 12px;
  box-sizing: border-box;
  padding: 8px 4px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.pie-item {
  flex: 0 0 auto;
  box-sizing: border-box;
}

.pie-chart {
  width: 100%;
  height: 100%;
}

.pie-empty {
  padding: 16px;
  text-align: center;
  font-size: 12px;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
}
</style>
