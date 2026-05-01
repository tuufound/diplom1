<template>
  <nav class="navbar navbar-expand-lg app-navbar">
    <div class="container-fluid px-2 px-lg-4">
      <router-link class="navbar-brand" to="/tasks">
        <span class="brand-icon"><i class="fas fa-tasks"></i></span>
        Task Planner
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
            <router-link class="nav-link" to="/kanban">
              <i class="fas fa-table-columns me-1"></i> Канбан
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
        <div class="d-flex align-items-center gap-2">
          <div class="user-chip">
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
.app-navbar {
  margin-bottom: 14px;
  border: 1px solid rgba(193, 207, 234, 0.9);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.88) 0%, rgba(235, 243, 255, 0.85) 100%);
  box-shadow: 0 8px 24px rgba(35, 63, 124, 0.08);
  backdrop-filter: blur(8px);
}

.navbar-brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #1a2741;
  font-weight: 700;
}

.brand-icon {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: #fff;
  background: linear-gradient(135deg, #637dff 0%, #7a56ff 100%);
}

.nav-link {
  transition: all 0.2s ease;
  border-radius: 10px;
  color: #33425f !important;
  padding: 8px 12px !important;
}

.nav-link:hover {
  color: #1e2e4d !important;
  background: rgba(120, 145, 224, 0.15);
}

.nav-link.router-link-active {
  color: #182643 !important;
  font-weight: 600;
  background: rgba(125, 145, 229, 0.22);
}

.btn-outline-light {
  border-color: #b7c8e9;
  color: #2c3d60;
  background: rgba(255, 255, 255, 0.7);
}

.user-chip {
  padding: 7px 10px;
  border-radius: 999px;
  border: 1px solid #c7d5ef;
  color: #2c3d60;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.78);
}

.btn-outline-light:hover {
  background: #edf3ff;
  border-color: #9cb4e0;
  color: #223252;
}
</style>