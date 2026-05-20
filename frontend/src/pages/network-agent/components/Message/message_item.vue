<!-- src/components/message/Message/message_item.vue -->
<script setup lang="ts">
import { computed, ref, onMounted, onUpdated, onUnmounted, nextTick, watch } from 'vue'
import Agent from '@/components/svg/Agent.vue'
import Lighting from '@/components/svg/lighting.vue'
import MarkdownIt from 'markdown-it'
import MdKatex from '@vscode/markdown-it-katex'
import 'katex/dist/katex.min.css'
import MdLinkAttributes from 'markdown-it-link-attributes'
import hljs from 'highlight.js'
import { useChatStore } from '@/stores'
import { openMarkdownExternalUrl, usePcBrowserForMarkdownLinks } from '@/utils/markdownLink'
import RightOutLined from '@/components/svg/RightOutLined.vue'
import DownOutLined from '@/components/svg/DownOutLined.vue'
import JiakuanItem from '../jiakuan/jiakuan_item.vue'
import AiOptionCard from '../xinLing/AiOptionCard.vue'

interface MessageProps {
  message: Chat.ChatItem
}
const chatStore = useChatStore()

const props = defineProps<MessageProps>()
const textRef = ref<HTMLElement>()
const showReasoning = ref(true)

const isJiakuanAnswerType = (type?: string) => type === 'jiakuan_sql' || type === 'jiakuansql'

const normalizeJiakuanContent = (content: unknown): jiakuan.jiakuanProps | null => {
  if (!content) return null
  if (typeof content !== 'string') return content as jiakuan.jiakuanProps
  try {
    return JSON.parse(content) as jiakuan.jiakuanProps
  } catch {
    return null
  }
}

// Store event handler references to prevent memory leaks
const copyClickHandlers = new Map<HTMLElement, () => void>()

// 初始化markdown-it实例
const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
  highlight(code, language) {
    const validLang = !!(language && hljs.getLanguage(language))
    if (validLang) {
      const lang = language ?? ''
      return highlightBlock(hljs.highlight(code, { language: lang }).value, lang)
    }
    return highlightBlock(hljs.highlightAuto(code).value, '')
  }
})

// 配置markdown-it插件
md.renderer.rules.image = function (tokens, idx, options, env, self) {
  const token = tokens[idx]
  const srcIndex = token.attrIndex('src')
  const src = token.attrs![srcIndex][1]
  const alt = token.content
  return `<img src="${src}" alt="${alt}" class="markdown-rendered-img" data-src="${src}" style="cursor: pointer;max-width: 200px"/>`
}

// PC 走浏览器默认 + _blank；移动端在 handleMarkdownBubbleClick 里拦截后用 uni 下载
md.use(MdLinkAttributes, {
  attrs: { target: '_blank', rel: 'noopener noreferrer' }
}).use(MdKatex)

// 高亮代码块
function highlightBlock(str: string, lang?: string) {
  return `<pre class="code-block-wrapper"><div class="code-block-header"><span class="code-block-header__lang">${lang}</span><span class="code-block-header__copy">复制代码</span></div><code class="hljs code-block-body ${lang}">${str}</code></pre>`
}

// 处理数学公式，自动添加 $$ 符号
function escapeBrackets(text: string) {
  const pattern = /(```[\s\S]*?```|`.*?`)|\\\[([\s\S]*?[^\\])\\\]|\\\((.*?)\\\)/g
  return text.replace(pattern, (match, codeBlock, squareBracket, roundBracket) => {
    if (codeBlock) return codeBlock
    else if (squareBracket) return `$$${squareBracket}$$`
    else if (roundBracket) return `$${roundBracket}$`
    return match
  })
}

// 处理美元符号后面跟数字的情况
function escapeDollarNumber(text: string) {
  let escapedText = ''
  for (let i = 0; i < text.length; i += 1) {
    let char = text[i]
    const nextChar = text[i + 1] || ' '
    if (char === '$' && nextChar >= '0' && nextChar <= '9') char = '\\$'
    escapedText += char
  }
  return escapedText
}

// 处理 <think...</think 标签
function handleThinkTags(text: string) {
  return text.replace(/<think([\s\S]*?)<\/think>/g, '<div class="thinking-content">$1</div>')
}

// 计算属性，用于渲染markdown内容
const renderedContent = computed(() => {
  if (!props.message.content) return ''
  let content = handleThinkTags(props.message.content as string)
  // 对数学公式进行处理，自动添加 $$ 符号
  const escapedText = escapeBrackets(escapeDollarNumber(content))
  const html = md.render(escapedText)
  const wrappedHtml = html.replace(/<table>[\s\S]*?<\/table>/g, match => {
    return `<div class="markdown-table-wrapper">${match}</div>`
  })
  return wrappedHtml
})

