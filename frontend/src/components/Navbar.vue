<template>
  <nav class="navbar navbar-expand-lg app-navbar">
    <div class="container-fluid px-2 px-lg-4">
      <router-link class="navbar-brand" to="/tasks">
        <span class="brand-icon"><i class="fas fa-tasks"></i></span>
        Task Planner
      </router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <i class="fas fa-bars"></i>
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
          <li class="nav-item">
            <router-link class="nav-link" to="/profile">
              <i class="fas fa-user me-1"></i> Профиль
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
  position: sticky;
  top: 10px;
  z-index: 100;
  margin: 8px auto 14px;
  max-width: 1420px;
  border: 1px solid rgba(224, 206, 232, 0.8);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.88) 0%, rgba(252, 241, 248, 0.88) 100%);
  box-shadow: 0 12px 24px rgba(131, 102, 146, 0.18);
  backdrop-filter: blur(10px);
}

.navbar-brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #293a65;
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
  background: linear-gradient(135deg, #f35db5 0%, #8b7aff 100%);
}

.nav-link {
  transition: all 0.2s ease;
  border-radius: 10px;
  color: #5a4d7e !important;
  padding: 8px 12px !important;
  border: 1px solid transparent;
}

.nav-link:hover {
  color: #2f3f6d !important;
  background: rgba(244, 232, 249, 0.9);
  border-color: rgba(219, 199, 230, 0.72);
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  color: #2f3f6d !important;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(219, 199, 230, 0.74);
}

.btn-outline-light {
  border-color: rgba(219, 199, 230, 0.74);
  color: #5d4e81;
  background: rgba(255, 255, 255, 0.86);
}

.user-chip {
  padding: 7px 10px;
  border-radius: 999px;
  border: 1px solid rgba(220, 202, 231, 0.78);
  color: #5d4f80;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.78);
}

.btn-outline-light:hover {
  background: rgba(248, 238, 252, 0.95);
  border-color: rgba(207, 181, 221, 0.86);
  color: #4f4370;
}

.navbar-toggler {
  border-color: rgba(220, 202, 231, 0.78);
  color: #5d4f80;
  background: rgba(255, 255, 255, 0.82);
}

.navbar-toggler:focus {
  box-shadow: 0 0 0 0.2rem rgba(179, 128, 205, 0.22);
}

@media (max-width: 992px) {
  .app-navbar {
    top: 0;
    margin: 0 0 10px;
    border-radius: 0 0 16px 16px;
  }

  .navbar-collapse {
    padding-top: 10px;
  }

  .navbar-nav .nav-link {
    margin-bottom: 6px;
  }

  .user-chip {
    display: none;
  }
}
</style>