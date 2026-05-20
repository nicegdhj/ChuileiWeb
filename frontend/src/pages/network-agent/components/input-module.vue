<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import DeepThink from '@/components/svg/DeepThink.vue'
import Scene from '@/components/svg/Scene.vue'
import Address from '@/components/svg/Address.vue'
import More from '@/components/svg/More.vue'
import Conference from '@/components/svg/Conference.vue'
import Recognition from '@/components/svg/Recognition.vue'
import Report from '@/components/svg/Report.vue'
import Translate from '@/components/svg/Translate.vue'
import Subscribe from '@/components/svg/Subscribe.vue'
import Voice from '@/components/svg/Voice.vue'
import Voice2 from '@/components/svg/Voice2.vue'
import Picture from '@/components/svg/Picture.vue'
import Link from '@/components/svg/Link.vue'
import Add from '@/components/svg/Add.vue'
import Send from '@/components/svg/Send.vue'
import Common from '@/components/svg/Common.vue'
import Footer from './footer.vue'
import ImagePreview from './ImagePreview.vue'
import { useChatStore } from '@/stores/modules/chat'
import { request } from '@/utils/http'
import CryptoJS from 'crypto-js'
import { useSessionStore } from '@/stores'

const chatStore = useChatStore()

type aite_type = {
  code?: number
  title?: string
  type?: number
  description?: string
  iconColor?: string
  name?: string[]
}
// 使用 uni-easyinput 替代自定义组件

const mySubscribeList = ref<aite_type[]>([])
const sceneList = ref<aite_type[]>([])
const cityList = ref<aite_type[]>([])

const sessionStore = useSessionStore()
const getSceneList = async () => {
  const { code, data, message } = await request<
    Response<{
      commonScene: aite_type[]
      subscriptionScene: aite_type[]
      zoneScene: aite_type[]
      nationScene: string[]
    }>
  >({
    url: '/suban-h5-dx/lingxi/agent/scene',
    method: 'GET'
  })
  // const result = {
  //   commonScene: [
  //     {
  //       code: 1,
  //       type: 1,
  //       title: '家宽智慧支撑',
  //       description: null
  //     },
  //     {
  //       code: 2,
  //       type: 1,
  //       title: '家宽智慧支撑',
  //       description: null
  //     },
  //     {
  //       code: 3,
  //       type: 1,
  //       title: '费用智慧管理',
  //       description: null
  //     },
  //     {
  //       code: 4,
  //       type: 1,
  //       title: '无线智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 5,
  //       type: 1,
  //       title: '无线智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 6,
  //       type: 1,
  //       title: '无线智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 7,
  //       type: 1,
  //       title: '家宽智慧支撑',
  //       description: null
  //     },
  //     {
  //       code: 8,
  //       type: 1,
  //       title: '无线智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 9,
  //       type: 1,
  //       title: '无线智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 10,
  //       type: 1,
  //       title: '网管智慧支撑',
  //       description: null
  //     },
  //     {
  //       code: 11,
  //       type: 1,
  //       title: '无线智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 12,
  //       type: 1,
  //       title: '家宽智慧支撑',
  //       description: null
  //     },
  //     {
  //       code: 13,
  //       type: 1,
  //       title: '核心网智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 14,
  //       type: 1,
  //       title: '政企智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 15,
  //       type: 1,
  //       title: '投诉智慧运维',
  //       description: null
  //     }
  //   ],
  //   zoneScene: [
  //     {
  //       code: 16,
  //       type: 2,
  //       title: '杭州智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 17,
  //       type: 2,
  //       title: '宁波智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 18,
  //       type: 2,
  //       title: '温州智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 19,
  //       type: 2,
  //       title: '嘉兴智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 20,
  //       type: 2,
  //       title: '湖州智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 21,
  //       type: 2,
  //       title: '绍兴智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 22,
  //       type: 2,
  //       title: '金华智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 23,
  //       type: 2,
  //       title: '衢州智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 24,
  //       type: 2,
  //       title: '舟山智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 25,
  //       type: 2,
  //       title: '台州智慧运维',
  //       description: null
  //     },
  //     {
  //       code: 26,
  //       type: 2,
  //       title: '丽水智慧运维',
  //       description: null
  //     }
  //   ],
  //   subscriptionScene: [
  //     {
  //       code: 27,
  //       type: 3,
  //       title: '舟山家客AI取数和分析小助手',
  //       description: '你好，测试文字'
  //     },
  //     {
  //       code: 28,
  //       type: 3,
  //       title: '装维随销智能体',
  //       description: null
  //     },
  //     {
  //       code: 29,
  //       type: 3,
  //       title: '铁塔精算助手',
  //       description: null
  //     },
  //     {
  //       code: 30,
  //       type: 3,
  //       title: '数仓查询智能体',
  //       description: null
  //     },
  //     {
  //       code: 31,
  //       type: 3,
  //       title: 'CA优化助手智能体',
  //       description: null
  //     },
  //     {
  //       code: 32,
  //       type: 3,
  //       title: '无线排障助手',
  //       description: null
  //     },
  //     {
  //       code: 33,
  //       type: 3,
  //       title: '宽带智能诊断',
  //       description: null
  //     },
  //     {
  //       code: 34,
  //       type: 3,
  //       title: '无线网络性能分析助手',
  //       description: null
  //     },
  //     {
  //       code: 35,
  //       type: 3,
  //       title: '无线网络5GA智能升级助手',
  //       description: null
  //     },
  //     {
  //       code: 36,
  //       type: 3,
  //       title: '工具便携式调用智能体',
  //       description: null
  //     },
  //     {
  //       code: 37,
  //       type: 3,
  //       title: '杭州无线保障通报助手',
  //       description: null
  //     },
  //     {
  //       code: 38,
  //       type: 3,
  //       title: '家宽装维智能体',
  //       description: null
  //     },
  //     {
  //       code: 39,
  //       type: 3,
  //       title: '核心网知识问答智能体',
  //       description: null
  //     },
  //     {
  //       code: 40,
  //       type: 3,
  //       title: '政企智能体',
  //       description: null
  //     },
  //     {
  //       code: 41,
  //       type: 3,
  //       title: '投诉处理智联助手',
  //       description: null
  //     }
  //   ]
  // }
  if (code == '00000') {
    let result = data
    let commonNum = result.commonScene.length * 1
    let cityNum = result.zoneScene.length * 1
    // console.log('🚀 ~ getSceneList ~ result:', result)
    sessionStore.updateNationScene(result.nationScene! || [])
    mySubscribeList.value = result.subscriptionScene?.map((item, index) => {
      switch (index) {
        case 0:
          item.iconColor = '#a855f7'
          break
        case 1:
          item.iconColor = '#3b82f6'
          break
        default:
          item.iconColor = '#6366f1'
          break
      }
      return { code: commonNum + cityNum + index * 1 + 1, ...item }
    })
    sceneList.value = result.commonScene?.map((item, index) => ({
      code: index + 1,
      ...item,
      iconColor:
        index == 0
          ? '#ec4899'
          : index > 0 && index <= 2
          ? '#f43f5e'
          : index > 2 && index <= 6
          ? '#f59e0b'
          : index > 6 && index <= 13
          ? '#3b82f6'
          : '#16a34a'
    }))
    cityList.value = result.zoneScene.map((item, index) => ({
      code: commonNum + index * 1 + 1,
      ...item
    }))
  } else {
    // uni.showToast({ icon: 'error', title: message || '请求失败' })
  }
}