// 计算属性，用于渲染深度思考内容
const renderedReasoning = computed(() => {
  if (!props.message.reasoning) return ''
  let content = handleThinkTags(props.message.reasoning)
  const escapedText = escapeBrackets(escapeDollarNumber(content))
  return md.render(escapedText)
})

// 复制代码的事件处理函数
const handleCopyClick = (btn: HTMLElement) => {
  const code = btn.parentElement?.nextElementSibling?.textContent
  if (code) {
    navigator.clipboard
      .writeText(code)
      .then(() => {
        btn.textContent = '复制成功'
        setTimeout(() => {
          btn.textContent = '复制代码'
        }, 1000)
      })
      .catch(err => {
        console.error('复制失败:', err)
      })
  }
}

// 绑定代码块的复制事件
function addCopyEvents() {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll('.code-block-header__copy')
    copyBtn.forEach(btn => {
      const element = btn as HTMLElement
      const handler = () => handleCopyClick(element)
      copyClickHandlers.set(element, handler)
      element.addEventListener('click', handler)
    })
  }
}

// 删除绑定的复制事件
function removeCopyEvents() {
  if (textRef.value) {
    const copyBtn = textRef.value.querySelectorAll('.code-block-header__copy')
    copyBtn.forEach(btn => {
      const element = btn as HTMLElement
      const handler = copyClickHandlers.get(element)
      if (handler) {
        element.removeEventListener('click', handler)
        copyClickHandlers.delete(element)
      }
    })
  }
}

// 预览图片
const showImagePreview = (src: string) => {
  uni.previewImage({
    urls: [src],
    current: src,
    indicator: 'default',
    loop: true,
    success: () => {
      console.log('图片预览成功')
    },
    fail: err => {
      console.error('图片预览失败:', err)
    }
  })
}

// 切换深度思考显示
function toggleReasoning() {
  showReasoning.value = !showReasoning.value
}

// Markdown 气泡：PC 不拦 a，用 _blank；移动端拦掉，走 uni 下载（不新开页）
const handleMarkdownBubbleClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  const anchor = target.closest('a')
  if (anchor && textRef.value?.contains(anchor)) {
    const href = anchor.getAttribute('href')
    if (href && !href.startsWith('#')) {
      if (usePcBrowserForMarkdownLinks()) return
      e.preventDefault()
      e.stopPropagation()
      openMarkdownExternalUrl(href)
    }
    return
  }
  if (target.classList.contains('markdown-rendered-img')) {
    const src = target.getAttribute('data-src')
    if (src) showImagePreview(src)
  }
}

// HTML 内容点击事件处理
const handleHtmlClick = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  const actionElement = target.closest('[data-action]') as HTMLElement

  if (!actionElement) return

  const actionType = actionElement.dataset.action
  const param = actionElement.dataset.param || actionElement.dataset.question || ''
  const extra = actionElement.dataset.extra || ''

  switch (actionType) {
    case 'send':
      chatStore.enterAnswer(param, [], extra ? { toolId: extra } : undefined)
      break
    case 'toggle-detail': {
      const actionDiv = target.closest('[data-action="toggle-detail"]')
      const parent = actionDiv?.parentElement
      const detailContent = parent?.querySelector('.detail-content')
      const detailText = actionDiv?.querySelector('.detail-text') as HTMLElement | null
      const expandIcon = actionDiv?.querySelector('.expand-icon')

      if (detailContent?.classList.contains('hidden')) {
        detailContent.classList.remove('hidden')
        if (detailText) detailText.textContent = '收起'
        expandIcon?.classList.add('rotate-180')
      } else {
        detailContent?.classList.add('hidden')
        if (detailText) detailText.textContent = '更多'
        expandIcon?.classList.remove('rotate-180')
      }
      break
    }
    case 'toggle-faq': {
      const toggleText = actionElement.querySelector('.toggle-text') as HTMLElement
      const toggleArrow = actionElement.querySelector('.toggle-arrow') as HTMLElement
      const moreSection = actionElement.closest('.questions-list')?.querySelector('.more-section')
      const moreItems = moreSection
        ? Array.from(moreSection.querySelectorAll('.more-question-item'))
        : []

      if (toggleText) {
        const isHidden = moreItems[0]?.classList.contains('hidden')
        moreItems.forEach(item => {
          if (isHidden) item.classList.remove('hidden')
          else item.classList.add('hidden')
        })
        if (toggleArrow) {
          toggleArrow.style.transform = isHidden ? 'rotate(180deg)' : ''
        }
        toggleText.textContent = isHidden ? '收起' : '更多'
      }
      break
    }
    case 'show-popup':
      window.dispatchEvent(new CustomEvent('show-order-popup'))
      break
    case 'show-preview':
      window.dispatchEvent(new CustomEvent('show-preview-popup', { detail: { type: param } }))
      break
  }
}

