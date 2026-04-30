<template>
  <div class="app-container">
    <Navbar v-if="isAuthenticated" />
    <div class="main-content">
      <router-view />
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
  padding: 24px;
}

@import './assets/main.scss';
</style>