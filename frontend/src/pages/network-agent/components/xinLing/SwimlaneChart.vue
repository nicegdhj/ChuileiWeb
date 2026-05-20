<!-- src/pages/network-agent/components/xinLing/SwimlaneChart.vue -->
<!-- 泳道图组件 - 从 Vue2 lane-chart.vue 迁移至 Vue3 Composition API -->
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as Highcharts from 'highcharts'
import imgBoxUrl from '@/assets/img/imgBox.png'

interface DeviceItem {
  [key: string]: any
}

interface ReportItem {
  [key: string]: any
}

interface ChartDataResult {
  reports: ReportItem[]
  devices: DeviceItem[]
}

interface TypeGroup {
  type: string
  source: string
  data: Array<{ ip: string; uuid: string }>
}

const props = defineProps<{
  chartData: ChartDataResult
}>()

const scrollContainer = ref<HTMLElement>()
const topScrollContainer = ref<HTMLElement>()
const leftScrollContainer = ref<HTMLElement>()

let chat1: Highcharts.Chart | null = null
let chat2: Highcharts.Chart | null = null
let chat3: Highcharts.Chart | null = null

const chartWidth = ref(0)
const chartHeight = ref(0)
const typeList = ref<TypeGroup[]>([])

/** 找出收发两端同类型的设备类型 */
function uniqueArray(reports: ReportItem[], devices: DeviceItem[]): string[] {
  const matched101s: string[] = []
  reports?.forEach(aItem => {
    let start101: string | null = null
    let end101: string | null = null
    devices.forEach(bItem => {
      if (aItem[8] === bItem[100]) start101 = bItem[101]
    })
    devices.forEach(bItem => {
      if (aItem[9] === bItem[100]) end101 = bItem[101]
    })
    if (start101 !== null && end101 !== null && start101 === end101) {
      matched101s.push(start101)
    }
  })
  return [...new Set(matched101s)]
}

/** 按 type 分组设备 */
function transformedArray(devices: DeviceItem[], uni: string[]): TypeGroup[] {
  return (
    devices?.reduce((acc: TypeGroup[], item) => {
      const type = item[101]
      const uuid = item[0]
      const ip = item[100]
      const source = item['source']
      if ([...uni, 'UE', 'UNDEFINED'].includes(type)) {
        acc.push({ type, source, data: [{ ip, uuid }] })
      } else {
        const found = acc.find(group => group.type === type)
        if (!found) {
          acc.push({ type, source, data: [{ ip, uuid }] })
        } else {
          found.data.push({ ip, uuid })
        }
      }
      return acc
    }, []) ?? []
  )
}

/** 合并相同 type 的数据 */
function mergeDataArray(array: TypeGroup[], uni: string[]): TypeGroup[] {
  const merged: Record<
    string,
    Array<{ data: Array<{ ip: string; uuid: string }>; source: string }>
  > = {}
  array.forEach((item, index) => {
    const key = [...uni, 'UE', 'UNDEFINED'].includes(item.type) ? `${item.type}${index}` : item.type
    if (!merged[key]) merged[key] = []
    merged[key].push({ data: [...item.data], source: item.source })
  })
  return Object.entries(merged).map(([type, data]) => {
    let finalType = type
    for (const prefix of [...uni, 'UNDEFINED', 'UE']) {
      if (type.startsWith(prefix)) {
        finalType = type.replace(/\d+$/, '')
      }
    }
    return { type: finalType, data: data[0].data, source: data[0].source }
  })
}

/** 计算箭头 SVG path */
function getLineArrow(startX: number, end: number, ydata: number): (string | number)[] {
  const Y = ydata + 10
  const endX = end + 11
  return [
    'M',
    startX + 35,
    Y,
    'L',
    endX,
    Y,
    'L',
    endX > startX ? endX - 5 : endX + 5,
    Y - 5,
    'M',
    endX,
    Y,
    'L',
    endX > startX ? endX - 5 : endX + 5,
    Y + 5
  ]
}

