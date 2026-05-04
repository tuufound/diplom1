<template>
  <div class="app-container">
    <Navbar v-if="isAuthenticated" />
    <div v-if="isAuthenticated" class="authenticated-shell">
      <AppShellDecor />
      <main class="main-content">
        <router-view v-slot="{ Component, route }">
          <Transition name="slide-up" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </Transition>
        </router-view>
      </main>
    </div>
    <main v-else class="main-content main-content--guest">
      <router-view v-slot="{ Component, route }">
        <Transition name="slide-up" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </router-view>
    </main>
    <Footer v-if="isAuthenticated" />
  </div>
</template>

<script>
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import AppShellDecor from '@/components/AppShellDecor.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer,
    AppShellDecor
  },
  setup() {
    const authStore = useAuthStore()
    const themeStore = useThemeStore()
    const { locale } = useI18n()
    const isAuthenticated = computed(() => authStore.isAuthenticated)

    onMounted(() => {
      themeStore.applyTheme(themeStore.isDark)
    })

    watch(locale, (v) => {
      localStorage.setItem('locale', v)
    })

    return {
      isAuthenticated
    }
  }
}
</script>

<style lang="scss">
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.authenticated-shell {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 0;
}

.main-content {
  flex: 1;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.main-content--guest {
  flex: 1;
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}
</style>