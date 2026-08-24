<template>
  <div class="chat-page">
    <van-nav-bar title="小助手" fixed />
    <div class="chat-content">
      <div class="messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['msg', msg.role === 'user' ? 'user' : 'ai']">
          <div class="msg-label">{{ msg.role === 'user' ? '你' : 'AI' }}</div>
          <div class="msg-bubble">
            <div v-if="msg.role === 'assistant' && msg.content === ''" class="typing"><span></span><span></span><span></span></div>
            <div v-else v-html="formatMessage(msg.content)"></div>
          </div>
        </div>
      </div>
      <div class="input-area">
        <van-field v-model="userInput" rows="1" autosize type="textarea" placeholder="请输入问题..." class="chat-input" @keypress.enter.prevent="sendMessage" />
        <van-button type="primary" class="send-btn" :disabled="isLoading || !userInput.trim()" @click="sendMessage">发送</van-button>
      </div>
    </div>
    <tab-bar />
  </div>
</template>
<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'; import TabBar from '../components/TabBar.vue'; import * as marked from 'marked'; import DOMPurify from 'dompurify'; import { aiChatConfig } from '../config/api';
const messages = ref([{ role: 'assistant', content: '你好！我是AI助手，有什么可以帮助你的吗？' }]);
const userInput = ref(''); const messagesContainer = ref(null); const isLoading = ref(false);
const formatMessage = (c) => c ? DOMPurify.sanitize(marked.parse(c)) : '';
const scrollToBottom = () => { if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight };
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  const msg = userInput.value.trim(); messages.value.push({ role: 'user', content: msg }); userInput.value = '';
  messages.value.push({ role: 'assistant', content: '' }); await nextTick(); scrollToBottom();
  isLoading.value = true;
  try {
    const all = messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }));
    const res = await fetch(aiChatConfig.apiEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ messages: all }) });
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
.chat-page { display: flex; flex-direction: column; height: 100vh; padding-top: 46px; padding-bottom: 50px; box-sizing: border-box; }
:deep(.van-nav-bar) { background: transparent !important; border-bottom: none !important; }
:deep(.van-nav-bar__title) { color: var(--text-primary); }
.chat-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages { flex: 1; overflow-y: auto; padding: 12px; background: transparent; }
.msg { margin-bottom: 16px; max-width: 85%; animation: fadeInUp 0.3s var(--ease-smooth) both; }
.user { margin-left: auto; }
.ai { margin-right: auto; }
.msg-label { font-size: 11px; font-weight: 600; color: var(--text-tertiary); margin-bottom: 4px; letter-spacing: 0.05em; }
.msg-bubble { padding: 10px 14px; border-radius: 12px; word-break: break-word; font-size: 14px; line-height: 1.6; }
.user .msg-bubble { background: var(--accent-blue); color: #fff; border-bottom-right-radius: 4px; }
.ai .msg-bubble { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); color: var(--text-primary); border-bottom-left-radius: 4px; }
.input-area { display: flex; padding: 10px 12px; gap: 8px; background: transparent; border-top: 1px solid rgba(255, 255, 255, 0.15); }
.chat-input { flex: 1; }
.chat-input :deep(.van-field__body) { background: rgba(255, 255, 255, 0.2); border-radius: 8px; }
.send-btn { align-self: flex-end; flex-shrink: 0; }
.msg-bubble pre { background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
.msg-bubble code { background: rgba(0,0,0,0.15); padding: 2px 6px; border-radius: 3px; font-family: var(--font-mono); font-size: 13px; }
.user .msg-bubble code { background: rgba(255,255,255,0.15); }
.msg-bubble img { max-width: 100%; border-radius: 6px; }
.msg-bubble p { margin: 6px 0; }
.msg-bubble ul, .msg-bubble ol { padding-left: 20px; margin: 6px 0; }
.msg-bubble a { color: var(--accent-purple); text-decoration: underline; }
.typing { display: flex; gap: 4px; padding: 4px 0; }
.typing span { height: 8px; width: 8px; background: var(--text-tertiary); border-radius: 50%; display: inline-block; animation: bounce 1.5s infinite ease-in-out; }
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,60%,100% { transform: translateY(0) } 30% { transform: translateY(-5px) } }
</style>