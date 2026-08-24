import { defineStore } from 'pinia';

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: localStorage.getItem('theme') || 'dark',
    themes: {
      dark: {
        name: '深色模式',
        backgroundColor: 'rgba(255, 255, 255, 0.88)',
        textColor: '#1a1a2e',
        primaryColor: '#4060d0',
        secondaryColor: 'rgba(255, 255, 255, 0.85)',
      },
      light: {
        name: '浅色模式',
        backgroundColor: 'rgba(248, 246, 243, 0.88)',
        textColor: '#1a1a1a',
        primaryColor: '#1a2332',
        secondaryColor: 'rgba(255, 255, 255, 0.9)',
      },
      pure: {
        name: '纯背景',
        backgroundColor: 'transparent',
        textColor: '#1a1a2e',
        primaryColor: '#4060d0',
        secondaryColor: 'transparent',
      }
    }
  }),

  getters: {
    getCurrentTheme: (state) => state.currentTheme,
    getThemeConfig: (state) => state.themes[state.currentTheme],
    getAllThemes: (state) => Object.keys(state.themes).map(key => ({
      id: key,
      name: state.themes[key].name,
      primaryColor: state.themes[key].primaryColor
    }))
  },

  actions: {
    setTheme(themeName) {
      if (this.themes[themeName]) {
        this.currentTheme = themeName;
        localStorage.setItem('theme', themeName);
        this.applyTheme();
      }
    },

    applyTheme() {
      const theme = this.themes[this.currentTheme];
      document.documentElement.style.setProperty('--background-color', theme.backgroundColor);
      document.documentElement.style.setProperty('--text-color', theme.textColor);
      document.documentElement.style.setProperty('--primary-color', theme.primaryColor);
      document.documentElement.style.setProperty('--secondary-color', theme.secondaryColor);
    },

    initTheme() {
      this.applyTheme();
    }
  }
});