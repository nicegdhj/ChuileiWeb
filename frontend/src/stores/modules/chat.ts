import { defineStore } from 'pinia'
import { onMounted, ref } from 'vue'
import { useSessionStore } from './session'
import { v4 as uuidv4 } from 'uuid'
import { request } from '@/utils/http'
import { getClientId } from '@/utils/client_id'
// import { useMemberStore } from './member'
import { data } from '@/static/subParams'
import { htmlParams1 } from '@/static/htmlParams'
import dayjs from 'dayjs'

type aite_type = {
  code?: number
  title?: string
  type?: number
  description?: string
  iconColor?: string
  name?: string[]
}

interface session_list_type {
  sessionId: string
  title: string
  latestCreateTime?: string
}

export const useChatStore = defineStore('chat', () => {
  /** 会话记录列表 */
  const sessionList = ref<session_list_type[]>([])

  const getSessionList = async () => {
    const { code, data, message } = await request<Response<session_list_type[]>>({
      url: `/sessions`,
      method: 'GET'
    })
    if (code == '00000') {
      sessionList.value = data
      return data
    } else {
      // uni.showToast({ icon: 'error', title: message || '请求失败' })
    }
  }

  const sessionStore = useSessionStore()
  onMounted(async () => {
    sessionStore.changeSelectedSessionId(uuidv4())
    try {
      await new Promise(resolve => setTimeout(resolve, 100))
      const list = await getSessionList()
      // 如果最新会话不超过半小时，则加载该会话内容；否则为新会话
      if (list && list.length > 0) {
        const latest = list[0]
        const diffMin = dayjs().diff(dayjs(latest.latestCreateTime), 'minute')
        if (diffMin <= 30) {
          sessionStore.changeSelectedSessionId(latest.sessionId)
          getDialogList(latest.sessionId)
        }
      }
    } catch (e) {
      console.warn('API不可用，使用mock数据')
    }
    // 使用 htmlParams 模拟流式输出
    // setTimeout(() => mockStreamChat(), 1500)
  })
  /** 当前的对话id */
  const currentMessageId = ref<string>('')
  const changeMessageId = (item: string) => {
    currentMessageId.value = item
  }

  const isDeepThink = ref(true)
  const setIsDeepThink = () => {
    isDeepThink.value = !isDeepThink.value
  }
  /** 当前的输入问题回答状态，true表示正在进行中 */
  const pageLoading = ref(false)
  const currentPrompt = ref('')
  const currentAite = ref<aite_type[]>([])
  //   对话数据列表
  const dialogList = ref<Chat.ChatItem[]>([
    // {
    //   id: 1770714672586,
    //   content:
    //     '你好是叫什么名字，你好是叫什么名字，你好是叫什么名字，你好是叫什么名字，你好是叫什么名字，你好是叫什么名字，',
    //   type: 'question'
    // },
    // {
    //   id: 1770714672587,
    //   content:
    //     // '  \n"政企终端类产品的开通时限要求如下：\\n\\n1、E企组网：\\n   - 组网与线路融合开通：安装时限同线路；\\n   - 组网加装：自预约上门时间起36小时；\\n   - 对于一次新装台数比较多（6台以上）的场景，可根据业务部门与客户商定的具体开通时限执行。\\n\\n2、专线卫士：\\n   - 基础版/增强版：3个工作日；\\n   - 增值套餐-装维服务：5个工作日。\\n\\n3、SD-WAN：\\n   - 组网：VPN开通1个工作日；CPE开通跨省4个工作日、跨地市/地市内3个工作日、跨境运输时间+5个工作日；\\n   - 入云：跨省9个工作日、跨地市/地市内6个工作日；\\n   - 国际快线：跨省4个工作日、跨地市/地市内3个工作日。\\n\\n4、千里眼：\\n   - 加装（线路已具备）：城区3个工作日、农村4个工作日；\\n   - 融合开通（接入线路有资源）：4个工作日。\\n\\n5、云视讯：\\n   - 加装（线路已具备）：AAA级2个工作日、AA级/A级/普通3个工作日；\\n   - 融合开通（接入线路有资源）：以相应接入线路开通时限为基础增加1个工作日。\\n\\n参考文献：政企专线智能问答语料整理V1.3@20250603.xlsx"',
    //     // 'UDM（Unified Data Management）上云后，语音业务（如VoLTE/VoNR）的接续时延增加200-300毫秒，这是一个比较典型的性能问题。这种时延增加通常与信令流程中新增的交互环节、网络路径变化、协议适配或数据同步机制有关。以下是可能造成时延增加的主要原因和分析方向：\n\n---\n\n### 一、可能引入的新增交互环节1. **UDM与AUSF分离导致的额外鉴权流程**\n - 在传统HSS中，鉴权和用户数据是合设的，而在5G架构中，AUSF（Authentication Server Function）和UDM是分离的。\n - 当UDM上云后，若AUSF仍保留在本地或与UDM不在同一区域，会引入额外的Nudm接口交互（如AUSF向UDM请求鉴权向量）。\n - **新增交互**：AUSF → UDM（跨DC或跨区域）→ AUSF，增加RTT（往返时延）。\n\n2. **Nudm_SDM_Get / Nudm_UECM_Registration 等服务化接口调用**\n - 在注册或会话建立时，AMF/SMF需要通过Nudm接口向UDM获取用户签约数据（如S-NSSAI、DNN、QoS模板等）。\n - 若UDM部署在远端（如公有云或异地DC），网络传输时延显著增加。\n - **典型新增时延**：跨DC通信可能增加50~200ms RTT。\n\n3. **签约数据同步延迟或缓存失效**\n - UDM上云后，若未启用本地缓存或缓存策略不合理，每次呼叫或注册都需实时查询UDM。\n - 特别是在语音呼叫建立时，S-CSCF或VoLTE AS可能需要通过Diameter或HTTP/2向UDM获取用户数据。\n - 若无缓存或缓存更新机制不完善，会导致重复查询。\n\n4. **Diameter与HTTP/2协议转换带来的开销**\n -传统IMS使用Diameter协议，而5G服务化接口使用HTTP/2。\n - 若UDM上云后，DRA或BSF需要进行协议转换或路由重定向，会引入额外处理时延。\n -例如：DRA → UDM（云上）→ DRA → CSCF，路径变长。\n\n5. **跨域路由或NRF发现机制引入的延迟**\n - UDM上云后，AMF/SMF需通过NRF（Network Repository Function）发现UDM实例。\n - NRF查询（Nnrf_NFDiscovery）本身会增加1~2个消息往返。\n - 若NRF部署在远端或响应慢，会显著增加注册或会话建立时延。\n\n---\n\n### 二、典型语音流程中的时延增长点以VoLTE/VoNR呼叫建立流程为例：\n\n| 步骤 |传统HSS本地部署 | UDM上云后变化 |时延影响 |\n|------|------------------|----------------|----------|\n|1. IMS注册 | HSS本地响应 | 需跨DC访问UDM | +50~150ms |\n|2. 鉴权流程 | AUSF与HSS合设 | AUSF → UDM（云） | +50~100ms |\n|3. 签约数据获取 |本地Diameter响应 | Nudm_SDM_Get（HTTP/2） | +100~200ms |\n|4. 呼叫建立 |本地路由 | 可能涉及BSF、DRA转发 | +50ms |\n\n> 合计新增时延：**200~400ms**，与现场反馈吻合。\n\n---\n\n### 三、可能的根因总结 \n | 原因 |说明 | 解决建议 |\n|------|------|----------|\n| **跨DC通信延迟** | UDM部署在远端，网络RTT高 |优化网络路径，部署边缘UDM或本地缓存 |\n| **服务化接口调用增加** | Nudm接口调用次数增多 | 合并请求、启用缓存、优化NRF发现 |\n| **鉴权流程分离** | AUSF与UDM分离导致额外交互 | 合理部署AUSF与UDM在同一区域 |\n| **缓存机制缺失** | 每次呼叫都查询UDM | 在CSCF/AS启用UDM数据缓存 |\n| **协议转换开销** | Diameter ↔ HTTP/2转换 |优化DRA/BSF性能，减少跳数 |\n\n---\n\n### 四、优化建议1. **启用UDM数据缓存**\n - 在S-CSCF、VoLTE AS、AMF/SMF中启用对UDM签约数据的本地缓存（TTL合理设置）。\n\n2. **优化网络部署**\n - 将UDM/AUSF部署在靠近核心网的区域（如边缘云或区域DC），减少跨DC通信。\n\n3. **NRF优化**\n - 配置NRF本地缓存，减少NF发现时延。\n - 使用静态配置替代动态发现（在稳定网络中）。\n\n4. **协议优化**\n - 减少Diameter与HTTP/2之间的转换跳数。\n - 使用DRA的智能路由功能，避免迂回。\n\n5. **性能监控与信令分析**\n - 使用EMS/OMC抓包分析信令流程，定位具体时延增长环节。\n - 对比上云前后关键节点（如注册、呼叫建立）的时延差异。\n\n---\n\n### 结论UDM上云后语音时延增加200~300ms，**主要原因是新增了服务化接口交互（如Nudm_SDM_Get）、跨DC通信延迟、AUSF与UDM分离导致的额外鉴权流程，以及可能的缓存缺失**。建议从网络部署、缓存机制、协议优化等方面入手进行针对性优化。\n\n如需进一步定位，建议抓取典型呼叫的信令流程（如INVITE到180 Ringing之间），分析各环节耗时。',
    //     '<b>业务信息概要：</b><b>&emsp;用户信息：</b>\n&emsp;&emsp;用户 IMSI：4600846<b>&emsp;终端信息:</b>\n&emsp;&emsp;5GNSA能力: 不支持&emsp;&emsp;5GSA能力：不支持<b>&emsp;网络信息：</b>\n&emsp;&emsp;业务发起TAC区：6737&emsp;&emsp;业务发起小区：262824577&emsp;<b>关键流程信息：</b>\n&emsp;&emsp;1、UE向MME发起Attach流程&emsp;&emsp;2、UE向MME发起PDN Connectivity流程<b>异常根因推理：</b><b>第1个流程：Attach</b>&emsp;&emsp;问题分析：2024-06-0214:09:02.201 RAN（10.106.177.131）向 APP-HDNJIHzjAMFm005BHW-07AHW011发起Attach流程，2024-06-0214:09:02.687 DFMHSS05FE01AZX向APP-HDNJIHhd',
    //   //       content: `**杭州的一级告警详情是什么**
    //   // | 序号 | 业务的影响 | 告警标题 | 原始告警流水号 | 告警定位信息 | 地市 | 网元名称 | 设备类型 | 网络专业 | 告警最后发生时间 | 网络类型 | 告警级别 | 资源池 | 机房名称 | 告警处理建议 |
    //   // | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    //   // | 1 | 未知 | Boot密码为默认密码 | 1391432221 | 核心网-5GTOC:10.211.53.90:null | 杭州市 | ZJHZ-GI-GPRS-FW59-SQHW | 防火墙 | 核心网 | 2026-02-11 10:12:07 | 配套设备 | PS_CRITICAL | 未知 | 杭州石桥枢纽三号楼4楼机房 | 未知 |`,
    //   // content:
    //   //   '这是一个简单的示例，展示了如何在 Markdown 中混合使用文字和表格。\n\n## 项目介绍\n\n以下是我们的产品列表，包括价格和库存信息：\n\n| 项目   | 描述         | 价格   | 库存 |\n|--------|--------------|--------|------|\n| 苹果   | 新鲜红富士   | ¥12.5  | 50   |\n| 香蕉   | 海南香蕉     | ¥8.0   | 30   |\n| 橙子   | 赣南脐橙     | ¥15.0  | 20   |\n\n我们还提供高质量的产品图片：\n\n![水果图片](https://picsum.photos/200/300 "水果展示")[📥 点击下载文件](https://picsum.photos/200/300)\n\n### 说明\n\n- **苹果**：产自山东，口感脆甜。\n- **香蕉**：来自海南，营养丰富。\n- **橙子**：江西赣州特产，汁多味甜。\n\n如有任何问题，请随时联系我们！',
    //   type: 'answer',
    //   answerType: 'markdown',
    //   loadingTexts: [
    //     { id: 0, value: '规划中......' },
    //     {
    //       id: 1,
    //       value:
    //         "任务规划候选的工具/智能体集: ['日报问答', '性能指标查询', '台风场景问答', '统一知识库问答', '图表绘制工具', '任务终止工具', '家宽服务质量指标查询', '项目介绍工具']"
    //     },
    //     { id: 2, value: "最终选中的工具/智能体集：['项目介绍工具']" },
    //     { id: 3, value: '调用：项目介绍工具 结束', type: 'endNode' }
    //   ],
    //   reasoning: '测试深度思考文案'
    // }
  ])

  const getDialogList = async (sessionId?: string) => {
    if (!sessionId) return
    const { code, data, message } = await request<
      Response<
        {
          role: 'user' | 'assistant'
          content: string
          messageId: string
        }[]
      >
    >({
      url: `/sessions/${sessionId}/messages`,
      method: 'GET'
    })
    if (code == '00000') {
      const dataList = data || []
      const list: Chat.ChatItem[] = []

      let lastAssistantMerged = false

      dataList.forEach((item: any, index: number) => {
        if (item.role === 'user') {
          lastAssistantMerged = false
          list.push({
            id: item.messageId,
            content: item.content,
            type: 'question'
          })
        } else {
          // AI 回答
          const normalizedType = (item.type || '').toLowerCase()

          // xinLing 类型：不在聊天框显示，直接跳过
          if (normalizedType === 'xinling') {
            return
          }

          // 数据类型：不在聊天框显示，仅存储到 dataParams
          if (
            normalizedType === 'diagnosis_data_params' ||
            normalizedType === 'todo_ticket_data_params'
          ) {
            try {
              const parsed = JSON.parse(item.content)
              Object.keys(parsed).forEach(key => {
                dataParams.value[key] = parsed[key]
              })
            } catch (e) {
              console.error('解析数据参数失败:', e)
            }
            return // 跳过，不加入对话列表
          }

          // cardBtn 类型：解析选项按钮，与前面的 markdown 合并到同一气泡
          if (normalizedType === 'cardbtn' && typeof item.content === 'string') {
            try {
              const parsed = JSON.parse(item.content) as Chat.AiOptionContent
              // 找到前一条 answer 类型的消息，将 optionContent 合并上去
              for (let i = list.length - 1; i >= 0; i--) {
                if (list[i].type === 'answer') {
                  list[i].optionContent = parsed
                  break
                }
              }
            } catch (e) {
              console.error('解析 cardBtn 失败:', e)
            }
            return // 跳过，不单独加入对话列表
          }

          // 合并逻辑：当前 html 且上一条是未合并的 answer(markdown/null) → 合并到一个气泡
          if (normalizedType === 'html' && !lastAssistantMerged && list.length > 0) {
            const lastMsg = list[list.length - 1]
            if (lastMsg.type === 'answer') {
              lastMsg.content += item.content
              lastAssistantMerged = true
              return
            }
          }

          // 处理 think/reasoning 内容，将转义的换行符转换为真实换行符
          const contentList = item.content.replace(/\\n/g, '\n').split('区块')
          let thinkContent = ''
          let content = ''

          if (contentList.length > 1) {
            thinkContent = contentList[0].replace('在此', '')
            if (thinkContent === ' ' || thinkContent === '\n' || thinkContent === '\n\n') {
              thinkContent = ''
            }
            content = contentList[1]
          } else {
            content = contentList[0]
          }

          // 根据 type 决定渲染方式：html → html 气泡，其余 → answer 文本气泡
          const displayType: 'answer' | 'html' = normalizedType === 'html' ? 'html' : 'answer'
          if (displayType === 'answer') lastAssistantMerged = false

          const answerType = item?.type || item?.answerType || 'markdown'
          list.push({
            id: item.messageId,
            content: parseJiakuanContentIfNeeded(answerType, content),
            type: displayType,
            loadingTexts:
              item?.intent && item?.intent.length
                ? item.intent.map((intentItem: string) => JSON.parse(intentItem))
                : [],
            answerType,
            reasoning: thinkContent
          })
        }
      })
      dialogList.value = list
    } else {
      // uni.showToast({ icon: 'error', title: message || '请求失败' })
    }
  }

  /** 清除对话列表 */
  const cleanDialog = () => {
    currentAite.value = []
    currentPrompt.value = ''
    pageLoading.value = false
    dialogList.value = []
    dataParams.value = {}
    stopLoadingPolling() // 清除轮询，避免内存泄漏
  }

  const deleteSession = async (sessionId: string) => {
    try {
      await request<Response<null>>({
        url: `/sessions/${sessionId}`,
        method: 'DELETE'
      })
    } catch (_e) {
      // 乐观删除，忽略网络错误
    }
    sessionList.value = sessionList.value.filter(s => s.sessionId !== sessionId)
    if (sessionStore.currentSessionId === sessionId) {
      if (sessionList.value.length > 0) {
        const next = sessionList.value[0]
        sessionStore.changeSelectedSessionId(next.sessionId!)
        cleanDialog()
        getDialogList(next.sessionId)
      } else {
        sessionStore.changeSelectedSessionId(uuidv4())
        cleanDialog()
      }
    }
  }

  // 存储 loadingText 数组
  const loadingTexts = ref<
    {
      id: number
      value: string
      type?: string
    }[]
  >([])
  /** 存储流式响应中 data-params 第二条消息的数据 */
  const dataParams = ref<
    Record<
      string,
      {
        name: string
        th: Array<{ en: string; zh: string }>
        td: Array<Record<string, any>>
      }
    >
  >({})
  /** 泳道图数据（xinLing 类型响应时不展示在聊天框，直接弹出泳道图） */
  const swimlaneChartData = ref<any>(null)
  const clearSwimlaneChart = () => {
    swimlaneChartData.value = null
  }
  // 定时器 ID
  let loadingPollingTimer: number | null = null

  const startLoadingPolling = async () => {
    if (loadingPollingTimer) return // 避免重复启动

    const poll = async () => {
      try {
        const { code, data, message } = await request<
          Response<
            {
              id: number
              value: string
              type?: string
            }[]
          >
        >({
          url: '/scene/use',
          method: 'POST',
          header: {
            'Content-Type': 'application/json' // 设置请求头
          },
          data: {
            sessionId: sessionStore.currentSessionId,
            messageId: currentMessageId.value
          }
        })
        if (code == '00000') {
          dialogList.value[dialogList.value.length - 1].loadingTexts = data.map(item =>
            JSON.parse(item)
          )
        }
      } catch (error) {
        console.error('获取 loadingText 失败:', error)
      }
    }

    // 立即执行一次
    await poll()

    // 每隔 500ms轮询一次
    loadingPollingTimer = window.setInterval(poll, 500)
  }
  /**
   * 停止轮询
   */
  const stopLoadingPolling = () => {
    if (loadingPollingTimer) {
      clearInterval(loadingPollingTimer)
      loadingPollingTimer = null
    }
  }

  /**
   * 处理单条 SSE JSON 数据
   * 支持 type: "markdown"（content为字符串）和 type: "html"（content为数组或字符串）
   */
  const processStreamChunk = (
    json: any,
    messageId: number,
    history: { text: string; think: string; thinkFlag: boolean; htmlMerged: boolean }
  ): boolean => {
    // code 错误判断：0 或 "00000" 正常，其他异常
    if (json.code !== undefined && json.code !== 0 && json.code !== '00000') {
      const errorMsg = json.message || '请求异常，请稍后重试'
      const messageIndex = dialogList.value.findIndex(msg => msg.id === messageId)
      if (messageIndex !== -1) {
        dialogList.value[messageIndex].content = errorMsg
        dialogList.value[messageIndex].type = 'answer'
      }
      return true // done
    }

    if (!json.choices?.[0]) return false

    const choice = json.choices[0]
    const normalizedType = (choice.type || '').toLowerCase()

    // finish_reason: "stop" 表示流结束
    if (choice.finish_reason === 'stop') return true

    const content = choice.message?.content

    if (content === null || content === undefined) return false

    // 数据类型：不在聊天框显示，仅存储到 dataParams
    if (
      (normalizedType === 'diagnosis_data_params' ||
        normalizedType === 'todo_ticket_data_params') &&
      typeof content === 'string'
    ) {
      try {
        const parsed = JSON.parse(content)
        Object.keys(parsed).forEach(key => {
          dataParams.value[key] = parsed[key]
        })
      } catch (e) {
        console.error(`解析 ${normalizedType} 失败:`, e)
      }
      return false
    }

    // cardBtn 类型：解析选项按钮，与前面的 markdown 合并到同一气泡
    if (normalizedType === 'cardbtn' && typeof content === 'string') {
      try {
        const parsed = JSON.parse(content) as Chat.AiOptionContent
        const messageIndex = dialogList.value.findIndex(msg => msg.id === messageId)
        if (messageIndex !== -1) {
          dialogList.value[messageIndex].optionContent = parsed
        }
      } catch (e) {
        console.error('解析 cardBtn 失败:', e)
      }
      return false
    }

    // xinLing 类型：不在聊天框展示，直接弹出泳道图
    if (normalizedType === 'xinling' && typeof content === 'string') {
      try {
        let parsed = JSON.parse(content)
        // 兼容处理：如果返回的是纯报告数组，需转换为 { reports, devices } 格式
        if (Array.isArray(parsed)) {
          const reports = parsed
          const deviceMap = new Map<string, any>()
          reports.forEach((report: any) => {
            const srcIp = report[8] || ''
            const dstIp = report[9] || ''
            const srcType = report.sourceIpType || 'UNDEFINED'
            const dstType = report.destIpType || 'UNDEFINED'
            const srcDevice = report.srcDevice || ''
            const dstDevice = report.dstDevice || ''
            if (srcIp && !deviceMap.has(srcIp)) {
              deviceMap.set(srcIp, { 0: srcDevice, 100: srcIp, 101: srcType, source: '1' })
            }
            if (dstIp && !deviceMap.has(dstIp)) {
              deviceMap.set(dstIp, { 0: dstDevice, 100: dstIp, 101: dstType, source: '1' })
            }
          })
          parsed = { reports, devices: Array.from(deviceMap.values()) }
        }
        swimlaneChartData.value = parsed
      } catch (e) {
        console.error('解析 xinLing 数据失败:', e)
      }
      return false
    }

    if (normalizedType === 'html' && typeof content === 'string') {
      // HTML 内容（字符串格式）
      if (history.text && !history.htmlMerged) {
        // 有前序 markdown 文本，将首个 html 合并到同一气泡
        const messageIndex = dialogList.value.findIndex(msg => msg.id === messageId)
        if (messageIndex !== -1) {
          dialogList.value[messageIndex].content += content
          dialogList.value[messageIndex].type = 'answer'
          history.htmlMerged = true
        }
      } else {
        // 无前序 markdown 或已合并过，作为独立气泡推送
        const loadingIdx = dialogList.value.findIndex(
          msg => msg.id === messageId && msg.type === 'loading'
        )
        if (loadingIdx !== -1) dialogList.value.splice(loadingIdx, 1)
        dialogList.value.push({
          id: messageId + dialogList.value.length,
          content: content,
          type: 'html'
        })
      }
    } else if (normalizedType === 'html' && Array.isArray(content)) {
      // HTML 内容（数组格式，兼容旧逻辑） [{ type: 'html'|'faq', data: '...' }]
      const loadingIdx = dialogList.value.findIndex(msg => msg.id === messageId)
      if (loadingIdx !== -1) dialogList.value.splice(loadingIdx, 1)
      content.forEach((item: { type: string; data: string }, idx: number) => {
        dialogList.value.push({
          id: messageId + idx + 10 + dialogList.value.length,
          content: item.data,
          type: item.type === 'faq' ? 'faq' : 'html'
        })
      })
    } else if (normalizedType === 'markdown' && Array.isArray(content)) {
      // data-params: [{ key, type, val }]
      content.forEach((item: any) => {
        if (item.val && typeof item.val === 'object') {
          Object.keys(item.val).forEach(key => {
            dataParams.value[key] = item.val[key]
          })
        }
      })
    } else if (typeof content === 'string') {
      // 普通文本流式输出，将转义的换行符（字面量 \n）转换为真实换行符
      const text = content.replace(/\\n/g, '\n')
      if (history.thinkFlag) {
        history.think += text
      } else {
        history.text += text
      }

      if (history.text.indexOf('<think') > -1) {
        history.thinkFlag = true
        history.text = history.text.replace('<think', '')
      }
      if (history.think.indexOf('</think') > -1) {
        history.thinkFlag = false
        const textList = history.think.split('</think')
        history.think = textList[0]
        history.text = history.text.replace('</think', '')
        history.text += textList[1]
        if (history.think == '\n\n' || history.think == '\n' || history.think == ' ')
          history.think = ''
      }

      const messageIndex = dialogList.value.findIndex(msg => msg.id === messageId)
      if (messageIndex !== -1) {
        dialogList.value[messageIndex].content = history.text
        dialogList.value[messageIndex].reasoning = history.think
        dialogList.value[messageIndex].type = 'answer'
        dialogList.value[messageIndex].answerType = choice.type || 'markdown'
      }
    }
    return false
  }

  /**
   * 处理流式响应（SSE 格式）
   */
  const handleStreamResponse = async (response: Response, messageId: number) => {
    const reader = response.body?.getReader()
    if (!reader) {
      completeStreamOutput(messageId)
      return
    }

    const decoder = new TextDecoder()
    let done = false
    let buffer = ''
    const history = { text: '', think: '', thinkFlag: false, htmlMerged: false }

    while (!done) {
      const { value, done: isDone } = await reader.read()
      done = isDone

      if (value) {
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        for (let i = 0; i < lines.length - 1; i++) {
          let line = lines[i]
          if (!line || line == ': keep-alive' || line.startsWith(':ping')) continue
          line = line.replace(/^\s*data:\s*/, '').trim()
          if (line.startsWith('data:')) line = line.replace(/^data:\s*/, '').trim()

          if (line === '[DONE]') {
            done = true
            break
          }

          try {
            const json = JSON.parse(line)
            if (processStreamChunk(json, messageId, history)) {
              done = true
              break
            }
          } catch (error) {
            console.error('Error parsing JSON:', error)
          }
        }
        buffer = lines[lines.length - 1]
      }
    }

    // 处理 buffer 中剩余数据
    if (buffer) {
      let line = buffer.replace(/^\s*data:\s*/, '').trim()
      if (line.startsWith('data:')) line = line.replace(/^data:\s*/, '').trim()
      if (line && line !== '[DONE]') {
        try {
          const json = JSON.parse(line)
          processStreamChunk(json, messageId, history)
        } catch (error) {
          console.error('Error parsing final JSON:', error)
        }
      }
    }
    completeStreamOutput(messageId)
  }

  /**
   * 判断是否为JSON字符串
   * @param str 字符串
   * @returns 是否为JSON字符串
   */
  const isJsonString = (str: string): boolean => {
    try {
      JSON.parse(str)
      return true
    } catch (error) {
      return false
    }
  }

  /**
   * 家宽 SQL 回答：message.content 是 JSON 字符串，需二次解析成对象。
   */
  const parseJiakuanContentIfNeeded = (
    answerType: string | undefined,
    content: string | jiakuan.jiakuanProps
  ) => {
    const isJiakuan = answerType === 'jiakuan_sql' || answerType === 'jiakuansql'
    if (!isJiakuan || typeof content !== 'string') return content
    if (!isJsonString(content)) return content
    try {
      return JSON.parse(content) as jiakuan.jiakuanProps
    } catch (error) {
      return content
    }
  }

  /**
   * 处理流式响应数据
   * @param messageId 消息ID
   * @param chunk 数据块
   */
  const handleStreamChunk = (messageId: number, chunk: string) => {
    const messageIndex = dialogList.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      dialogList.value[messageIndex].content += chunk
      dialogList.value[messageIndex].type = 'answer'
    }
  }

  /**
   * 完成流式输出
   * @param messageId 消息ID
   */
  const completeStreamOutput = (messageId: number) => {
    const messageIndex = dialogList.value.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      const msg = dialogList.value[messageIndex]
      // 没有实际可显示内容时（如 xinLing 类型全部走了弹窗），直接移除空气泡
      const emptyContent = !msg.content || (typeof msg.content === 'string' && !msg.content.trim())
      if (emptyContent && !msg.optionContent && !(msg.reasoning && msg.reasoning.trim())) {
        dialogList.value.splice(messageIndex, 1)
        pageLoading.value = false
        return
      }
      // faq / html 类型不需要修改 type
      if (
        dialogList.value[messageIndex].type !== 'faq' &&
        dialogList.value[messageIndex].type !== 'html'
      ) {
        dialogList.value[messageIndex].content = parseJiakuanContentIfNeeded(
          dialogList.value[messageIndex].answerType,
          dialogList.value[messageIndex].content as string | jiakuan.jiakuanProps
        )
        dialogList.value[messageIndex].type = 'answer'
      }
      // 清理_buffer字段
      delete dialogList.value[messageIndex]._buffer
      // 如果reasoning字段包含"思考中..."，则清空
      if (dialogList.value[messageIndex].reasoning?.includes('思考中...')) {
        dialogList.value[messageIndex].reasoning = ''
      }
    }
    pageLoading.value = false
  }

  /** 提取有用的那几个name */
  const extractScene = (aiteList: aite_type[], type: number) => {
    let usefulList = aiteList.filter(v => v.type == type)
    if (usefulList.length) {
      let arr: string[] = []
      usefulList.forEach(item => {
        if (item.name) {
          arr = [...arr, ...item.name]
        }
      })

      if (type == 2) {
        arr = [...arr, ...(sessionStore.nationScene || [])]
      }
      return [...new Set(arr)]
    }
    return []
  }

  /** 发送选项 */
  interface SendOptions {
    /** 静默模式：不在对话框中显示用户问题 */
    silent?: boolean
    /** 接口携带的额外参数，映射为 tool_id */
    toolId?: string
    /** 按钮携带的额外参数，会展开到请求体中（如 tool_id、ai_ref_id 等） */
    dataParams?: Record<string, any>
    /** 大模型模式 ID */
    modeId?: number
  }

  /**
   * 发送问题并获取流式响应
   * @param prompt 问题内容
   * @param aiteList 艾特列表
   * @param files 可选的文件列表
   * @param options 可选配置 { silent, toolId }
   */
  const sendQuestion = async (
    prompt: string,
    aiteList: aite_type[] = [],
    files?: any[],
    options: SendOptions = {}
  ) => {
    const { silent = false, toolId, dataParams: extraParams, modeId } = options

    currentPrompt.value = prompt
    currentAite.value = aiteList

    changeMessageId(uuidv4())

    if (!prompt && (!files || files.length === 0)) return

    pageLoading.value = true

    const answerId = Date.now() + 1

    // 非静默模式：添加用户问题气泡
    if (!silent && prompt) {
      dialogList.value.push({
        id: Date.now(),
        content: aiteList.map(v => `@${v.title}`).join(' ') + ' ' + prompt,
        type: 'question'
      })
    }

    // 添加加载状态的回答
    dialogList.value.push({
      id: answerId,
      content: '',
      type: 'loading'
    })

    try {
      // 启动轮询
      startLoadingPolling()

      // 构建 messages 数组（包含完整对话历史）
      const messages = dialogList.value
        .filter(m => (m.type === 'question' || m.type === 'answer') && m.content)
        .map(m => ({
          role: m.type === 'question' ? 'user' : 'assistant',
          content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content)
        }))

      // 静默模式：将当前 prompt 追加到 messages（不在气泡中显示）
      if (silent && prompt) {
        messages.push({ role: 'user', content: prompt })
      }

      const chatRequest: Record<string, any> = {
        sessionId: sessionStore.currentSessionId,
        messageId: currentMessageId.value,
        messages,
        think: isDeepThink.value,
        stream: true,
        commonScene: extractScene(aiteList, 1),
        zoneScene: extractScene(aiteList, 2),
        subscriptionScene: extractScene(aiteList, 3)
      }

      // 携带额外参数 tool_id
      if (toolId) {
        chatRequest.tool_id = toolId
      }
      // 携带大模型模式 ID
      if (modeId != null) {
        chatRequest.modeId = modeId
      }
      // 携带按钮 dataParams（tool_id、ai_ref_id 等）
      if (extraParams) {
        Object.assign(chatRequest, extraParams)
      }

      // Pre-upload files to /files, collect file metadata
      const baseApi = import.meta.env.VITE_APP_BASE_API as string
      const fileMetaList: { file_id: string; name: string; url: string; mime: string; size: number }[] = []
      if (files && files.length > 0) {
        for (const f of files) {
          const fd = new FormData()
          fd.append('file', f)
          const r = await fetch(`${baseApi}/files?sessionId=${encodeURIComponent(sessionStore.currentSessionId)}`, {
            method: 'POST',
            headers: { 'X-Client-Id': getClientId() },
            body: fd
          })
          const j = await r.json()
          if (j.code === '00000') fileMetaList.push(j.data)
        }
      }

      // Build multimodal content for last user message if files were uploaded
      if (fileMetaList.length > 0) {
        const lastUser = [...messages].reverse().find((m: any) => m.role === 'user')
        if (lastUser) {
          const parts: any[] = [{ type: 'text', text: typeof lastUser.content === 'string' ? lastUser.content : String(lastUser.content) }]
          fileMetaList.forEach(fm => parts.push({ type: 'file', file: { file_id: fm.file_id, name: fm.name, url: fm.url } }))
          lastUser.content = parts as any
        }
      }

      // Add file_ids to chatRequest
      if (fileMetaList.length > 0) {
        chatRequest.file_ids = fileMetaList.map(f => f.file_id)
      }

      // 纯 JSON 请求体（文件已通过 /files 上传，这里只带 file_ids）
      const response = await fetch(
        `${import.meta.env.VITE_APP_BASE_API}/chat/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Client-Id': getClientId()
          },
          body: JSON.stringify(chatRequest)
        }
      )

      // 处理流式响应
      await handleStreamResponse(response, answerId)

      // 流式完成后，获取回答耗时
      try {
        const durRes = await request<Response<number>>({
          url: `/chat/duration/${currentMessageId.value}`,
          method: 'GET'
        })
        if (durRes.code == '00000' && durRes.data != null) {
          const ms = durRes.data
          let timeCost: string
          const seconds = ms / 1000
          if (seconds >= 60) {
            const minutes = Math.floor(seconds / 60)
            const remainSec = (seconds % 60).toFixed(0)
            timeCost = `本次回答耗时 ${minutes}分${remainSec}秒`
          } else if (ms >= 1000) {
            timeCost = `本次回答耗时 ${seconds.toFixed(1)}s`
          } else {
            timeCost = `本次回答耗时 ${ms}ms`
          }
          const idx = dialogList.value.findIndex(msg => msg.id === answerId)
          if (idx !== -1) {
            dialogList.value[idx].timeCost = timeCost
          }
        }
      } catch (e) {
        console.warn('获取回答耗时失败:', e)
      }
    } catch (error) {
      console.error('流式请求失败:', error)
      // 出错时添加错误消息
      const messageIndex = dialogList.value.findIndex(msg => msg.id === answerId)
      if (messageIndex !== -1) {
        dialogList.value[messageIndex] = {
          id: answerId,
          content: '网络连接异常，请稍后再试。',
          type: 'answer'
        }
      }
      pageLoading.value = false
    } finally {
      getSessionList()
      setTimeout(() => {
        stopLoadingPolling()
        loadingTexts.value = []
      }, 2000)
    }
  }

  /** 回车发送问题 */
  const enterAnswer = (prompt = '', aiteList: aite_type[] = [], options: SendOptions = {}) => {
    sendQuestion(prompt, aiteList, undefined, options)
  }

  /** 输入框的值 */
  const inputValue = ref('')

  /** 设置输入框值的方法 */
  const setInputValue = (value: string) => {
    inputValue.value = value
  }

  /** 追加内容（如果需要保留原有内容） */
  const appendInputValue = (value: string) => {
    inputValue.value += (inputValue.value ? '\n' : '') + value
  }

  /**
   * 使用 htmlParams 模拟流式输出
   */
  const mockStreamChat = async () => {
    const questionText = '查询工单详情'
    pageLoading.value = true

    const questionId = Date.now()
    const answerId = Date.now() + 1

    dialogList.value.push({
      id: questionId,
      content: questionText,
      type: 'question'
    })
    dialogList.value.push({
      id: answerId,
      content: '',
      type: 'loading'
    })

    const history = { text: '', think: '', thinkFlag: false, htmlMerged: false }
    for (const chunk of htmlParams1) {
      await new Promise(resolve => setTimeout(resolve, 500))
      processStreamChunk(chunk, answerId, history)
    }
    completeStreamOutput(answerId)
  }

  return {
    pageLoading,
    currentPrompt,
    currentAite,
    enterAnswer,
    dialogList,
    handleStreamResponse,
    handleStreamChunk,
    completeStreamOutput,
    sendQuestion,
    cleanDialog,
    isDeepThink,
    setIsDeepThink,
    loadingTexts,
    dataParams,
    sessionList,
    getSessionList,
    deleteSession,
    getDialogList,
    inputValue,
    setInputValue,
    appendInputValue,
    mockStreamChat,
    swimlaneChartData,
    clearSwimlaneChart
  }
})
