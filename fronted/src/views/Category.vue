<template>
  <div class="category-page">
    <van-nav-bar :title="$t('common.allCategories')" :left-text="$t('common.back')" left-arrow @click-left="onClickLeft" fixed />
    <div class="category-container">
      <div class="category-grid">
        <div v-for="category in displayCategories" :key="category.id" class="category-card" @click="goToCategoryNews(category.id)">
          <div class="category-icon"><van-icon name="newspaper-o" /></div>
          <span class="category-name">{{ getCategoryTranslation(category.name) }}</span>
        </div>
      </div>
    </div>
    <tab-bar />
  </div>
</template>
<script setup>
import { useNewsStore } from '../store/modules/news'; import { useRouter } from 'vue-router'; import { useI18n } from 'vue-i18n'; import TabBar from '../components/TabBar.vue'; import { computed } from 'vue'
const newsStore = useNewsStore(); const router = useRouter(); const { t } = useI18n()
const displayCategories = computed(() => newsStore.categories.filter(c => c.name !== '更多'))
const onClickLeft = () => router.back()
const goToCategoryNews = (id) => { newsStore.changeCategory(id); router.push({ path: '/home', query: { categoryId: id } }) }
const getCategoryTranslation = (name) => { const map = { '头条':'headline','社会':'society','国内':'domestic','国际':'international','娱乐':'entertainment','体育':'sports','军事':'military','科技':'technology','财经':'finance' }; const k = map[name]; return k ? t(`home.categories.${k}`) : name }
</script>
<style scoped>
.category-page { padding-top: 46px; padding-bottom: 50px; min-height: 100vh; }
.category-container { padding: 12px; }
.category-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.category-card { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 22px 8px; background: var(--bg-card); backdrop-filter: blur(12px); border-radius: 10px; box-shadow: var(--shadow-card); border: 1px solid var(--border-light); cursor: pointer; animation: fadeInUp 0.35s var(--ease-smooth) both; }
.category-card:active { border-color: var(--border-hover); }
.category-icon :deep(.van-icon) { font-size: 28px; color: var(--accent-purple); margin-bottom: 8px; }
.category-name { font-size: 14px; color: var(--text-primary); font-weight: 500; }
</style>