// ==================== 诊断行 Tooltip ====================
const diagTooltip = ref<HTMLElement | null>(null)
let diagTooltipTimer: ReturnType<typeof setTimeout> | null = null

function ensureTooltipEl(): HTMLElement {
  if (!diagTooltip.value) {
    const el = document.createElement('div')
    el.className = 'diag-tooltip'
    el.style.cssText =
      'position:fixed;z-index:9999;max-width:70vw;padding:6px 12px;background:rgba(0,0,0,.78);color:#fff;font-size:13px;line-height:1.5;border-radius:6px;word-break:break-all;pointer-events:none;opacity:0;transition:opacity .15s'
    document.body.appendChild(el)
    diagTooltip.value = el
  }
  return diagTooltip.value
}

function showDiagTooltip(e: Event) {
  const target = e.target as HTMLElement
  const span = target.closest('.diag-section .space-y-1 > div > span')
  if (!span) return
  const el = span as HTMLElement
  if (el.scrollWidth <= el.clientWidth + 1) return
  const text = el.textContent || ''
  const tip = ensureTooltipEl()
  tip.textContent = text
  const rect = el.getBoundingClientRect()
  let top = rect.top - 8
  let left = rect.left + rect.width / 2
  tip.style.opacity = '1'
  nextTick(() => {
    const tw = tip.offsetWidth
    const th = tip.offsetHeight
    tip.style.left = Math.max(8, Math.min(left - tw / 2, window.innerWidth - tw - 8)) + 'px'
    tip.style.top = Math.max(8, top - th) + 'px'
  })
}

function hideDiagTooltip() {
  if (diagTooltip.value) {
    diagTooltip.value.style.opacity = '0'
  }
}

function onDiagTouchStart(e: TouchEvent) {
  const target = e.target as HTMLElement
  const span = target.closest('.diag-section .space-y-1 > div > span')
  if (!span) return
  const el = span as HTMLElement
  if (el.scrollWidth <= el.clientWidth + 1) return
  diagTooltipTimer = setTimeout(() => {
    const text = el.textContent || ''
    const tip = ensureTooltipEl()
    tip.textContent = text
    const touch = e.touches[0]
    tip.style.opacity = '1'
    nextTick(() => {
      const tw = tip.offsetWidth
      const th = tip.offsetHeight
      tip.style.left =
        Math.max(8, Math.min(touch.clientX - tw / 2, window.innerWidth - tw - 8)) + 'px'
      tip.style.top = Math.max(8, touch.clientY - th - 30) + 'px'
    })
  }, 500)
}

function onDiagTouchEnd() {
  if (diagTooltipTimer) {
    clearTimeout(diagTooltipTimer)
    diagTooltipTimer = null
  }
  hideDiagTooltip()
}

function initDiagTooltips() {
  const container = textRef.value
  if (!container) return
  const spans = container.querySelectorAll(
    '.diag-section .space-y-1 > div > span:first-child, .diag-section .space-y-1 > div > span:nth-child(2)'
  )
  spans.forEach(span => {
    const el = span as HTMLElement
    el.removeEventListener('mouseenter', showDiagTooltip)
    el.removeEventListener('mouseleave', hideDiagTooltip)
    el.removeEventListener('touchstart', onDiagTouchStart)
    el.removeEventListener('touchend', onDiagTouchEnd)
    el.addEventListener('mouseenter', showDiagTooltip)
    el.addEventListener('mouseleave', hideDiagTooltip)
    el.addEventListener('touchstart', onDiagTouchStart, { passive: true })
    el.addEventListener('touchend', onDiagTouchEnd)
  })
}

function destroyDiagTooltip() {
  if (diagTooltip.value) {
    diagTooltip.value.remove()
    diagTooltip.value = null
  }
}

onMounted(() => {
  addCopyEvents()
  const container = textRef.value
  if (container) {
    container.addEventListener('click', handleMarkdownBubbleClick)
  }
  initDiagTooltips()
})

onUpdated(() => {
  removeCopyEvents()
  addCopyEvents()
  initDiagTooltips()
})

