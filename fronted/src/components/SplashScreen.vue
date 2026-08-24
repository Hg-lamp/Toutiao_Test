<template>
  <div class="splash-screen" @click="skip">
    <!-- 视频播放 -->
    <video class="splash-video" ref="videoRef" autoplay muted playsinline preload="auto"
      @ended="onVideoEnd">
      <source src="/splash-intro.mp4" type="video/mp4">
    </video>

    <!-- 暗色遮罩 -->
    <div class="video-overlay"></div>

    <!-- 跳过按钮 -->
    <button class="skip-btn" @click.stop="skip">跳过 ›</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const emit = defineEmits(['complete'])
const videoRef = ref(null)
let transitionTimer = null

function onVideoEnd() {
  startTransition()
}

function startTransition() {
  emit('complete')
}

function skip() {
  if (videoRef.value) {
    videoRef.value.pause()
    videoRef.value.currentTime = 0
  }
  if (transitionTimer) clearTimeout(transitionTimer)
  emit('complete')
}

onMounted(() => {
  // 安全兜底：3秒后强制转场
  transitionTimer = setTimeout(() => {
    emit('complete')
  }, 3000)
})

onBeforeUnmount(() => {
  if (videoRef.value) {
    videoRef.value.pause()
    videoRef.value.currentTime = 0
  }
  if (transitionTimer) clearTimeout(transitionTimer)
})
</script>

<style scoped>
.splash-screen {
  position: fixed;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  max-width: 750px;
  height: 100vh;
  z-index: 9999;
  overflow: hidden;
  background: #08080c;
  cursor: pointer;
}

.splash-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 38% center;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  pointer-events: none;
}

.skip-btn {
  position: absolute;
  bottom: 40px;
  right: 20px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.5);
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  cursor: pointer;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  transition: all 0.2s ease;
}

.skip-btn:active {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}
</style>