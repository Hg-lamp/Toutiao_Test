<template>
  <div class="news-card" @click="goToDetail">
    <div class="news-card__content">
      <h3 class="news-card__title">{{ news.title }}</h3>
      <p class="news-card__desc">{{ news.description }}</p>
      <div class="news-card__meta">
        <span class="news-card__author">{{ news.author }}</span>
        <span class="meta-dot">·</span>
        <span class="news-card__time">{{ news.publishTime }}</span>
        <span class="meta-dot">·</span>
        <span class="news-card__views">{{ news.views }} 阅读</span>
      </div>
    </div>
    <div class="news-card__image" v-if="news.image">
      <img :src="news.image" :alt="news.title" loading="lazy" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  news: { type: Object, required: true }
})

const router = useRouter()

const goToDetail = () => {
  router.push(`/news/detail/${props.news.id}`)
}
</script>

<style scoped>
.news-card {
  display: flex;
  padding: 14px 16px;
  margin: 0 12px 8px;
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 10px;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--border-light);
  cursor: pointer;
  animation: fadeInUp 0.35s var(--ease-smooth) both;
}

.news-card:active {
  box-shadow: var(--shadow-card-hover);
  border-color: var(--border-hover);
  transform: translateY(-1px);
}

.news-card__content {
  flex: 1;
  min-width: 0;
  margin-right: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.news-card__title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.45;
  margin: 0 0 6px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.news-card__desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-secondary);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.news-card__meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
  flex-wrap: wrap;
}

.news-card__author {
  color: var(--accent-purple);
  font-weight: 500;
}

.meta-dot {
  color: var(--border-light);
  font-weight: 600;
}

.news-card__views {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: -0.02em;
  color: var(--text-tertiary);
}

.news-card__image {
  width: 100px;
  height: 76px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: var(--bg-mid);
}

.news-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s var(--ease-smooth);
}

.news-card:active .news-card__image img {
  transform: scale(1.05);
}
</style>