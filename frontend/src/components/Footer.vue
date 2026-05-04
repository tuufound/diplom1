<template>
  <footer class="app-footer">
    <div class="footer-content glass">
      <div class="footer-left">
        <span class="footer-brand">
          <i class="fas fa-gem"></i>
          TaskFlow
        </span>
        <span class="footer-copyright">
          {{ currentYear }} — {{ $t('footer.tagline') }}
        </span>
      </div>

      <div class="footer-links">
        <a href="#" class="social-link" title="GitHub">
          <i class="fab fa-github"></i>
        </a>
        <a href="#" class="social-link" title="Telegram">
          <i class="fab fa-telegram"></i>
        </a>
        <a href="#" class="social-link" title="Email">
          <i class="fas fa-envelope"></i>
        </a>
      </div>

      <div class="footer-right">
        <div class="theme-toggle" @click="toggleTheme" :title="isDark ? $t('footer.themeLight') : $t('footer.themeDark')">
          <i class="fas" :class="isDark ? 'fa-sun' : 'fa-moon'"></i>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

export default {
  name: 'Footer',
  setup() {
    const themeStore = useThemeStore()
    const currentYear = computed(() => new Date().getFullYear())
    const isDark = computed(() => themeStore.isDark)

    const toggleTheme = () => {
      themeStore.toggleTheme()
    }

    return {
      currentYear,
      isDark,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.app-footer {
  margin-top: auto;
  padding: 1.5rem 2rem;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  border-radius: 20px;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
}

.footer-brand i {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-copyright {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.footer-links {
  display: flex;
  gap: 0.75rem;
}

.social-link {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--surface-1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.social-link:hover {
  background: var(--accent-gradient);
  border-color: transparent;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
}

.footer-right {
  display: flex;
  align-items: center;
}

.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: var(--surface-1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  background: var(--surface-2);
  color: var(--accent-primary);
  transform: rotate(15deg);
}

.theme-toggle i {
  font-size: 1rem;
}

@media (max-width: 992px) {
  .app-footer {
    padding: 1rem;
  }

  .footer-content {
    flex-direction: column;
    text-align: center;
    padding: 1.25rem;
    gap: 1rem;
  }

  .footer-left {
    flex-direction: column;
    gap: 0.5rem;
  }

  .footer-brand {
    font-size: 1.1rem;
  }
}

@media (max-width: 576px) {
  .footer-copyright {
    font-size: 0.8rem;
  }

  .social-link {
    width: 36px;
    height: 36px;
  }
}
</style>