/** 初始化数据处理和图表渲染 */
function initPage() {
  const detailData = props.chartData
  if (!detailData?.reports || !detailData?.devices) return

  const maindevices = detailData.devices.filter(item => item.source == '1')
  const mainreports = detailData.reports.filter(item => item.identifyCallName == '主叫')
  const assistantdevices = detailData.devices.filter(item => item.source == '2')
  const assistantreports = detailData.reports.filter(item => item.identifyCallName == '被叫')

  const uni1 = uniqueArray(mainreports, maindevices)
  const uni2 = uniqueArray(assistantreports, assistantdevices)
  let res1 = transformedArray(maindevices, uni1)
  let res2 = transformedArray(assistantdevices, uni2)
  let resultArray1 = mergeDataArray(res1, uni1)
  let resultArray2 = mergeDataArray(res2, uni2)

  // 为重复类型添加编号
  let typeIndexes = new Map<string, number>()
  const uni1Use = uni1.filter(item => item !== 'UNDEFINED')
  uni1Use.forEach(type => typeIndexes.set(type, 0))
  resultArray1.forEach(item => {
    for (const u of uni1Use) {
      if (item.type.startsWith(u)) {
        const currentIndex = typeIndexes.get(u)!
        item.type = `${item.type} ${currentIndex + 1}`
        typeIndexes.set(u, currentIndex + 1)
      }
    }
  })

  let typeIndexes1 = new Map<string, number>()
  const uni2Use = uni2.filter(item => item !== 'UNDEFINED')
  uni2Use.forEach(type => typeIndexes1.set(type, 0))
  resultArray2.forEach(item => {
    for (const u of uni2Use) {
      if (item.type.startsWith(u)) {
        const currentIndex = typeIndexes1.get(u)!
        item.type = `${item.type} ${currentIndex + 1}`
        typeIndexes1.set(u, currentIndex + 1)
      }
    }
  })

  let resultArray = [...resultArray1, ...resultArray2]
  // UE 重命名
  resultArray.forEach(obj => {
    if (obj.type.startsWith('UE')) {
      let letterIndex = 0
      while (resultArray.some(item => item.type === `UE ${letterIndex + 1}`)) {
        letterIndex++
      }
      obj.type = `UE ${letterIndex + 1}`
    }
  })

  chartWidth.value = resultArray.length < 13 ? 1240 : resultArray.length * 90
  chartHeight.value = Math.ceil((detailData.reports?.length || 0) * 30.03)
  typeList.value = resultArray

  nextTick(() => {
    initCharts(resultArray, detailData.reports)
    innitHeader(resultArray, detailData.reports)
    innitDate(detailData.reports)
  })
}

