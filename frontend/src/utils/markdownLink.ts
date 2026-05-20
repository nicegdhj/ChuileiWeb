import { useSessionStore } from '@/stores/modules/session'

/**
 * 移动端 / 小屏（嵌入 App WebView）：拦截 <a>，用 uni 下载 + openDocument，不依赖新开页。
 * PC / 大屏：不拦截，Markdown 里保留 target=_blank，由浏览器处理预览或下载。
 *
 * 可选：VITE_MARKDOWN_DOWNLOAD_PROXY（同域代理）、window.__LINGXI_DOWNLOAD_BRIDGE__、uni.webView.postMessage（外层 uni 原生下载，绕 CORS）
 * VITE_MARKDOWN_LINK_MODE=open 时强制 window.open（调试用）
 */

const MESSAGE_TYPE = 'LINGXI_FILE_DOWNLOAD'

function isSafeHttpUrl(href: string): boolean {
  try {
    const u = new URL(href, typeof location !== 'undefined' ? location.href : undefined)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

const LINK_MODE = import.meta.env.VITE_MARKDOWN_LINK_MODE || 'download'
const DOWNLOAD_PROXY = import.meta.env.VITE_MARKDOWN_DOWNLOAD_PROXY || ''

function getAuthHeader(): Record<string, string> {
  let token = ''
  try {
    token = useSessionStore().token || ''
  } catch {
    /* Pinia 未就绪 */
  }
  return token ? { Authorization: token } : {}
}

function copyLinkFallback(href: string) {
  uni.setClipboardData({
    data: href,
    success: () => {
      uni.showToast({ title: '链接已复制', icon: 'none', duration: 2000 })
    }
  })
}

function openInBrowserFallback(href: string) {
  if (typeof window === 'undefined') return
  const opened = window.open(href, '_blank', 'noopener,noreferrer')
  if (!opened) copyLinkFallback(href)
}

function postDownloadToUniWebViewHost(
  href: string,
  header: Record<string, string>
): boolean {
  const post = (uni as unknown as { webView?: { postMessage?: (o: { data: unknown }) => void } })
    .webView?.postMessage
  if (!post) return false
  try {
    post({
      data: {
        type: MESSAGE_TYPE,
        url: href,
        header
      }
    })
    uni.showToast({ title: '已请求客户端下载', icon: 'none' })
    return true
  } catch {
    return false
  }
}

function invokeHostDownloadBridge(href: string, header: Record<string, string>): boolean {
  const fn = (typeof window !== 'undefined'
    ? (window as unknown as { __LINGXI_DOWNLOAD_BRIDGE__?: (u: string, h: Record<string, string>) => void })
        .__LINGXI_DOWNLOAD_BRIDGE__
    : undefined) as ((u: string, h: Record<string, string>) => void) | undefined
  if (typeof fn !== 'function') return false
  try {
    fn(href, header)
    return true
  } catch {
    return false
  }
}

function buildProxyUrl(target: string): string {
  const base = DOWNLOAD_PROXY.replace(/\/$/, '')
  const sep = base.includes('?') ? '&' : '?'
  return `${base}${sep}target=${encodeURIComponent(target)}`
}

function hasPlusRuntime(): boolean {
  if (typeof window === 'undefined') return false
  try {
    const w = window as unknown as { plus?: { runtime?: unknown } }
    return !!(w.plus && w.plus.runtime)
  } catch {
    return false
  }
}

function runDownloadFile(
  url: string,
  header: Record<string, string>,
  onFail: () => void
) {
  uni.showLoading({ title: '下载中...', mask: true })
  const opts: UniNamespace.DownloadFileOption = {
    url,
    success: (res: UniNamespace.DownloadSuccessData) => {
      uni.hideLoading()
      if (res.statusCode !== 200) {
        uni.showToast({ title: `下载失败(${res.statusCode})`, icon: 'none' })
        return
      }
      const tempPath = res.tempFilePath
      uni.openDocument({
        filePath: tempPath,
        showMenu: true,
        fail: () => {
          if (typeof window !== 'undefined' && tempPath) {
            try {
              const w = window.open(tempPath, '_blank', 'noopener,noreferrer')
              if (!w) copyLinkFallback(url)
            } catch {
              copyLinkFallback(url)
            }
          } else {
            copyLinkFallback(url)
          }
        }
      })
    },
    fail: () => {
      uni.hideLoading()
      onFail()
    }
  }
  if (Object.keys(header).length) opts.header = header
  uni.downloadFile(opts)
}

/**
 * 为 true 时：Markdown 外链不拦截，依赖 a 标签上 target=_blank（PC 预览/下载）。
 * 为 false 时：由 message_item 里拦截并走 openMarkdownExternalUrl。
 */
export function usePcBrowserForMarkdownLinks(): boolean {
  try {
    const s = uni.getSystemInfoSync()
    const w = s.windowWidth || s.screenWidth || 0
    if (w >= 768) return true
    const p = String(s.platform || '').toLowerCase()
    if (p === 'windows' || p === 'mac' || p === 'linux') return true
  } catch {
    /* empty */
  }
  if (typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches) return true
  return false
}

/** 仅应在移动端拦截后调用 */
export function openMarkdownExternalUrl(href: string): void {
  if (!href || href.startsWith('#') || href.toLowerCase().startsWith('javascript:')) return
  if (!isSafeHttpUrl(href)) {
    uni.showToast({ title: '不支持的链接类型', icon: 'none' })
    return
  }

  if (LINK_MODE === 'open') {
    openInBrowserFallback(href)
    return
  }

  const header = getAuthHeader()

  if (DOWNLOAD_PROXY) {
    runDownloadFile(buildProxyUrl(href), header, () => {
      uni.showToast({ title: '代理下载失败', icon: 'none' })
    })
    return
  }

  if (invokeHostDownloadBridge(href, header)) return
  if (postDownloadToUniWebViewHost(href, header)) return

  const nativeApp = hasPlusRuntime()
  runDownloadFile(href, header, () => {
    uni.showToast({
      title: nativeApp ? '下载失败' : '下载失败，可能跨域限制',
      icon: 'none',
      duration: 2500
    })
    if (!nativeApp) copyLinkFallback(href)
  })
}
