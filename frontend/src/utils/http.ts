import { useSessionStore } from '@/stores'
import { getClientId } from './client_id'

const BASE_URL = import.meta.env.VITE_APP_BASE_API

const httpInterceptor = {
  invoke(options: UniApp.RequestOptions) {
    options.url = !options.url.startsWith('http') ? BASE_URL + options.url : options.url
    options.timeout = 30000
    options.header = {
      ...options.header,
      'X-Client-Id': getClientId()
    }
  }
}
uni.addInterceptor('request', httpInterceptor)
uni.addInterceptor('uploadFile', httpInterceptor)

interface Data<T> {
  code: number
  msg: string
  result: T
}
export function request<T>(options: UniApp.RequestOptions) {
  return new Promise<T>((resolve, reject) => {
    uni.request({
      ...options,
      success(res: UniApp.RequestSuccessCallbackResult) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          reject(res)
        } else {
          reject(res)
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}
