/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

// AI 聊天后端接口配置
export const aiChatConfig = {
  // 后端 AI 聊天 SSE 接口地址
  apiEndpoint: `${apiConfig.baseURL}/api/ai/chat`,
}