/** 智能体/大模型选择 */
interface ModeOption {
  modeId: number
  name: string
}
const modeOptions = ref<ModeOption[]>([])
const selectedModeId = ref<number | undefined>(undefined)

const getModeList = async () => {
  try {
    const { code, data } = await request<Response<ModeOption[]>>({
      url: '/suban-h5-dx/lingxi/agent/mode',
      // url: '/lingxi/agent/mode',
      method: 'GET'
    })
    if (code == '00000' && data?.length) {
      modeOptions.value = data
      selectedModeId.value = data[0].modeId
    }
  } catch (e) {
    console.warn('获取大模型列表失败:', e)
  }
}

const agentDropdownOpen = ref(false)
const toggleAgentDropdown = () => {
  agentDropdownOpen.value = !agentDropdownOpen.value
}
const selectAgent = (mode: ModeOption) => {
  selectedModeId.value = mode.modeId
  agentDropdownOpen.value = false
}

// 点击外部关闭智能体下拉框
const handleClickOutsideAgent = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.mobile-nav, .agent-dropdown-wrap')) {
    agentDropdownOpen.value = false
  }
}
watch(agentDropdownOpen, open => {
  if (open) {
    setTimeout(() => document.addEventListener('mousedown', handleClickOutsideAgent), 0)
  } else {
    document.removeEventListener('mousedown', handleClickOutsideAgent)
  }
})

/** 选中的艾特列表 */
const aiteList = ref<aite_type[]>([])

/** 选中某个艾特项目 */
const choiceOneAite = (item: aite_type) => {
  let index = aiteList.value.findIndex(v => v.code == item.code && v.type == item.type)
  if (index == -1) {
    aiteList.value.push({ ...item })
  } else {
    aiteList.value.splice(index, 1)
  }
}
/** 删除某个艾特选项 */
const deleteOneAite = (item: aite_type) => {
  aiteList.value = aiteList.value.filter(v => !(v.code == item.code && v.type == item.type))
}

/** 输入框内容 */
const inputValue = ref('')

/** 已选择的图片列表 */
const selectedImages = ref<string[]>([])

/** 已选择的文件列表 */
const selectedFiles = ref<any[]>([])

const MAX_FILE_COUNT = 5
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_EXTENSIONS = ['.pcap', '.xdr', '.zip']

/** 点击添加按钮，弹出选择菜单 */
const handleAddClick = () => {
  uni.showActionSheet({
    itemList: ['拍照', '从相册选择', '选择文件'],
    success: (res: any) => {
      if (res.tapIndex === 0) {
        chooseImage(['camera'])
      } else if (res.tapIndex === 1) {
        chooseImage(['album'])
      } else if (res.tapIndex === 2) {
        chooseFile()
      }
    }
  })
}

/** 选择图片 */
const chooseImage = (sourceType: string[]) => {
  uni.chooseImage({
    count: sourceType.includes('album') ? 9 : 1,
    sourceType: sourceType as any,
    success: (res: any) => {
      selectedImages.value = [...selectedImages.value, ...res.tempFilePaths]
    }
  })
}

/** 选择文件后加入预览列表 */
const chooseFile = () => {
  const remaining = MAX_FILE_COUNT - selectedFiles.value.length
  if (remaining <= 0) {
    uni.showToast({ title: '最多上传5个文件', icon: 'none' })
    return
  }
  uni.chooseFile({
    count: remaining,
    extension: ALLOWED_EXTENSIONS,
    success: (res: any) => {
      const files: any[] = res.tempFiles
      // 校验单个文件大小
      const oversized = files.find((f: any) => (f.size || 0) > MAX_FILE_SIZE)
      if (oversized) {
        uni.showToast({ title: `文件 ${oversized.name || ''} 超过10MB限制`, icon: 'none' })
        return
      }
      selectedFiles.value = [...selectedFiles.value, ...files]
    },
    fail: (err: any) => {
      console.error('文件选择失败:', err)
    }
  })
}

/** 删除预览图片 */
const removeImage = (index: number) => {
  selectedImages.value.splice(index, 1)
}

/** 删除预览文件 */
const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