/** 渲染主泳道图 */
function initCharts(q: TypeGroup[], w: ReportItem[]) {
  const options: Highcharts.Options = {
    chart: {
      backgroundColor: '#fff',
      events: {
        load: function (this: any) {
          const ren = this.renderer

          q.forEach((item, index) => {
            let x = index * 90 + 8
            if (q.length < 13) {
              const elseWidth = 1160 - 80 * q.length
              x = index * 80 + 20 + index * (elseWidth / (q.length - 1))
            }
            ren
              .path(['M', x + 28, -20, 'L', x + 28, w.length * 30] as any)
              .attr({ 'stroke-width': 1, stroke: 'silver', dashstyle: 'dash' })
              .add()
          })

          w.forEach((val, key) => {
            const heightbase = 20
            const offsetY = 15
            const y = key * (heightbase + 10) + offsetY

            const nv = String(val['5']).toLocaleLowerCase().trim()
            const protocol = String(val['2']).toLocaleLowerCase().trim()
            const isSipReason = typeof val['sip.Reason'] !== 'undefined' && val['sip.Reason'] !== ''
            const isSipWarning =
              typeof val['sip.Warning'] !== 'undefined' && val['sip.Warning'] !== ''
            const isHttp2error =
              typeof val['http2ErrorFlag'] !== 'undefined' && val['http2ErrorFlag'] === '是'
            const isError = typeof val['is_error'] !== 'undefined' && val['is_error'] !== ''

            let alarmcolor = '#000'
            if (
              nv.includes('uecontextreleasecommand [nas-cause=normal-release]') ||
              nv.includes('failure') ||
              nv.includes('reject') ||
              (protocol.includes('diameter') && nv.startsWith('abort-session request')) ||
              (protocol.includes('sip') && nv.startsWith('cancel')) ||
              (protocol.includes('sip') &&
                /^\d{3}.*$/g.test(nv) &&
                (nv.startsWith('4') || nv.startsWith('5') || nv.startsWith('6'))) ||
              isSipReason ||
              isHttp2error ||
              isSipWarning ||
              isError
            ) {
              alarmcolor = 'red'
            }

            const xStart = getXPosition(val[8], q)
            const xEnd = getXPosition(val[9], q)

            ren
              .path(getLineArrow(xStart, xEnd + 22, y) as any)
              .attr({ 'stroke-width': 1, stroke: alarmcolor, title: val[2], id: 'arrow' + val[0] })
              .add()

            const usex = xStart > xEnd ? xEnd : xStart
            const linelength = xStart > xEnd ? xStart - xEnd : xEnd - xStart
            const label = val[5].length > 50 ? val[5].slice(0, 50) + '...' : val[5]
            const txtLength = label.length * 6.2
            let xflot = 0
            if (linelength > txtLength) {
              xflot = (linelength - txtLength) / 2 - 5
            }

            ren
              .label(label, usex + 30 + xflot, y - 10)
              .addClass('highcharts-custom-label')
              .attr({ id: 'arrowlabel' + val[0], title: val[5] })
              .css({ fontWeight: '500', color: alarmcolor, fontSize: '12px', cursor: 'pointer' })
              .add()
          })
        }
      }
    },
    title: { text: '' },
    credits: { enabled: false }
  }

  chat1 = Highcharts.chart('container', options)
}

/** 渲染设备头部 */
function innitHeader(q: TypeGroup[], w: ReportItem[]) {
  const options: Highcharts.Options = {
    chart: {
      backgroundColor: '#fff',
      events: {
        load: function (this: any) {
          const ren = this.renderer

          q.forEach((item, index) => {
            let x = index * 90
            if (q.length < 13) {
              const elseWidth = 1160 - 80 * q.length
              x = index * 80 + 10 + index * (elseWidth / (q.length - 1))
            }

            const y = 20
            const typeLabel =
              item.type === 'UNDEFINED'
                ? 'Unknown'
                : item.type === 'GNB'
                ? 'gNB'
                : ['ENB', 'EGNB'].includes(item.type)
                ? 'eNB'
                : item.type
            const words = typeLabel.split('_')

            words.forEach((word, idx) => {
              const typeHeight = words.length === 1 ? 32 : idx === 0 ? 26 : 40
              ren
                .html(
                  `<div style="width:76px;text-align:center;font-size:${
                    word === 'PGW&LAC' ? '12px' : '14px'
                  }">${word}</div>`,
                  x,
                  y + typeHeight,
                  56,
                  56
                )
                .addClass('typeTxt')
                .attr({ id: String(index), textAnchor: 'middle' })
                .css({ fontWeight: '700', color: '#5257F9', fontSize: '14px', textAlign: 'center' })
                .add()
            })

            ren
              .image(imgBoxUrl, x, y, 76, 56)
              .addClass('typeImg')
              .attr({ id: `image-${index}` })
              .add()
          })
        }
      }
    },
    title: { text: '' },
    credits: { enabled: false }
  }

  chat3 = Highcharts.chart('headercontainer', options)
}

