<template>
  <div class="app-container">
    <Navbar v-if="isAuthenticated" />
    <div class="main-content">
      <router-view v-slot="{ Component, route }">
        <Transition name="slide-up" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </router-view>
    </div>
    <Footer v-if="isAuthenticated" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  },
  setup() {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)

    return {
      isAuthenticated
    }
  }
}
</script>

<style lang="scss">
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: 18px;
  width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.main-content::before,
.main-content::after {
  content: '';
  position: fixed;
  pointer-events: none;
  border-radius: 999px;
  z-index: -1;
}

.main-content::before {
  width: 220px;
  height: 220px;
  right: 14%;
  top: 160px;
  background: radial-gradient(circle, rgba(238, 162, 201, 0.3) 0%, rgba(238, 162, 201, 0) 68%);
}

.main-content::after {
  width: 300px;
  height: 300px;
  left: 8%;
  bottom: 80px;
  background: radial-gradient(circle, rgba(181, 162, 234, 0.28) 0%, rgba(181, 162, 234, 0) 68%);
}

@media (max-width: 768px) {
  .main-content {
    padding: 12px;
  }
}
</style>