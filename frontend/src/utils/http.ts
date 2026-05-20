// const BASE_URL = 'http://127.0.0.1:1234'

import { useSessionStore } from '@/stores'

// const BASE_URL = import.meta.env.VITE_APP_BASE_API
const BASE_URL = import.meta.env.VITE_APP_BASE_API

const httpInterceptor = {
  // 拦截前触发
  invoke(options: UniApp.RequestOptions) {
    // 1.地址拼接
    options.url = !options.url.startsWith('http') ? BASE_URL + options.url : options.url
    // 2.超时时间
    options.timeout = 10000
    //3.请求头（每次请求时从 store 取最新 token）
    const token = useSessionStore().token || ''
    options.header = {
      ...options.header,
      'source-client': 'miniapp',
      // Authorization: `Bearer ${token}`
      'Web-Authorization': 'WebBearer'
    }
  }
}
// 添加拦截器
uni.addInterceptor('request', httpInterceptor)

uni.addInterceptor('uploadFile', httpInterceptor)

interface Data<T> {
  code: number
  msg: string
  result: T
}
export function request<T>(options: UniApp.RequestOptions) {
  // Promise<Data<T>>
  return new Promise<T>((resolve, reject) => {
    uni.request({
      ...options,
      success(res: UniApp.RequestSuccessCallbackResult) {
        // 判断接口成功，但是错误返回
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // resolve(res.data as Data<T>)
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          // 401错误清理用户信息，跳转到登录页面
          //   useMemberStore().clearProfile()
          //   uni.navigateTo({ url: '/pages/login/login' })
          reject(res)
        } else {
          // uni.showToast({
          //   icon: 'none',
          //   title: '请求错误'
          //   // title: (res.data as Data<T>).msg || '请求错误'
          // })
          reject(res)
        }
      },
      fail(err) {
        // uni.showToast({
        //   icon: 'none',
        //   title: '网络错误'
        // })
        reject(err)
      }
    })
  })
}
