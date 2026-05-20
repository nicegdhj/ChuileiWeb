<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";


import { getCurrentInstance } from 'vue'

const globalData = {
  baseUrl: '/suban-h5-dx/eoms-suban',
  askUrl: '/suban-h5-dx/ask-suban',
  suwenUrl: '/suban-h5-dx/agent-suwen',
  token: null as string | null
}

const instance = getCurrentInstance()
if (instance) {
  ;(instance.appContext.config.globalProperties as any).globalData = globalData
}
onLaunch(() => {
  console.log('App Launch')
  if (typeof window !== 'undefined' && window.document) {
    const link = document.createElement('link')
    link.rel = 'icon'
    link.href = 'static/favicon.ico'
    link.type = 'image/x-icon'
    document.head.appendChild(link)

    const shortcutLink = document.createElement('link')
    shortcutLink.rel = 'shortcut icon'
    shortcutLink.href = 'static/favicon.ico'
    shortcutLink.type = 'image/x-icon'
    document.head.appendChild(shortcutLink)
  }
})
onShow(() => {
  console.log("App Show");
});
onHide(() => {
  console.log("App Hide");
});
</script>
<style></style>
