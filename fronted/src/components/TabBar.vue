<template>
  <van-tabbar v-model="active" route>
    <van-tabbar-item to="/home" icon="home-o">{{ $t('nav.home') }}</van-tabbar-item>
    <van-tabbar-item to="/aichat" icon="chat-o">小助手</van-tabbar-item>
    <van-tabbar-item to="/my" icon="user-o">{{ $t('nav.my') }}</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

const setActiveTab = () => {
  const path = route.path
  if (path.includes('/home')) {
    active.value = 0
  } else if (path.includes('/aichat')) {
    active.value = 1
  } else if (path.includes('/my')) {
    active.value = 2
  }
}

setActiveTab()
</script>

<style scoped>
:deep(.van-tabbar) { background: transparent !important; border-top: 1px solid rgba(255, 255, 255, 0.1) !important; }
:deep(.van-tabbar-item) { color: var(--text-tertiary); }
:deep(.van-tabbar-item--active) { color: var(--accent-purple); }
</style>