/** 其它按钮 我的订阅subscribe 常用场景scene 地市专区prefecture 更多more(仅限移动端) 上传uploads(仅移动端) */
const otherBtn = ref<'SubscriptionScene' | 'CommonScene' | 'ZoneScene' | 'more' | 'uploads' | ''>(
  ''
)

/** 点击关闭弹窗的模块 */
// 用于引用弹窗元素
const selectionModalRef = ref<HTMLElement | null>(null)

// 点击外部区域关闭弹窗的处理函数
const handleClickOutside = (event: MouseEvent) => {
  // 如果弹窗未显示，则不执行任何操作
  if (!otherBtn.value) return

  // 检查点击的目标是否在弹窗及其子元素之外
  if (selectionModalRef.value && !selectionModalRef.value.contains(event.target as Node)) {
    // 检查点击的目标是否是触发弹窗显示的按钮
    const target = event.target as HTMLElement
    const isTriggerButton = target.closest('.nav-item, .action-button')

    // 如果不是触发按钮，则关闭弹窗
    if (!isTriggerButton) {
      otherBtn.value = ''
    }
  }
}

// 监听其他按钮状态变化
watch(otherBtn, newVal => {
  if (newVal) {
    // 如果弹窗被打开，添加事件监听器
    setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside)
    }, 0)
  } else {
    // 如果弹窗被关闭，移除事件监听器
    document.removeEventListener('mousedown', handleClickOutside)
  }
})

onMounted(() => {
  getSceneList()
  getModeList()
})

onUnmounted(() => {
  // 组件卸载时移除事件监听器
  document.removeEventListener('mousedown', handleClickOutside)
  // 清理音频资源，避免内存泄漏
  if (scriptProcessorNode) {
    scriptProcessorNode.disconnect()
    scriptProcessorNode = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
})

/** 处理键盘事件 */
const handleKeydown = (event: KeyboardEvent) => {
  const isAltPressed = event.altKey || event.keyCode === 18 // 18 是 Alt 键的 keyCode
  const isEnterPressed = event.key === 'Enter' || event.keyCode === 13 // 13 是 Enter 键的 keyCode

  // 检测 Alt + Enter
  if (isAltPressed && isEnterPressed) {
    return
  }

  // 检测普通 Enter
  if (isEnterPressed && !isAltPressed) {
    event.preventDefault()
    onEnter()
  }
}

// 点击发送
const onEnter = () => {
  const hasText = !!inputValue.value
  const hasFiles = selectedFiles.value.length > 0
  if ((!hasText && !hasFiles) || chatStore.pageLoading) return

  const opts = selectedModeId.value != null ? { modeId: selectedModeId.value } : undefined

  if (hasText) {
    chatStore.sendQuestion(
      inputValue.value,
      aiteList.value,
      hasFiles ? selectedFiles.value : undefined,
      opts
    )
    inputValue.value = ''
  } else if (hasFiles) {
    chatStore.sendQuestion('', aiteList.value, selectedFiles.value, { silent: true, ...opts })
  }

  aiteList.value = []
  selectedFiles.value = []
}

/** 点击开关按钮抽屉 */
const showBox = (
  item: 'SubscriptionScene' | 'CommonScene' | 'ZoneScene' | 'more' | 'uploads' | ''
) => {
  // console.log(otherBtn.value != item)
  // console.log('🚀 ~ showBox ~ item:', otherBtn.value, item)
  if (otherBtn.value != item) {
    otherBtn.value = item
  } else {
    otherBtn.value = ''
  }
  // console.log('🚀 ~ showBox ~ otherBtn:', otherBtn.value != item, otherBtn.value)
}

/** 语音识别 */

const isRecording = ref(false) // 是否正在录音
let audioContext: AudioContext | null = null
let scriptProcessorNode: ScriptProcessorNode | null = null
let mediaStream: MediaStream | null = null
let audioChunks: ArrayBuffer[] = []

const getWebSocketUrl = () => {
  const url = 'wss://iat-api.xfyun.cn/v2/iat'
  const host = 'iat-api.xfyun.cn'
  const apiKey = 'b7a322ab53305024e37389b8fc699249'
  const apiSecret = 'ZWJiZmQ3YTRhOTdkYjE2NjllY2VlMDYw'
  const date = new Date().toUTCString()
  const algorithm = 'hmac-sha256'
  const headers = 'host date request-line'
  const signatureOrigin = `host: ${host}\ndate: ${date}\nGET /v2/iat HTTP/1.1`
  const signatureSha = CryptoJS.HmacSHA256(signatureOrigin, apiSecret)
  const signature = CryptoJS.enc.Base64.stringify(signatureSha)
  const authorizationOrigin = `api_key="${apiKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`
  const authorization = btoa(authorizationOrigin)
  return `${url}?authorization=${authorization}&date=${date}&host=${host}`
}

// PC端语音按钮：mousedown时开始录音，并在window上监听mouseup以防止鼠标移出按钮后无法停止录音
const handleVoiceMouseDown = () => {
  startRecording()
  const onMouseUp = () => {
    stopRecording()
    window.removeEventListener('mouseup', onMouseUp)
  }
  window.addEventListener('mouseup', onMouseUp)
}

// 开始录音
const startRecording = async () => {
  audioChunks = []
  isRecording.value = true
  try {
    uni.showToast({ title: '开始录音...', icon: 'none', duration: 1000 })
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        sampleSize: 16,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    })

    audioContext = new AudioContext({ sampleRate: 16000 })
    const source = audioContext.createMediaStreamSource(mediaStream)
    scriptProcessorNode = audioContext.createScriptProcessor(4096, 1, 1)

    scriptProcessorNode.onaudioprocess = event => {
      const inputData = event.inputBuffer.getChannelData(0)
      const buffer = new ArrayBuffer(inputData.length * 2)
      const view = new DataView(buffer)
      for (let i = 0; i < inputData.length; i++) {
        const sample = Math.max(-1, Math.min(1, inputData[i]))
        view.setInt16(i * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
      }
      audioChunks.push(buffer)
    }

    source.connect(scriptProcessorNode)
    scriptProcessorNode.connect(audioContext.destination)
  } catch (error) {
    uni.showToast({ title: '无法访问麦克风', icon: 'error' })
    console.error('无法访问麦克风：', error)
    isRecording.value = false
  }
}

