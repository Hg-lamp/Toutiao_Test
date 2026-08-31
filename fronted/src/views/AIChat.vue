<template>
  <div class="chat-page">
    <van-nav-bar title="小助手" fixed />
    <div class="chat-content">
      <div class="messages" ref="messagesContainer">
        <template v-for="(msg, index) in messages" :key="index">
          <!-- 文件气泡：用户侧，右对齐，可点击删除 -->
          <div v-if="msg.role === 'file'" class="msg file" @click="removeFileMsg(index)">
            <div class="msg-label">你</div>
            <div class="msg-bubble">
              📄 {{ msg.name }}（{{ formatSize(msg.size) }}）
            </div>
          </div>
          <!-- 普通消息气泡 -->
          <div v-else :class="['msg', msg.role === 'user' ? 'user' : 'ai']">
            <div class="msg-label">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
            <div class="msg-bubble">
              <div v-if="msg.role === 'assistant' && msg.content === ''" class="typing"><span></span><span></span><span></span></div>
              <div v-else v-html="formatMessage(msg.content)"></div>
            </div>
          </div>
        </template>
      </div>
      <div class="input-area">
        <input type="file" ref="fileInput" @change="handleFileSelect" accept=".txt,.md,.csv,.pdf,.docx,.xlsx" style="display:none">
        <div class="upload-bar">
          <van-button class="upload-btn" :disabled="isUploading" @click="triggerUpload">{{ isUploading ? '⏳' : 'file' }}</van-button>
        </div>
        <div class="input-row">
          <van-field v-model="userInput" rows="1" autosize type="textarea" placeholder="请输入问题..." class="chat-input" @keypress.enter.prevent="sendMessage" />
          <van-button type="primary" class="send-btn" :disabled="isLoading || !userInput.trim()" @click="sendMessage">发送</van-button>
        </div>
      </div>
    </div>
    <tab-bar />
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'; import TabBar from '../components/TabBar.vue'; import * as marked from 'marked'; import DOMPurify from 'dompurify'; import { aiChatConfig } from '../config/api';
const messages = ref([{ role: 'assistant', content: '你好！我是聪明鼠鼠，没有什么麻烦我解决不了！！！' }]);
const userInput = ref(''); const messagesContainer = ref(null); const isLoading = ref(false);
const isUploading = ref(false); const fileInput = ref(null);
const formatMessage = (c) => c ? DOMPurify.sanitize(marked.parse(c)) : '';
const formatSize = (bytes) => { if (bytes < 1024) return bytes + 'B'; if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'; return (bytes / 1024 / 1024).toFixed(1) + 'MB'; };
const scrollToBottom = () => { if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight };
const triggerUpload = () => { if (!isUploading.value) fileInput.value.click() };
const handleFileSelect = async (e) => {
  const file = e.target.files[0]; if (!file) return;
  isUploading.value = true;
  try {
    const fd = new FormData(); fd.append('file', file);
    const res = await fetch(aiChatConfig.uploadEndpoint, { method: 'POST', body: fd });
    if (!res.ok) { const err = await res.json(); throw new Error(err.detail || `上传失败: ${res.status}`); }
    const data = await res.json();
    // 在消息列表末尾插入文件气泡（用户侧）
    messages.value.push({ role: 'file', name: data.filename, text: data.text, size: data.size });
    await nextTick(); scrollToBottom();
  } catch (e) { messages.value.push({ role: 'assistant', content: `⚠️ 文件上传失败: ${e.message}` }); await nextTick(); scrollToBottom(); }
  finally { isUploading.value = false; e.target.value = ''; }
};
const removeFileMsg = (index) => {
  messages.value.splice(index, 1);
};
const sendMessage = async () => {
  let msg = userInput.value.trim();
  if (!msg || isLoading.value) return;
  // 检查是否有文件气泡在消息列表中，找到最新的文件气泡
  const fileIdx = messages.value.findLastIndex(m => m.role === 'file');
  if (fileIdx !== -1) {
    const file = messages.value[fileIdx];
    msg = `用户上传了文件 ${file.name}，内容如下：\n\`\`\`\n${file.text}\n\`\`\`\n\n${msg}`;
    messages.value.splice(fileIdx, 1); // 发送后移除文件气泡
  }
  messages.value.push({ role: 'user', content: msg }); userInput.value = '';
  messages.value.push({ role: 'assistant', content: '' }); await nextTick(); scrollToBottom();
  isLoading.value = true;
  try {
    const threadId = sessionStorage.getItem('ai_thread_id') || crypto.randomUUID();
    sessionStorage.setItem('ai_thread_id', threadId);
    const res = await fetch(aiChatConfig.apiEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: [{ role: 'user', content: msg }], thread_id: threadId }) });
    if (!res.ok) throw new Error(`请求失败，状态码: ${res.status}`);
    const reader = res.body.getReader(); const decoder = new TextDecoder(); let buf = '', ai = '';
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      buf += decoder.decode(value, { stream: true }); const lines = buf.split('\n'); buf = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) { const data = line.slice(6); if (data === '[DONE]') continue;
          try { const j = JSON.parse(data); if (j.content) { ai += j.content; messages.value[messages.value.length - 1].content = ai; await nextTick(); scrollToBottom() } } catch (e) { console.error(e) } }
      }
    }
    if (!ai) messages.value[messages.value.length - 1].content = '抱歉，AI 暂时无法生成回复，请稍后再试。';
  } catch (e) { messages.value[messages.value.length - 1].content = `发生错误: ${e.message}` } finally { isLoading.value = false; await nextTick(); scrollToBottom() }
};
watch(messages, () => nextTick(scrollToBottom), { deep: true });
onMounted(() => scrollToBottom());
</script>
<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding-top: 46px;
  padding-bottom: 50px;
  box-sizing: border-box;
  font-family: "Ma Shan Zheng", "ZCOOL KuaiLe", "PingFang SC", cursive;
}
:deep(.van-nav-bar) { background: transparent !important; border-bottom: none !important; }
:deep(.van-nav-bar__title) {
  color: var(--text-primary);
  font-family: "Ma Shan Zheng", "ZCOOL KuaiLe", cursive;
  font-size: 20px;
}
.chat-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages {
  flex: 1; overflow-y: auto; padding: 16px 14px; background: transparent;
  scroll-behavior: smooth;
}

