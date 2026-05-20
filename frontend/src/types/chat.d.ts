declare namespace Chat {
  /** AI 选项按钮 */
  type AiOption = {
    tile?: string
    title?: string
    selected: number
    action: string | number
    dataParams?: Record<string, any>
    showQuestion?: boolean | string | number
  }

  /** AI 选项消息内容 */
  type AiOptionContent = {
    content: string
    options: AiOption[]
  }

  /** 对话记录的数组 */
  type ChatItem = {
    id?: number
    content?: string | jiakuan.jiakuanProps | AiOptionContent
    type: 'question' | 'answer' | 'loading' | 'html' | 'faq' | 'xinling'
    /** 回答的数据类型，默认为markdown */
    answerType?: 'markdown' | 'html' | 'jiakuan_sql'
    /** cardBtn 选项内容（与 markdown 合并显示在同一气泡） */
    optionContent?: AiOptionContent
    /** 回答耗时文本，如 "本次回答耗时 182.2s" */
    timeCost?: string
    loadingTexts?: {
      id: number
      value: string
      type?: string
    }[]
    reasoning?: string
    _buffer?: string
    loading?: boolean
    picture?: string[]
  }
}