// 停止录音并发送数据
const stopRecording = () => {
  if (!isRecording.value) return
  isRecording.value = false
  uni.showToast({ title: '录音结束，识别中...', icon: 'none', duration: 1500 })
  if (scriptProcessorNode) {
    scriptProcessorNode.disconnect()
    scriptProcessorNode = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
  // 停止所有音频轨道，释放麦克风
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }

  const mergedArrayBuffer = mergeArrayBuffers(audioChunks)
  if (mergedArrayBuffer.byteLength > 0) {
    sendAudioDataToServer(mergedArrayBuffer)
  }
}

// 合并音频数据块
const mergeArrayBuffers = (chunks: ArrayBuffer[]): ArrayBuffer => {
  const totalLength = chunks.reduce((acc, chunk) => acc + chunk.byteLength, 0)
  const result = new Uint8Array(totalLength)
  let offset = 0
  for (const chunk of chunks) {
    result.set(new Uint8Array(chunk), offset)
    offset += chunk.byteLength
  }
  return result.buffer
}

// ArrayBuffer 转 Base64
const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
  let binary = ''
  const bytes = new Uint8Array(buffer)
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

// 发送音频数据到服务器
const sendAudioDataToServer = (audioData: ArrayBuffer) => {
  const wsUrl = getWebSocketUrl()
  const socket = new WebSocket(wsUrl)
  let resultText = '' // 累积识别结果
  let tempText = '' // 当前中间结果（可能被修正）

  let sendTimer: ReturnType<typeof setTimeout> | null = null

  socket.onopen = () => {
    const chunkSize = 1280
    const uint8Array = new Uint8Array(audioData)
    let offset = 0

    const sendNextChunk = () => {
      if (offset >= uint8Array.length) {
        console.log('音频数据发送完成')
        return
      }

      // 连接已关闭则停止发送
      if (socket.readyState !== WebSocket.OPEN) {
        return
      }

      const chunk = uint8Array.slice(offset, offset + chunkSize)
      const base64Chunk = arrayBufferToBase64(chunk)

      const requestData =
        offset === 0
          ? {
              common: { app_id: 'bbd25908' },
              business: {
                language: 'zh_cn',
                domain: 'iat',
                accent: 'mandarin',
                vad_eos: 5000,
                dwa: 'wpgs',
                ptt: 0
              },
              data: {
                status: 0,
                format: 'audio/L16;rate=16000',
                encoding: 'raw',
                audio: base64Chunk
              }
            }
          : {
              data: {
                status: offset + chunkSize >= uint8Array.length ? 2 : 1,
                format: 'audio/L16;rate=16000',
                encoding: 'raw',
                audio: base64Chunk
              }
            }

      socket.send(JSON.stringify(requestData))
      offset += chunkSize
      sendTimer = setTimeout(sendNextChunk, 10)
    }

    sendNextChunk()
  }

  socket.onclose = () => {
    if (sendTimer) clearTimeout(sendTimer)
    console.log('WebSocket 连接已关闭')
  }

  socket.onmessage = event => {
    const jsonData = JSON.parse(event.data)
    if (jsonData.data && jsonData.data.result) {
      const data = jsonData.data.result
      let str = ''
      const ws = data.ws
      for (let i = 0; i < ws.length; i++) {
        str += ws[i].cw[0].w
      }
      if (str.length) {
        // pgs="apd"表示追加结果，pgs="rpl"表示替换之前的临时结果
        if (data.pgs === 'apd') {
          // 将上一段临时结果确认追加到最终结果
          resultText += tempText
          tempText = str
        } else if (data.pgs === 'rpl') {
          // 替换当前临时结果
          tempText = str
        } else {
          // 非wpgs模式或最后一条结果，直接追加
          resultText += str
        }
        inputValue.value = resultText + tempText
      }
    }
  }

  socket.onerror = error => {
    if (sendTimer) clearTimeout(sendTimer)
    console.error('WebSocket 错误：', error)
  }
}
</script>

