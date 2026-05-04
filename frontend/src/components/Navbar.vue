<template>
  <nav class="navbar navbar-expand-lg app-navbar">
    <div class="container-fluid px-3 px-lg-4">
      <router-link class="navbar-brand" to="/tasks">
        <span class="brand-icon">
          <i class="fas fa-gem"></i>
        </span>
        <span class="brand-text">TaskFlow</span>
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <i class="fas fa-bars"></i>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mx-auto">
          <li class="nav-item" v-for="item in navItems" :key="item.path">
            <router-link class="nav-link" :to="item.path">
              <i :class="item.icon"></i>
              <span>{{ item.label }}</span>
            </router-link>
          </li>
        </ul>

        <div class="nav-actions">
          <div class="user-info">
            <div class="user-avatar">
              <i class="fas fa-user"></i>
            </div>
            <span class="user-name">{{ user?.username || 'User' }}</span>
          </div>
          <button class="btn-logout" @click="logout">
            <i class="fas fa-sign-out-alt"></i>
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

    const navItems = [
      { path: '/tasks', icon: 'fas fa-list-check', label: 'Задачи' },
      { path: '/kanban', icon: 'fas fa-columns', label: 'Канбан' },
      { path: '/projects', icon: 'fas fa-folder', label: 'Проекты' },
      { path: '/time-tracking', icon: 'fas fa-clock', label: 'Таймер' },
      { path: '/reports', icon: 'fas fa-chart-pie', label: 'Отчеты' },
      { path: '/profile', icon: 'fas fa-user-circle', label: 'Профиль' }
    ]

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      user,
      navItems,
      logout
    }
  }
}
</script>

<style scoped>
.app-navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  margin: 0;
  border: none;
  border-radius: 0;
  background: var(--glass-bg) !important;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  padding: 0.75rem 0;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.brand-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: var(--accent-gradient);
  color: white;
  font-size: 1.25rem;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 800;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-item {
  margin: 0 0.25rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem !important;
  border-radius: 12px;
  color: var(--text-secondary) !important;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

.nav-link i {
  font-size: 1rem;
  transition: transform 0.3s ease;
}

.nav-link:hover {
  color: var(--accent-primary) !important;
  background: var(--surface-1);
  border-color: var(--glass-border);
}

.nav-link:hover i {
  transform: scale(1.1);
}

.nav-link.router-link-active {
  color: white !important;
  background: var(--accent-gradient);
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.nav-link.router-link-active i {
  color: white;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--surface-1);
  border: 1px solid var(--glass-border);
  border-radius: 50px;
  backdrop-filter: blur(10px);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
}

.user-name {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.btn-logout {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background: rgba(252, 129, 129, 0.15);
  border-color: var(--danger-color);
  color: var(--danger-color);
  transform: translateY(-2px);
}

.navbar-toggler {
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 0.5rem 0.75rem;
  background: var(--glass-bg);
  color: var(--text-primary);
}

.navbar-toggler:focus {
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
}

@media (max-width: 992px) {
  .app-navbar {
    padding: 0.5rem 0;
  }

  .navbar-collapse {
    margin-top: 1rem;
    padding: 1rem;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    backdrop-filter: blur(10px);
  }

  .nav-item {
    margin: 0.25rem 0;
  }

  .nav-link {
    padding: 0.75rem 1rem !important;
  }

  .nav-actions {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--glass-border);
    justify-content: center;
  }

  .user-name {
    display: none;
  }
}

@media (max-width: 576px) {
  .brand-text {
    display: none;
  }

  .brand-icon {
    width: 38px;
    height: 38px;
  }
}
</style>