<template>
  <div class="home">
    <van-nav-bar :title="$t('home.title')" fixed />

    <div class="more-options">
      <div class="more-tab" @click="goToCategory">
        {{ $t('home.more') }} <van-icon name="arrow" />
      </div>
    </div>

    <div class="category-tabs">
      <van-tabs v-model:active="activeTab" sticky swipeable animated>
        <van-tab
          v-for="(category, index) in displayCategories"
          :key="category.id"
          :title="getCategoryTranslation(category.name)"
          @click="newsStore.changeCategory(category.id)"
        >
          <van-pull-refresh v-model="newsStore.refreshing" @refresh="onRefresh">
            <van-list
              v-model:loading="newsStore.loading"
              :finished="newsStore.finished"
              :finished-text="$t('home.noMore')"
              @load="onLoad"
            >
              <news-item
                v-for="item in newsStore.newsList"
                :key="item.id"
                :news="item"
              />
            </van-list>
          </van-pull-refresh>
        </van-tab>
      </van-tabs>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { useNewsStore } from '../store/modules/news'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import NewsItem from '../components/NewsItem.vue'
import TabBar from '../components/TabBar.vue'

const newsStore = useNewsStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const activeTab = ref(0)
const tabsTop = ref(0)

watch(
  () => route.query.categoryId,
  (newCategoryId) => {
    if (newCategoryId) {
      const categoryId = parseInt(newCategoryId)
      const filteredCategories = newsStore.categories.filter(category => category.name !== '更多')
      const index = filteredCategories.findIndex(cat => cat.id === categoryId)
      if (index !== -1) {
        activeTab.value = index
        newsStore.changeCategory(categoryId)
      }
    }
  },
  { immediate: true }
)

onMounted(() => {
  newsStore.getCategories().then(() => {
    newsStore.getNewsList()
  })
  setTimeout(updateTabsPosition, 300)
  window.addEventListener('scroll', handleScroll)
})

const displayCategories = computed(() => {
  return newsStore.categories.filter(category => category.name !== '更多');
})

const getCategoryTranslation = (categoryName) => {
  const categoryMap = {
    '头条': 'headline', '社会': 'society', '国内': 'domestic',
    '国际': 'international', '娱乐': 'entertainment', '体育': 'sports',
    '军事': 'military', '科技': 'technology', '财经': 'finance', '更多': 'more'
  };
  const key = categoryMap[categoryName];
  return key ? t(`home.categories.${key}`) : categoryName;
}

const goToCategory = () => {
  router.push('/category')
}

const updateTabsPosition = () => {
  const tabsElement = document.querySelector('.van-tabs__wrap')
  if (tabsElement) {
    tabsTop.value = tabsElement.getBoundingClientRect().top
  }
}

const handleScroll = () => {
  updateTabsPosition()
}

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})

watch(activeTab, (newVal) => {
  const categoryId = newsStore.categories[newVal]?.id
  if (categoryId) newsStore.changeCategory(categoryId)
})

const onRefresh = () => { newsStore.getNewsList(true) }
const onLoad = () => { newsStore.getNewsList() }
</script>

<style scoped>
.home {
  padding-top: 46px;
  padding-bottom: 50px;
  min-height: 100vh;
}

.category-tabs {
  margin-bottom: 10px;
  position: relative;
}

:deep(.van-tabs__wrap) {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
}

:deep(.van-tab) {
  font-size: 14px;
  color: var(--text-secondary);
}

:deep(.van-tab--active) {
  font-weight: 600;
  color: var(--accent-purple);
}

.more-options {
  position: fixed;
  right: 0;
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 0;
  border-radius: 4px 0 0 4px;
  box-shadow: var(--shadow-card);
  z-index: 1000;
  top: v-bind('tabsTop + "px"');
  height: 44px;
  display: flex;
  align-items: center;
  border: 1px solid var(--border-light);
  border-right: none;
}

.more-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--accent-purple);
  font-weight: 500;
  height: 100%;
  padding: 0 12px;
  font-size: 13px;
}
</style>