<template>
  <div class="input-module-container">
    <div class="max-w-4xl mx-auto relative">
      <!-- 桌面端功能按钮区域 -->
      <!-- <div class="feature-buttons">
        <view class="feature-item group">
          <div class="feature-icon shadow-md group-hover:scale-110 transition-all">
            <Conference class="svg-class" />
          </div>
          <span class="text-[10px] text-slate-500 font-medium group-hover:text-slate-700"
            >会议记录</span
          ></view
        >
        <view class="feature-item group">
          <div class="feature-icon shadow-md group-hover:scale-110 transition-all">
            <Recognition class="svg-class" />
          </div>
          <span class="text-[10px] text-slate-500 font-medium group-hover:text-slate-700"
            >扫码识别</span
          ></view
        ><view class="feature-item group">
          <div class="feature-icon shadow-md group-hover:scale-110 transition-all">
            <Report class="svg-class" />
          </div>
          <span class="text-[10px] text-slate-500 font-medium group-hover:text-slate-700"
            >报告生成</span
          ></view
        ><view class="feature-item group">
          <div class="feature-icon shadow-md group-hover:scale-110 transition-all">
            <Translate class="svg-class" />
          </div>
          <span class="text-[10px] text-slate-500 font-medium group-hover:text-slate-700"
            >语言翻译</span
          >
        </view>
      </div> -->
      <!-- 移动端导航区域 -->
      <div class="mobile-nav">
        <div class="nav-scroll-container">
          <button
            class="nav-item text-xs transition-colors"
            :class="agentDropdownOpen ? 'active' : ''"
            @click="toggleAgentDropdown"
          >
            <Scene class="item-icon" />
            {{ modeOptions.find(m => m.modeId === selectedModeId)?.name || '选择模型' }}
            <svg
              class="item-icon dropdown-arrow"
              :class="{ 'rotate-180': agentDropdownOpen }"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>
          <button
            class="nav-item text-xs transition-colors"
            :class="chatStore.isDeepThink ? 'active' : ''"
            @click="chatStore.setIsDeepThink()"
          >
            <DeepThink class="item-icon" />深度思考
          </button>

          <button
            class="nav-item text-xs transition-colors"
            :class="otherBtn == 'CommonScene' ? 'active' : ''"
            @click="showBox('CommonScene')"
          >
            <Scene class="item-icon" />常用场景
          </button>
          <button
            class="nav-item text-xs transition-colors"
            :class="otherBtn == 'ZoneScene' ? 'active' : ''"
            @click="showBox('ZoneScene')"
          >
            <Address class="item-icon" />地市专区
          </button>
          <button
            class="nav-item text-xs transition-colors"
            :class="otherBtn == 'SubscriptionScene' ? 'active' : ''"
            @click="showBox('SubscriptionScene')"
          >
            <Subscribe class="item-icon" />我的订阅
          </button>
          <!-- <button
            class="nav-item text-xs transition-colors"
            :class="otherBtn == 'more' ? 'active' : ''"
            @click="showBox('more')"
          >
            <More class="item-icon" />更多
          </button> -->
        </div>
        <!-- 下拉菜单放在 scroll-container 外面，避免被 overflow 裁剪 -->
        <div v-if="agentDropdownOpen" class="mobile-agent-dropdown-menu">
          <div
            v-for="mode in modeOptions"
            :key="mode.modeId"
            class="mobile-agent-dropdown-item"
            :class="{ selected: mode.modeId === selectedModeId }"
            @click="selectAgent(mode)"
          >
            {{ mode.name }}
          </div>
        </div>
      </div>
      <!-- 图片预览区域 -->
      <ImagePreview
        :images="selectedImages"
        :files="selectedFiles"
        @remove="removeImage"
        @remove-file="removeFile"
      />
      <!-- 弹窗选择区域 -->
      <div
        ref="selectionModalRef"
        class="selection-modal shadow-xl custom-scrollbar animate-in slide-in-from-bottom-2 fade-in"
        v-if="
          !!otherBtn &&
          ((otherBtn == 'SubscriptionScene' && mySubscribeList?.length) ||
            (otherBtn == 'CommonScene' && sceneList?.length) ||
            (otherBtn == 'ZoneScene' && cityList?.length) ||
            otherBtn == 'more' ||
            otherBtn == 'uploads')
        "
      >
        <div class="subscription-grid" v-if="otherBtn == 'SubscriptionScene'">
          <div
            v-for="(item, index) in mySubscribeList"
            :key="item.code"
            class="subscription-card active:bg-blue-50"
            @click="choiceOneAite(item)"
          >
            <div class="card-wrap">
              <Common class="card-icon" :style="{ color: item.iconColor }" />
            </div>
            <div>
              <div class="font-bold text-slate-700 text-sm">{{ item.title }}</div>
              <div class="text-xs text-slate-400 mt-0.5 line-clamp-1">
                {{ item.description }}
              </div>
            </div>
          </div>
        </div>
        <div class="scene-section" v-else-if="otherBtn == 'CommonScene'">
          <div
            class="scene-grid active:bg-blue-50"
            v-for="item in sceneList"
            :key="item.code"
            @click="choiceOneAite(item)"
          >
            <div class="scene-wrap">
              <Common class="scene-icon" :style="{ color: item.iconColor }" />
            </div>
            <div class="font-medium text-slate-700 text-xs line-clamp-1">
              {{ item.title }}
            </div>
          </div>
        </div>
        <div class="city-grid" v-else-if="otherBtn == 'ZoneScene'">
          <div
            v-for="item in cityList"
            :key="item.code"
            class="city-item active:bg-blue-50"
            @click="choiceOneAite(item)"
          >
            <div class="font-medium text-slate-700 text-xs">{{ item.title }}</div>
          </div>
        </div>
        <div class="more-grid" v-else-if="otherBtn == 'more'">
          <button class="more-item">
            <div class="icon-wrap">
              <Conference class="svg-class" />
            </div>
            <span class="more-text">会议记录</span>
          </button>
          <button class="more-item">
            <div class="icon-wrap">
              <Recognition class="svg-class" />
            </div>
            <span class="more-text">扫码识别</span>
          </button>
          <button class="more-item">
            <div class="icon-wrap">
              <Report class="svg-class" />
            </div>
            <span class="more-text">报告生成</span>
          </button>
          <button class="more-item">
            <div class="icon-wrap">
              <Translate class="svg-class" />
            </div>
            <span class="more-text">语言翻译</span>
          </button>
        </div>
        <div class="upload-grid" v-else-if="otherBtn == 'uploads'">
          <button class="upload-item">
            <div class="icon-wrap">
              <Picture />
            </div>
            <span class="text">图片</span>
          </button>
          <button class="upload-item">
            <div class="icon-wrap">
              <Link />
            </div>
            <span class="text">文档</span>
          </button>
        </div>
      </div>
      <!-- 桌面端输入框区域 -->
      <div
        class="desktop-input-area shadow-[0_8px_30px_rgb(0,0,0,0.06)] transition-all focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300"
      >
        <div class="pc-special-choice-wrap">
          <div
            v-for="item in aiteList"
            :key="`id${item.code}type${item.type}`"
            class="flex items-center gap-1 bg-blue-50 text-blue-600 px-2 py-0.5 rounded-lg text-xs font-medium shrink-0 select-none animate-in fade-in zoom-in duration-200 h-7"
          >
            <span class="opacity-60">@</span><span>{{ item.title }}</span
            ><button class="ml-1 hover:text-blue-800" @click="deleteOneAite(item)">×</button>
          </div>
        </div>

        <div class="input-container">
          <!-- PC端使用uni-easyinput，支持最多4行 -->
          <uni-easyinput
            v-model="inputValue"
            type="textarea"
            :inputBorder="false"
            autoHeight
            :maxlength="500"
            placeholder="给网络运维超级入口发送消息..."
            class="w-full custom-textarea-height custom-scrollbar"
            @keydown="handleKeydown"
          />
        </div>
        <div class="input-controls">
          <div class="left-controls">
            <div class="agent-dropdown-wrap">
              <button
                class="action-button transition-colors"
                :class="agentDropdownOpen ? 'active' : ''"
                @click="toggleAgentDropdown"
              >
                <Scene class="action-icon" />
                {{ modeOptions.find(m => m.modeId === selectedModeId)?.name || '选择模型' }}
                <svg
                  class="action-icon dropdown-arrow"
                  :class="{ 'rotate-180': agentDropdownOpen }"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              <div v-if="agentDropdownOpen" class="agent-dropdown-menu">
                <div
                  v-for="mode in modeOptions"
                  :key="mode.modeId"
                  class="agent-dropdown-item"
                  :class="{ selected: mode.modeId === selectedModeId }"
                  @click="selectAgent(mode)"
                >
                  {{ mode.name }}
                </div>
              </div>
            </div>
            <button
              class="action-button transition-colors"
              :class="chatStore.isDeepThink ? 'active' : ''"
              @click="chatStore.setIsDeepThink()"
            >
              <DeepThink class="action-icon" />
              深度思考
            </button>
            <!-- <button
              class="action-button transition-colors"
              :class="otherBtn == 'CommonScene' ? 'active' : ''"
              @click="showBox('CommonScene')"
            >
              <Scene class="action-icon" />常用场景
            </button>
            <button
              class="action-button transition-colors"
              :class="otherBtn == 'ZoneScene' ? 'active' : ''"
              @click="showBox('ZoneScene')"
            >
              <Address class="action-icon" />地市专区
            </button>
            <button
              class="action-button transition-colors"
              :class="otherBtn == 'SubscriptionScene' ? 'active' : ''"
              @click="showBox('SubscriptionScene')"
            >
              <Subscribe class="action-icon" />我的订阅
            </button> -->
          </div>
          <div class="right-controls">
            <button class="icon-button" @mousedown="handleVoiceMouseDown">
              <Voice class="icon" /></button
            ><button class="icon-button" @click="chooseImage(['album'])">
              <Picture class="icon" /></button
            ><button class="icon-button" @click="chooseFile">
              <Link class="icon" />
            </button>
            <div class="dividing-line"></div>
            <button
              class="send-icon"
              :class="inputValue || selectedFiles.length ? 'active' : ''"
              @click="onEnter"
            >
              <Send class="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
      <!-- 移动端输入区域 -->
      <div class="mobile-input-area">
        <view class="add-button transition-colors" @click="handleAddClick">
          <Add class="w-6 h-6" />
        </view>
        <div class="mobile-input-container">
          <div class="special-choice-wrap custom-scrollbar">
            <div
              v-for="item in aiteList"
              :key="`id${item.code}type${item.type}`"
              class="special-item font-medium shrink-0 select-none animate-in fade-in zoom-in duration-200"
            >
              <span class="text-xs">{{ `@${item.title}` }}</span
              ><button
                class="ml-0.5 text-sm hover:text-blue-800 p-0.5"
                @click="deleteOneAite(item)"
              >
                ×
              </button>
            </div>
          </div>
          <div class="mobile-input">
            <uni-easyinput
              v-model="inputValue"
              type="textarea"
              :inputBorder="false"
              autoHeight
              :maxlength="500"
              placeholder="给网络运维超级入口发送消息..."
              class="w-[80%] custom-mobile-textarea-height no-scrollbar"
            />
            <view
              class="voice-button transition-colors"
              @touchstart="startRecording"
              @touchend="stopRecording"
            >
              <Voice2 class="w-6 h-6" />
            </view>
            <!-- <view
              class="text-slate-400 hover:text-slate-600 flex-shrink-0 ml-auto"
              @click.stop="showBox('uploads')"
            >
              <Add class="w-5 h-5" />
            </view> -->
          </div>
          <!-- 移动端使用uni-easyinput -->
        </div>
        <button
          class="mobile-send-button shadow-sm transition-all"
          :class="inputValue || selectedFiles.length ? 'active' : ''"
          @click="onEnter"
        >
          <Send />
        </button>
      </div>
      <Footer />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.input-module-container {
  padding: 0;
  width: 100%;
  z-index: 30;
  background-color: #fff;
  border-top: 1px solid #f1f5f9;
  .feature-buttons {
    display: none;
    justify-content: center;
    margin-bottom: 32rpx;
    gap: 24rpx;
    flex-wrap: wrap;
    .feature-item {
      gap: 8rpx;
      display: flex;
      flex-direction: column;
      &:nth-child(1) .svg-class {
        color: #3b82f6; // Conference - blue-500
      }

      &:nth-child(2) .svg-class {
        color: #6366f1; // Recognition - indigo-500
      }

      &:nth-child(3) .svg-class {
        color: #10b981; // Report - green-500
      }

      &:nth-child(4) .svg-class {
        color: #f97316; // Translate - orange-500
      }
      .feature-icon {
        width: 80rpx;
        height: 80rpx;
        border-radius: 50%;
        background-color: #fff;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: center;
        align-items: center;
        .svg-class {
          width: 40rpx;
          height: 40rpx;
        }
      }
    }
  }
  .mobile-nav {
    padding: 16rpx 32rpx 24rpx 32rpx;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    .nav-scroll-container {
      display: flex;
      gap: 16rpx;
      overflow-x: auto;
      width: 100%;
      max-width: 100%;
      scrollbar-width: none;
      .dropdown-arrow {
        transition: transform 0.2s ease;
      }
      .nav-item {
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        gap: 8rpx;
        padding: 12rpx 24rpx;
        border-radius: 50rem;
        white-space: nowrap;
        border: 1px solid #e2e8f0;
        background-color: #f8fafc;
        color: #475569;
        &.active {
          border: 1px solid #c7d2fe;
          background-color: #dbeafe;
          color: #2563eb;
        }
        .item-icon {
          width: 28rpx;
          height: 28rpx;
        }
      }
    }
    .mobile-agent-dropdown-menu {
      position: absolute;
      bottom: calc(100% + 8rpx);
      left: 32rpx;
      background-color: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 24rpx;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
      padding: 8rpx 0;
      z-index: 60;
      min-width: 240rpx;
      .mobile-agent-dropdown-item {
        padding: 20rpx 32rpx;
        font-size: 24rpx;
        color: #475569;
        white-space: nowrap;
        transition: background-color 0.15s ease;
        &:active {
          background-color: #f1f5f9;
        }
        &.selected {
          color: #2563eb;
          background-color: #eff6ff;
          font-weight: 500;
        }
      }
    }
  }
  .selection-modal {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    margin: 16rpx;
    margin-top: 0;
    background-color: #fff;
    border-radius: 32rpx;
    border: 1px solid #e2e8f0;
    padding: 32rpx;
    z-index: 50;
    max-height: 16rem;
    overflow-y: auto;
    .subscription-grid {
      display: grid;
      grid-template-columns: repeat(1, minmax(0, 1fr));
      gap: 16rpx;
      margin-bottom: 40rpx;
      .subscription-card {
        // active:bg-blue-50
        background-color: #f8fafc;
        border: 1px solid #e2e8f0; // border border-slate-100
        border-radius: 24rpx;
        padding: 24rpx;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 24rpx;
        &:hover {
          background-color: rgba(59, 130, 246, 0.2);
        }
        .card-wrap {
          padding: 16rpx;
          background-color: #fff;
          border-radius: 16rpx;
          box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
          color: #475569;

          .card-icon {
            width: 40rpx;
            height: 40rpx;
          }
        }
      }
    }
    .scene-section {
      // grid grid-cols-2 md:grid-cols-4 gap-2
      display: grid;
      gap: 16rpx;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin-bottom: 40rpx;
      .scene-grid {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 24rpx; // rounded-xl
        padding: 24rpx; // p-3
        cursor: pointer; // cursor-pointer
        display: flex; // flex items-center gap-2
        align-items: center;
        gap: 16rpx;
        &:hover {
          background-color: rgba(59, 130, 246, 0.2); // hover:bg-blue-50/50
        }
        .scene-wrap {
          padding: 12rpx;
          background-color: #fff;
          border-radius: 16rpx; // rounded-lg
          box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
          .scene-icon {
            width: 40rpx;
            height: 40rpx;
          }
        }
      }
    }
    .city-grid {
      display: grid; // grid grid-cols-3
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16rpx;
      .city-item {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 24rpx;
        padding: 24rpx;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        &:hover {
          background-color: rgba(59, 130, 246, 0.2); // hover:bg-blue-50/50
        }
      }
    }
    .more-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16rpx;
      .more-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16rpx;
        padding: 16rpx;
        &:nth-child(1) .svg-class {
          color: #3b82f6; // Conference - blue-500
        }

        &:nth-child(2) .svg-class {
          color: #6366f1; // Recognition - indigo-500
        }

        &:nth-child(3) .svg-class {
          color: #10b981; // Report - green-500
        }

        &:nth-child(4) .svg-class {
          color: #f97316; // Translate - orange-500
        }
        .icon-wrap {
          width: 80rpx;
          height: 80rpx;
          border-radius: 50%;
          border: 1px solid #f1f5f9;
          background-color: #f8fafc;
          color: #475569;
          display: flex;
          justify-content: center;
          align-items: center;
          .svg-class {
            width: 40rpx;
            height: 40rpx;
          }
        }
        .more-text {
          font-size: 20rpx;
          color: #475569;
        }
      }
    }
    .upload-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16rpx;
      .upload-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16rpx;
        padding: 16rpx;
        .icon-wrap {
          width: 80rpx;
          height: 80rpx;
          border-radius: 50%;
          background-color: #f8fafc;
          border: 1px solid #f1f5f9;
          color: #3b82f6;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .text {
          color: #475569;
          font-size: 20rpx;
        }
      }
    }
  }
  .desktop-input-area {
    //
    display: none;
    background-color: #fff;
    border-radius: 64rpx;
    border: 1px solid rgb(226 232 240 / 0.8);
    flex-direction: column;
    padding: 24rpx;
    gap: 16rpx;
    position: relative;
    .pc-special-choice-wrap {
      display: flex;
      width: 100%;
      justify-content: flex-start;
      align-items: flex-start;
      padding: 0 8rpx;
      flex-wrap: wrap;
      gap: 8rpx;
    }
    .input-container {
      display: flex;
      width: 100%;
      align-items: center;
      padding: 0 8rpx;
      flex-wrap: wrap;
      gap: 8rpx;
    }
    .input-controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 8rpx;
      .left-controls {
        display: flex;
        align-items: center;
        gap: 16rpx;
        flex-wrap: wrap;
        .agent-dropdown-wrap {
          position: relative;
          .dropdown-arrow {
            transition: transform 0.2s ease;
          }
          .agent-dropdown-menu {
            position: absolute;
            bottom: calc(100% + 12rpx);
            left: 0;
            background-color: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 24rpx;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            padding: 8rpx 0;
            z-index: 60;
            min-width: 200rpx;
            .agent-dropdown-item {
              padding: 16rpx 32rpx;
              font-size: 24rpx;
              color: #475569;
              cursor: pointer;
              white-space: nowrap;
              transition: background-color 0.15s ease;
              &:hover {
                background-color: #f1f5f9;
              }
              &.selected {
                color: #2563eb;
                background-color: #eff6ff;
                font-weight: 500;
              }
            }
          }
        }
        .action-button {
          display: flex;
          align-items: center;
          gap: 12rpx;
          padding: 12rpx 24rpx;
          border-radius: 64rpx;
          font-size: 24rpx;
          line-height: 32rpx;
          transition: background-color 0.2s ease;
          background-color: #f8fafc;
          color: #6b7280;
          border: 1px solid #e2e8f0;
          font-weight: 500;

          &:hover {
            background-color: #e2e8f0;
          }
          &.active {
            border: 1px solid #c7d2fe;
            transition: background-color 0.2s ease;
            background-color: #dbeafe;
            color: #2563eb;
            &:hover {
              background-color: #bfdbfe;
            }
          }
          .action-icon {
            width: 28rpx;
            height: 28rpx;
          }
        }
      }
      .right-controls {
        // flex items-center gap-1
        display: flex;
        align-items: center;
        gap: 8rpx;
        .icon-button {
          color: #94a3b8;
          transition: all 0.2s ease;
          padding: 16rpx;
          border-radius: 50%;
          &:hover {
            background-color: #e2e8f0;
            color: #3b82f6;
          }
          // icon-button
          .icon {
            width: 40rpx;
            height: 40rpx;
          }
        }
        .dividing-line {
          width: 1px;
          height: 48rpx;
          background-color: #e2e8f0;
          margin: 0 8rpx;
        }
        .send-icon {
          background-color: #e2e8f0;
          padding: 16rpx;
          border-radius: 50%;
          color: #94a3b8;
          cursor: not-allowed;
          &.active {
            background-color: #2563eb;
            color: #fff;
            cursor: pointer;
          }
        }
      }
    }
  }
  .mobile-input-area {
    display: flex; // flex items-end gap-2
    align-items: flex-end;
    gap: 16rpx;
    padding: 24rpx;
    padding-top: 16rpx;
    background-color: #fff;
    border-top: 1px solid #e2e8f0;
    .add-button {
      margin-bottom: 16rpx;
      color: #64748b; // text-slate-500
      padding: 8rpx;
      &:hover {
        color: #334155;
      }
    }
    .voice-button {
      color: #64748b; // text-slate-500
      padding: 8rpx;
      &:hover {
        color: #334155;
      }
    }
    .mobile-input-container {
      flex: 1;
      background-color: #f1f5f9;
      border-radius: 1rem;
      padding: 16rpx 24rpx;
      // display: flex;
      // align-items: center;
      // flex-wrap: wrap;
      // gap: 16rpx;
      min-height: 44px;
      .mobile-input {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 16rpx;
        min-height: 44px;
      }
      .special-choice-wrap {
        max-height: 200rpx;
        overflow-y: auto;
        display: flex;
        gap: 8rpx;
        justify-content: flex-start;
        align-items: flex-start;
        flex-wrap: wrap;
        .special-item {
          //   select-none animate-in fade-in zoom-in duration-200
          display: flex;
          align-items: center;
          gap: 8rpx;
          background-color: #dbeafe;
          color: #2563eb;
          padding: 4rpx 16rpx;
          border-radius: 12rpx;
          flex-shrink: 0;
          // inline-block max-w-[130rpx] truncate 如果控制长度的话
          .delete-icon {
          }
        }
      }
    }
    .mobile-send-button {
      // mb-1 p-2.5 rounded-full shadow-sm flex items-center justify-center transition-all bg-slate-200 text-slate-400
      margin-top: 8rpx;
      padding: 20rpx;
      border-radius: 50%;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #e2e8f0;
      color: #94a3b8;
      cursor: not-allowed;
      &.active {
        background-color: #2563eb;
        color: #fff;
        cursor: pointer;
      }
    }
  }
}

