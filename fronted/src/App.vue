<template>
  <div class="app">
    <!-- 开场动画 -->
    <SplashScreen v-if="showSplash" @complete="onSplashComplete" />

    <!-- 动态背景 -->
    <AmbientBackground />

    <!-- 内容层 -->
    <div class="content-layer">
      <router-view v-slot="{ Component }">
        <Transition :name="transitionName" mode="out-in">
          <template v-if="$route.meta.keepAlive">
            <keep-alive>
              <component :is="Component" :key="$route.fullPath" />
            </keep-alive>
          </template>
          <template v-else>
            <component :is="Component" :key="$route.fullPath" />
          </template>
        </Transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import SplashScreen from './components/SplashScreen.vue'
import AmbientBackground from './components/AmbientBackground.vue'

const router = useRouter()
const transitionName = ref('fade-slide')
const showSplash = ref(true)

// 开场动画完成
const onSplashComplete = () => {
  showSplash.value = false
}

// 今日日期
const today = computed(() => {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  const w = weekdays[d.getDay()]
  return `${y}.${m}.${day} · 周${w}`
})

// 根据路由层级决定动画方向
const routeDepth = {
  '/home': 0, '/category': 0, '/aichat': 0, '/my': 0,
  '/login': 1, '/register': 1,
  '/history': 1, '/favorite': 1, '/profile': 1, '/settings': 1,
  '/news/detail': 2,
}

watch(() => router.currentRoute.value, (to, from) => {
  if (!from) {
    transitionName.value = 'fade'
    return
  }
  const toDepth = routeDepth[to.path] ?? (to.path.startsWith('/news/detail') ? 2 : 1)
  const fromDepth = routeDepth[from.path] ?? (from.path.startsWith('/news/detail') ? 2 : 1)
  transitionName.value = toDepth > fromDepth ? 'slide-left' : 'slide-right'
}, { immediate: true })
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  font-size: 16px;
  background: #08080c;
  color: #e0e0e0;
}

.app {
  max-width: 750px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

/* 内容层 */
.content-layer {
  position: relative;
  z-index: 1;
  animation: contentFadeIn 0.5s ease-out;
}

/* 移动端适配 */
@media screen and (max-width: 750px) {
  html {
    font-size: calc(100vw / 750 * 16);
  }
}

/* ========== 页面转场动画 ========== */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-left-enter-from {
  transform: translateX(30px);
  opacity: 0;
}
.slide-left-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-right-enter-from {
  transform: translateX(-30px);
  opacity: 0;
}
.slide-right-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

.fade-slide-enter-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.fade-slide-enter-from {
  transform: translateY(15px);
  opacity: 0;
}

@keyframes contentFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>