onUnmounted(() => {
  removeCopyEvents()
  const container = textRef.value
  if (container) {
    container.removeEventListener('click', handleMarkdownBubbleClick)
  }
  destroyDiagTooltip()
})
</script>

<template>
  <div
    class="message-item"
    :class="{
      'question-message': message.type === 'question',
      'answer-message':
        message.type === 'answer' || message.type === 'loading' || message.type === 'html',
      'faq-message': message.type === 'faq'
    }"
  >
    <!-- 用户头像 -->
    <div v-if="message.type === 'question'" class="sender-avatar user-avatar">
      <span class="user-initial">Me</span>
    </div>

    <!-- AI头像 (faq不显示) -->
    <div v-else-if="message.type !== 'faq'" class="sender-avatar ai-avatar">
      <Agent />
    </div>

    <!-- 消息内容 -->
    <div class="message-content">
      <!-- faq 类型：无气泡、无头像 -->
      <div
        v-if="message.type === 'faq' && message.content"
        class="faq-content"
        v-html="message.content"
        @click="handleHtmlClick"
      ></div>

      <!-- 其他消息使用气泡样式 -->
      <template v-else>
        <!-- 加载状态的消息 -->
        <div v-if="message.loadingTexts?.length" class="loading-container">
          <div
            v-for="(item, index) in message.loadingTexts"
            :key="item.id"
            class="loading-item animate-in fade-in slide-in-from-left-2 duration-500"
            :class="item?.type == 'endNode' ? 'end-style' : ''"
          >
            <Lighting class="w-3 h-3 min-w-3" :endNode="item?.type == 'endNode'" />
            <span>{{ item.value }}</span>
          </div>
        </div>

        <!-- 普通消息和流式输出消息 -->
        <div
          v-if="!(message.type === 'loading' && !message.content)"
          class="message-bubble"
          :class="{
            'user-message': message.type === 'question',
            'ai-message':
              message.type === 'answer' ||
              (message.type === 'loading' && message.content) ||
              message.type === 'html' ||
              message.type === 'xinling'
          }"
        >
          <!-- 用户问题直接显示 -->
          <template v-if="message.type === 'question'">
            {{ message.content }}
          </template>
          <!-- AI回答 -->
          <template v-else>
            <div ref="textRef" class="leading-relaxed">
              <!-- 深度思考的部分 -->
              <div v-if="message.reasoning" class="mb-4">
                <div
                  @click="toggleReasoning"
                  class="bg-[#eee] py-2 px-4 text-[23rpx] text-[#262626] rounded-lg cursor-pointer inline-block"
                >
                  <span>深度思考</span>
                  <span class="ml-2">
                    <DownOutLined
                      class="inline-block w-[23rpx] h-[23rpx] text-[#262626]"
                      v-if="showReasoning"
                    />
                    <RightOutLined class="inline-block w-[23rpx] h-[23rpx] text-[#262626]" v-else />
                  </span>
                </div>
                <div
                  v-if="showReasoning"
                  class="markdown-body text-[#a6a6a6] pl-4 border-l mt-2"
                  v-html="renderedReasoning"
                ></div>
              </div>
              <!-- 家宽的回复数据类型 -->
              <div v-if="message.content && isJiakuanAnswerType(message.answerType)">
                <JiakuanItem
                  v-if="normalizeJiakuanContent(message.content)"
                  :content="normalizeJiakuanContent(message.content) as jiakuan.jiakuanProps"
                />
              </div>
              <!-- xinling 选项卡片类型 -->
              <div v-else-if="message.type === 'xinling' && message.content">
                <AiOptionCard :content="(message.content as Chat.AiOptionContent)" />
              </div>
              <!-- html 类型：直接渲染 HTML -->
              <div
                v-else-if="message.content && message.type === 'html'"
                class="markdown-body"
                :class="{ 'markdown-body-generate': message.loading }"
                v-html="message.content"
                @click="handleHtmlClick"
              ></div>
              <!-- answer / loading 类型：markdown 渲染 -->
              <div
                v-else-if="message.content"
                class="markdown-body"
                :class="{ 'markdown-body-generate': message.loading }"
                v-html="renderedContent"
                @click="handleHtmlClick"
              ></div>
              <!-- cardBtn 选项按钮（与 markdown 合并在同一气泡） -->
              <div v-if="message.optionContent" class="mt-3">
                <AiOptionCard :content="message.optionContent" />
              </div>
              <!-- 加载状态 -->
              <div v-if="message.loading && !message.content" class="text-[#666]">
                <span>思考中...</span>
              </div>
            </div>
          </template>
        </div>

        <!-- 加载动画（仅在无内容时显示） -->
        <div v-else class="loading-animation">
          <div class="loading-dots">
            <span class="dot dot-1"></span>
            <span class="dot dot-2"></span>
            <span class="dot dot-3"></span>
          </div>
        </div>
        <!-- 回答耗时 -->
        <div
          v-if="message.timeCost"
          class="time-cost animate-in fade-in slide-in-from-left-2 duration-500"
        >
          <span>{{ message.timeCost }}</span>
        </div>
      </template>
    </div>
  </div>
  <!-- 泳道图弹窗已移至 dialogue.vue 层级 -->