@media (min-width: 768px) {
  .input-module-container {
    padding: 32rpx 48rpx 64rpx 48rpx;
    background-color: transparent;
    border: none;
    .feature-buttons {
      display: flex;
      gap: 48rpx;
      align-items: center;
    }
    .mobile-nav {
      display: none;
    }
    .selection-modal {
      .subscription-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
      .scene-section {
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }
      .city-grid {
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }
    }
    .desktop-input-area {
      display: flex;
    }
    .mobile-input-area {
      display: none;
    }
  }
}
// 专门针对自定义高度的textarea样式（使用rpx单位）
::v-deep .custom-textarea-height {
  & .uni-easyinput__content.is-textarea {
    min-height: 88rpx !important; // 44px转换为rpx（按1:2比例）
    .uni-textarea-placeholder {
      font-size: 32rpx !important;
    }

    & textarea {
      min-height: 40rpx !important; // 最小高度
      max-height: 160rpx !important; /* 4行的高度，每行约40rpx */
      overflow-y: auto !important;
      resize: none;
      font-size: 32rpx !important; // 确保字体大小
      line-height: 40rpx !important; // 行高
    }
  }
}
::v-deep .custom-mobile-textarea-height {
  & .uni-easyinput__content.is-textarea {
    // min-height: 44px !important;
    background-color: #f1f5f9 !important;
    .uni-textarea-placeholder {
      font-size: 30rpx !important;
    }

    & textarea {
      background-color: #f1f5f9 !important;
      font-size: 30rpx !important;
      line-height: 36rpx !important;
      min-height: 36rpx !important;
      max-height: 108rpx !important;
      overflow-y: auto !important;
      resize: none;
      padding: 0 !important;
    }

    // 隐藏滚动条
    & textarea::-webkit-scrollbar {
      display: none;
    }
  }
}
</style>
