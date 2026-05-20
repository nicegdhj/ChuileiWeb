<template>
  <view class="content"> </view>
</template>

<script setup lang="ts">
import { useChatStore, useSessionStore } from '@/stores'
import { request } from '@/utils/http'
import { onMounted, ref } from 'vue'
const title = ref('Hello')

const chatStore = useChatStore()
// const memberStore = useMemberStore()
const sessionStore = useSessionStore()

const initSystem = async () => {
  try {
    // let token = window.location.href.split('token=')[1]?.split('&')[0]
    // if (token) {
    //   // 更新token存储
    //   sessionStore.updateToken(token)
    //   document.cookie = `token=${token}`
    //   const result = await request<any>({
    //     url: '/suban-h5-dx/eoms-suban/verifyToken/getVerify',
    //     method: 'GET',
    //     header: {
    //       'Content-Type': 'application/json',
    //       accept: 'application/json'
    //     }
    //   })
    //   const obj = result.data
    //   memberStore.setUserInfo(obj)
    //   localStorage.setItem('mobile1', obj.mobile)
    //   /** 获取会话记录列表 */
    //   chatStore.getSessionList()
    //   uni.redirectTo({
    //     url: '/pages/network-agent/index'
    //   })
    // }
    sessionStore.updateToken('default')
    chatStore.getSessionList()
  } catch (err) {
    console.log(err)
    // uni.showToast({ icon: 'error', title: '验证失败' })
  } finally {
    uni.redirectTo({ url: '/pages/network-agent/index' })
    // 无论是否有 token、请求成败，都标记初始化完成，再挂载 InputModule，保证其 onMounted 时能拿到 token
  }
}
onMounted(() => {
  initSystem()
})
</script>

<style>
.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
