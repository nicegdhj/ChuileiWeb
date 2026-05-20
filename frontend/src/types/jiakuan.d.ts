declare namespace jiakuan {
  type Chart = {
    legend: string
    x: Record<string, string | number>
  }
  type UserProfile = {
    avatar: string
    id: string
    name: string
    region: string
    entry_date: string
    working_age: string | number
    group_name: string
    post: string
    monitor_id: string
  }

  // 1. 定义普通图表项 (chart_type 为 1, 2, 3 等)
  type NormalChartItem = {
    title: string
    chart_type: 1 | 2 | 3 // 明确列出非5的类型，或者使用 number 排除 5，但联合类型更精准
    data: Chart[] // 注意：原代码是 chart || userProfile，通常图表数据是数组，这里假设是数组。如果是单个对象请改为 Chart
  }

  // 2. 定义用户画像项 (chart_type 为 5)
  type UserProfileChartItem = {
    title: string
    chart_type: 5
    data: UserProfile[] // 用户画像数据
  }

  type excelType = {
    name: string
    th?: {
      en: string
      zh: string
    }[]
    td?: Partial<{
      month: string
      region: string
      orderid: string
      mtn_username: string
      mtn_yxticket: string
      order_type: string
      install_basic_salary: string
      star_reward_fees: string
      fast_install_fee: string
      diff_fee: string
      mass_integral_fee: string
      order_salary: string
      capital_pool_fee: string
    }>[]
  }

  type jiakuanProps = {
    chat: string
    query_chat_details?: (NormalChartItem | UserProfileChartItem)[]
    query_chat_excel?: excelType[]
    query_recommend_questions?: string[]
  }
}
