import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSessionStore = defineStore(
  'session',
  () => {
    const token = ref<string>('')
    const updateToken = (str: string) => {
      token.value = str
    }
    const currentSessionId = ref<string>()
    const changeSelectedSessionId = (item: string) => {
      currentSessionId.value = item
    }

    //需要全部合到zoneScene(地市专区)中的类型
    const nationScene = ref<string[]>([])
    const updateNationScene = (items: string[]) => {
      nationScene.value = items
    }
    return {
      currentSessionId,
      changeSelectedSessionId,
      token,
      updateToken,
      nationScene,
      updateNationScene
    }
  },
  {
    //网页端写法
    // persist: true,
    // 小程序写法
    persist: {
      key: 'session-store', // 自定义存储键名
      storage: {
        getItem(key: string) {
          try {
            if (typeof uni !== 'undefined') {
              return uni.getStorageSync(key)
            } else {
              return typeof localStorage !== 'undefined' ? localStorage.getItem(key) : null
            }
          } catch (e) {
            console.warn('Storage get error:', e)
            return null
          }
        },
        setItem(key: string, value: any) {
          try {
            if (typeof uni !== 'undefined') {
              uni.setStorageSync(key, value)
            } else if (typeof localStorage !== 'undefined') {
              localStorage.setItem(key, value)
            }
          } catch (e) {
            console.warn('Storage set error:', e)
          }
        }
      }
    }
  }
)
