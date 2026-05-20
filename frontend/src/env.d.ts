/// <reference types="vite/client" />

interface ImportMetaEnv {
  /**
   * markdown 外链：download=下载后 openDocument（默认）；open=仅 window.open/复制
   */
  readonly VITE_MARKDOWN_LINK_MODE?: string
  /**
   * 同域下载代理前缀，如 /api/file-proxy（自行实现 ?target=encodeURIComponent(原链)）
   */
  readonly VITE_MARKDOWN_DOWNLOAD_PROXY?: string
}

declare global {
  interface Window {
    /** (url, header) => void：由壳/父页用原生或代理下载，绕过子页 CORS */
    __LINGXI_DOWNLOAD_BRIDGE__?: (url: string, header: Record<string, string>) => void
  }
}

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}
