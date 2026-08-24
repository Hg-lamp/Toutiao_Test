<template>
  <div class="settings-page">
    <van-nav-bar :title="$t('settings.title')" left-arrow @click-left="onClickLeft" />
    <div class="settings-list">
      <van-cell-group inset :title="$t('settings.personalization')">
        <van-cell :title="$t('settings.themeCustomization')" is-link @click="showThemePopup = true" icon="smile-o" />
        <van-cell :title="$t('settings.languageSettings')" is-link @click="showLanguagePopup = true" icon="label-o" />
      </van-cell-group>
      <van-cell-group inset :title="$t('settings.account')">
        <van-cell :title="$t('settings.aboutUs')" is-link icon="info-o" />
      </van-cell-group>
    </div>
    <van-popup v-model:show="showThemePopup" position="bottom" round :style="{ height: '40%' }">
      <div class="popup-title">{{ $t('settings.selectTheme') }}</div>
      <div class="theme-list">
        <div v-for="theme in themeList" :key="theme.id" class="theme-item" :class="{ active: currentTheme === theme.id }" @click="changeTheme(theme.id)">
          <div class="theme-color" :style="{ backgroundColor: theme.primaryColor }"></div>
          <div class="theme-name">{{ theme.name }}</div>
        </div>
      </div>
    </van-popup>
    <van-popup v-model:show="showLanguagePopup" position="bottom" round :style="{ height: '40%' }">
      <div class="popup-title">{{ $t('settings.selectLanguage') }}</div>
      <van-radio-group v-model="currentLanguage">
        <van-cell-group inset>
          <van-cell v-for="lang in languageOptions" :key="lang.value" :title="lang.label" clickable @click="currentLanguage = lang.value">
            <template #right-icon><van-radio :name="lang.value" /></template>
          </van-cell>
        </van-cell-group>
      </van-radio-group>
      <div class="popup-footer"><van-button type="primary" block @click="changeLanguage">{{ $t('common.confirm') }}</van-button></div>
    </van-popup>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue'; import { useRouter } from 'vue-router'; import { showToast } from 'vant'; import { useThemeStore } from '../store/theme'; import { useI18n } from 'vue-i18n'; import { useLanguageStore } from '../store/language';
const router = useRouter(); const themeStore = useThemeStore(); const languageStore = useLanguageStore(); const { t, locale } = useI18n();
const onClickLeft = () => router.back();
const showThemePopup = ref(false); const themeList = computed(() => themeStore.getAllThemes); const currentTheme = computed(() => themeStore.getCurrentTheme);
const changeTheme = (id) => { themeStore.setTheme(id); showToast(t('settings.themeChanged')); showThemePopup.value = false };
const showLanguagePopup = ref(false); const currentLanguage = ref(languageStore.getCurrentLanguage);
const languageOptions = [{ label: '简体中文', value: 'zh-CN' }, { label: 'English', value: 'en-US' }];
const changeLanguage = () => { languageStore.setLanguage(currentLanguage.value); locale.value = currentLanguage.value; showLanguagePopup.value = false; showToast(t('settings.languageChanged')); window.location.reload() };
</script>
<style scoped>
.settings-page { min-height: 100vh; padding-top: 46px; padding-bottom: 20px; }
.settings-list { margin-top: 16px; }
.settings-list :deep(.van-cell-group) { margin-bottom: 12px; }
.settings-list :deep(.van-cell__left-icon) { color: var(--accent-purple); font-size: 18px; }
.popup-title { text-align: center; padding: 16px; font-size: 16px; font-weight: 600; color: var(--text-primary); border-bottom: 1px solid var(--border-light); }
.theme-list { display: flex; flex-wrap: wrap; padding: 20px 16px; }
.theme-item { width: 25%; display: flex; flex-direction: column; align-items: center; margin-bottom: 16px; cursor: pointer; }
.theme-color { width: 40px; height: 40px; border-radius: 50%; margin-bottom: 8px; border: 2px solid transparent; }
.theme-item.active .theme-color { border-color: var(--accent-blue); box-shadow: 0 0 0 3px var(--bg-dark), 0 0 0 5px var(--accent-blue); }
.theme-name { font-size: 12px; color: var(--text-secondary); }
.popup-footer { padding: 16px; position: absolute; bottom: 0; left: 0; right: 0; }
</style>