/** 渲染左侧时间轴 */
function innitDate(w: ReportItem[]) {
  const getTimeStamp = (val: ReportItem) => {
    const dateTime = new Date(val[3])
    const ms = parseInt(val[4], 10) || 0
    return dateTime.getTime() + ms
  }
  const timeStamps = w.map(getTimeStamp)

  const options: Highcharts.Options = {
    chart: {
      backgroundColor: '#fff',
      events: {
        load: function (this: any) {
          const ren = this.renderer
          w.forEach((val, key) => {
            const heightbase = 20
            const offsetY = 14
            const currentTimeY = key * (heightbase + 10) + offsetY

            // 时延
            if (key > 0) {
              const prevTimeY = (key - 1) * (heightbase + 10) + offsetY
              const diffY = prevTimeY + (currentTimeY - prevTimeY) / 2
              const timeDiffValue = (timeStamps[key] - timeStamps[key - 1]) / 1000
              const timeDiff = Number(timeDiffValue.toFixed(3)).toString()
              ren
                .label(`时延(${timeDiff}ms)`, 47, diffY)
                .attr({ id: `delay-${key}` })
                .css({ fontSize: '11px', color: '#0e95d0' })
                .add()
            }

            const timePart = val[3].split(' ')[1] || val[3]
            const timeStr = `${timePart}.${val[4]}`
            ren
              .label(timeStr, 5, currentTimeY)
              .attr({ id: `time-${key}` })
              .css({ fontWeight: '700', color: '#000', fontSize: '12px', whiteSpace: 'nowrap' })
              .add()
          })
        }
      }
    },
    title: { text: '' },
    credits: { enabled: false }
  }

  chat2 = Highcharts.chart('datecontainer', options)
}

/** 获取设备在泳道中的 X 坐标 */
function getXPosition(ip: string, q: TypeGroup[]): number {
  let x = 0
  q.forEach((item, index) => {
    if (item.data.find(d => d.ip === ip)) {
      if (q.length < 13) {
        const elseWidth = 1160 - 80 * q.length
        x = index * 80 + 14 + index * (elseWidth / (q.length - 1))
      } else {
        x = index * 90 + 2
      }
    }
  })
  return x
}

/** 滚动同步：主容器 */
function handleScroll(event: Event) {
  const target = event.target as HTMLElement
  if (topScrollContainer.value) topScrollContainer.value.scrollLeft = target.scrollLeft
  if (leftScrollContainer.value) leftScrollContainer.value.scrollTop = target.scrollTop
}

/** 滚动同步：左侧时间轴 */
function handleLeftScroll(event: Event) {
  const target = event.target as HTMLElement
  if (scrollContainer.value) scrollContainer.value.scrollTop = target.scrollTop
}

function destroyCharts() {
  chat1?.destroy()
  chat2?.destroy()
  chat3?.destroy()
  chat1 = null
  chat2 = null
  chat3 = null
}

onMounted(() => {
  initPage()
})

onBeforeUnmount(() => {
  destroyCharts()
})
</script>

<template>
  <div class="swimlane-chart">
    <div class="leftcontent">
      <div style="display: flex; width: 100%; height: 100%">
        <!-- 左侧时间 -->
        <div class="date-scroll-content">
          <div class="datescroll" ref="leftScrollContainer" @scroll="handleLeftScroll">
            <div id="datecontainer" :style="{ height: chartHeight + 'px' }"></div>
          </div>
        </div>
        <!-- 右侧容器 -->
        <div style="width: calc(100% - 130px); height: 100%">
          <div class="headerscroll" ref="topScrollContainer">
            <div id="headercontainer" :style="{ width: chartWidth + 'px' }"></div>
          </div>
          <div
            style="width: 100%; height: calc(100% - 80px); overflow: auto"
            class="scroll-container"
            @scroll="handleScroll"
            ref="scrollContainer"
          >
            <div
              id="container"
              :style="{
                width: chartWidth + 'px',
                height: chartHeight + 'px'
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.swimlane-chart {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #fff;
  position: relative;
}

#container {
  position: relative;
  min-width: 500px;
}

#headercontainer {
  height: 80px;
  min-width: 500px;
}

#datecontainer {
  width: 130px;
}

.leftcontent {
  width: 100%;
  min-height: 300px;
  position: relative;
  height: 100%;
}

.headerscroll {
  position: relative;
  overflow: hidden;
  width: 100%;
}

.headerscroll::-webkit-scrollbar {
  display: none;
}

.datescroll::-webkit-scrollbar {
  display: none;
}

.date-scroll-content {
  width: 130px;
  height: 100%;
  position: relative;
  background-color: #fff;

  .datescroll {
    width: 100%;
    height: calc(100% - 80px);
    position: absolute;
    left: 0;
    bottom: 0;
    overflow: hidden;
  }
}

.scroll-container {
  scrollbar-color: #97b4ed #dee9fe;
}
</style>
