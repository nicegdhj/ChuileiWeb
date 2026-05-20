/**
 * 灵犀选项卡片模拟数据（文件上传后返回的按钮数据）
 */
export const xinLingOptionData = {
  content: '建议先通过意见诊断对该账号问题进行全面分析，请确认是否需要执行',
  options: [
    {
      tile: '不需要',
      selected: 0,
      action: '0',
      dataParams: {} // 内容读取 src/static/xinLing.js 文件里的内容
    },
    {
      tile: '一键诊断',
      selected: 1,
      action: '1',
      showQuestion: false
    }
  ]
}
