<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/tasks">
        <i class="fas fa-tasks me-2"></i>Task Planner
      </router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/tasks">
              <i class="fas fa-list-check me-1"></i> Задачи
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/time-tracking">
              <i class="fas fa-clock me-1"></i> Таймер
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/reports">
              <i class="fas fa-chart-bar me-1"></i> Отчеты
            </router-link>
          </li>
        </ul>
        <div class="d-flex align-items-center">
          <div class="me-3 text-white">
            <i class="fas fa-user me-1"></i>
            {{ user?.username || 'Пользователь' }}
          </div>
          <button class="btn btn-outline-light" @click="logout">
            <i class="fas fa-sign-out-alt me-1"></i> Выход
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'Navbar',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const user = computed(() => authStore.user)

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      user,
      logout
    }
  }
}
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.nav-link {
  transition: all 0.3s ease;
}

.nav-link:hover {
  color: #f8f9fa !important;
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  font-weight: 500;
  border-bottom: 2px solid #f8f9fa;
}

.btn-outline-light {
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-outline-light:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}
</style>