/* ----- 云朵气泡通用 ----- */
.msg {
  margin-bottom: 20px;
  max-width: 80%;
  animation: cloudFloat 0.5s var(--ease-smooth) both;
  position: relative;
}
.user { margin-left: auto; }
.ai { margin-right: auto; }

/* 文件气泡：用户侧，右对齐，可点击删除 */
.file {
  margin-left: auto;
  cursor: pointer;
  transition: opacity 0.2s;
}
.file:hover { opacity: 0.7; }

.msg-label {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-tertiary);
  margin-bottom: 6px;
  padding-left: 4px;
  letter-spacing: 0.08em;
  font-family: "Ma Shan Zheng", cursive;
}
.user .msg-label, .file .msg-label { text-align: right; padding-right: 4px; }

/* ----- 云朵气泡本体 ----- */
.msg-bubble {
  position: relative;
  padding: 14px 18px;
  word-break: break-word;
  font-size: 16px;
  line-height: 1.8;
  letter-spacing: 0.03em;
  transition: transform 0.2s var(--ease-smooth);
}

/* AI 云朵（左侧）—— 暖白蓬松云 */
.ai .msg-bubble {
  background: linear-gradient(145deg, #fff8e7, #fffdf5);
  color: #5a4a3a;
  border-radius: 28px 28px 28px 6px;
  box-shadow:
    0 6px 20px rgba(255, 200, 100, 0.15),
    0 2px 6px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 220, 150, 0.25);
}
.ai .msg-bubble::before {
  content: '';
  position: absolute;
  left: -8px;
  bottom: 10px;
  width: 16px;
  height: 14px;
  background: radial-gradient(circle at 6px 8px, #fff8e7 60%, transparent 61%);
  filter: drop-shadow(-1px 1px 2px rgba(255, 200, 100, 0.1));
}

/* 用户云朵（右侧）—— 蓝天白云 */
.user .msg-bubble {
  background: linear-gradient(145deg, #e8f4fd, #d4eaf7);
  color: #2a3a5a;
  border-radius: 28px 28px 6px 28px;
  box-shadow:
    0 6px 20px rgba(100, 180, 255, 0.15),
    0 2px 6px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(150, 200, 255, 0.25);
}
.user .msg-bubble::before {
  content: '';
  position: absolute;
  right: -8px;
  bottom: 10px;
  width: 16px;
  height: 14px;
  background: radial-gradient(circle at 10px 8px, #e8f4fd 60%, transparent 61%);
  filter: drop-shadow(1px 1px 2px rgba(100, 180, 255, 0.1));
}

/* 文件云朵气泡 —— 浅绿，用户侧右对齐 */
.file .msg-bubble {
  background: linear-gradient(145deg, #e8fae8, #d4f0d4);
  color: #2a5a3a;
  border-radius: 28px 28px 6px 28px;
  box-shadow:
    0 6px 20px rgba(100, 200, 100, 0.12),
    0 2px 6px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(100, 200, 100, 0.2);
  padding: 10px 16px;
  font-size: 14px;
}
.file .msg-bubble::before {
  content: '';
  position: absolute;
  right: -8px;
  bottom: 10px;
  width: 16px;
  height: 14px;
  background: radial-gradient(circle at 10px 8px, #e8fae8 60%, transparent 61%);
  filter: drop-shadow(1px 1px 2px rgba(100, 200, 100, 0.08));
}

/* 云朵悬停效果 */
.msg-bubble:hover {
  transform: translateY(-2px) scale(1.01);
}

/* 输入区域 */
.input-area {
  padding: 4px 12px 10px;
  background: transparent;
  border-top: 1px solid rgba(255, 200, 150, 0.2);
}
/* 上传按钮栏 */
.upload-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}
.upload-btn {
  height: 32px;
  padding: 0 10px;
  border-radius: 16px;
  background: rgba(255, 248, 235, 0.4);
  border: 1px solid rgba(255, 200, 150, 0.2);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}
.input-row {
  display: flex;
  gap: 6px;
  align-items: flex-end;
}
.chat-input { flex: 1; }
.chat-input :deep(.van-field__body) {
  background: rgba(255, 248, 235, 0.4);
  border-radius: 24px;
  border: 1px solid rgba(255, 200, 150, 0.2);
  backdrop-filter: blur(4px);
}
.send-btn { align-self: flex-end; flex-shrink: 0; }

/* Markdown 样式适配云朵 */
.msg-bubble pre {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  padding: 12px;
  border-radius: 16px;
  overflow-x: auto;
  margin: 10px 0;
  border: 1px solid rgba(255, 220, 150, 0.15);
  font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
  font-size: 14px;
}
.msg-bubble code {
  background: rgba(255, 220, 150, 0.2);
  padding: 2px 8px;
  border-radius: 6px;
  font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
  font-size: 14px;
}
.user .msg-bubble code { background: rgba(255, 255, 255, 0.3); }
.msg-bubble img {
  max-width: 100%;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.msg-bubble p { margin: 6px 0; }
.msg-bubble ul, .msg-bubble ol { padding-left: 20px; margin: 6px 0; }
.msg-bubble a {
  color: #4060d0;
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* 打字动画 */
.typing { display: flex; gap: 6px; padding: 6px 0; align-items: center; }
.typing span {
  height: 10px; width: 10px;
  background: #ffd54f;
  border-radius: 50%;
  display: inline-block;
  animation: cloudBounce 1.4s infinite ease-in-out;
  box-shadow: 0 2px 6px rgba(255, 200, 100, 0.3);
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

/* 云朵飘入动画 */
@keyframes cloudFloat {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes cloudBounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}
</style>