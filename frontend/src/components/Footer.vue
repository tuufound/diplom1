<template>
  <footer class="app-footer">
    <div class="app-footer-inner">
      <div class="copy">
        &copy; {{ currentYear }} Task Planner
      </div>
      <div class="links">
        <a href="#" aria-label="GitHub"><i class="fab fa-github"></i></a>
        <a href="#" aria-label="Twitter"><i class="fab fa-twitter"></i></a>
        <a href="#" aria-label="LinkedIn"><i class="fab fa-linkedin"></i></a>
      </div>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'Footer',
  setup() {
    const currentYear = computed(() => new Date().getFullYear())

    return {
      currentYear
    }
  }
}
</script>

<style scoped>
.app-footer {
  margin-top: auto;
  padding: 14px 18px;
}

.app-footer-inner {
  max-width: 1440px;
  margin: 0 auto;
  border: 1px solid rgba(224, 206, 232, 0.7);
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(8px);
  border-radius: 16px;
  box-shadow: 0 10px 22px rgba(136, 110, 149, 0.12);
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.copy {
  color: #6d5a86;
  font-size: 0.9rem;
}

.links {
  display: inline-flex;
  gap: 10px;
}

.links a {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(219, 199, 230, 0.8);
  background: rgba(255, 255, 255, 0.9);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #5d4f80;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.links a:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(136, 110, 149, 0.18);
  background: rgba(248, 238, 252, 0.95);
}
</style>