</template>

<style lang="scss" scoped>
// @import './style.scss';

.message-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;

  &.question-message {
    flex-direction: row-reverse;
  }

  &.answer-message {
    flex-direction: row;
  }

  &.faq-message {
    flex-direction: row;
    justify-content: flex-start;
    padding-left: 2.5rem;
  }
}

.sender-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid;
  overflow: hidden;

  &.user-avatar {
    background-color: #4f46e5;
    color: white;
    border-color: #4f46e5;
  }

  &.ai-avatar {
    background-color: white;
    border-color: #dbeafe;
  }
  .user-initial {
    font-weight: bold;
    font-size: 0.75rem;
    line-height: 1rem;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 85%;
  word-break: break-all;
}

.faq-message .message-content {
  max-width: 80%;
}

.faq-content {
  color: #999;
  font-size: 23rpx;
  background: transparent;
}

.loading-container {
  margin-bottom: 0.75rem;
  padding: 0.75rem;
  background-color: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  .loading-item {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    background-color: #eff6ff;
    color: #1d4ed8;
    border-radius: 0.375rem;
    font-size: 0.75rem;
    line-height: 1rem;
    font-weight: 500;
    border: 1px solid #dbeafe;
    &.end-style {
      border-color: #dcfce7;
      background-color: #dcfce7;
      color: #22c55e;
    }
  }
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.message-bubble {
  border-radius: 1rem;
  padding: 0.5rem 0.8rem;
  line-height: 1.625;
  white-space: normal;
  // white-space: pre-wrap;
  font-size: 22rpx;

  &.user-message {
    background-color: #2563eb;
    color: white;
    border-top-right-radius: 0.125rem;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
  }

  &.ai-message {
    font-size: 23rpx !important;
    background-color: white;
    color: #383838;
    border: 1px solid #e2e8f0;
    border-top-left-radius: 0.125rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
    .markdown-body {
      font-size: 23rpx !important;
      // line-height: 1em !important; /* 设置为 1 或更小值 */
    }
  }
}

.time-cost {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.5rem;
  padding-left: 0.25rem;
  &.end-style {
    border-color: #dcfce7;
    background-color: #dcfce7;
    color: #22c55e;
  }
}

.loading-animation {
  border-radius: 1rem;
  padding: 1.5rem;
  background-color: white;
  color: #383838;
  border: 1px solid #e2e8f0;
  border-top-left-radius: 0.25rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
}

.loading-dots {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #94a3b8;
}

.dot {
  width: 0.375rem;
  height: 0.375rem;
  background-color: #94a3b8;
  border-radius: 50%;
  animation: bounce 1.4s infinite both;

  &.dot-2 {
    animation-delay: 0.1s;
  }

  &.dot-3 {
    animation-delay: 0.2s;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 思考内容样式 */
.thinking-content {
  background-color: #f0f9ff;
  border-left: 4px solid #3b82f6;
  padding: 0.75rem;
  margin: 1rem 0;
  border-radius: 0 0.5rem 0.5rem 0;
  font-style: italic;
  color: #1e40af;
}

/* 图片预览样式 */
.markdown-rendered-img {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  transition: transform 0.2s ease-in-out;

  &:hover {
    transform: scale(1.02);
  }
}

/* 图片预览对话框样式 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.image-preview-content {
  position: relative;
  max-width: 82%;
  max-height: 82%;
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 0.5rem;
}

.close-button {
  position: absolute;
  top: -40px;
  right: -40px;
  background-color: white;
  color: black;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .close-button {
    top: -40rpx;
    right: -40rpx;
    width: 30rpx;
    height: 30rpx;
    font-size: 18rpx;
  }
}

// 诊断结果行样式 — 通过 :deep() 穿透 v-html 渲染的内容
:deep(.diag-section .space-y-1 > div.flex.justify-between) {
  // 第1个子元素(标签): 不换行, 超长省略
  > span:first-child {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 45%;
    min-width: 0;
  }

  // 第2个子元素(值): 居中, 不换行, 超长省略
  > span:nth-child(2) {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;
    text-align: center;
  }
}
</style>
