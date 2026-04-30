<template>
  <footer class="footer mt-auto py-3 bg-light">
    <div class="container">
      <div class="row">
        <div class="col-md-6 text-center text-md-start">
          <p class="mb-0">
            &copy; {{ currentYear }} Task Planner. Все права защищены.
          </p>
        </div>
        <div class="col-md-6 text-center text-md-end">
          <div class="social-links">
            <a href="#" class="text-muted me-2"><i class="fab fa-github"></i></a>
            <a href="#" class="text-muted me-2"><i class="fab fa-twitter"></i></a>
            <a href="#" class="text-muted"><i class="fab fa-linkedin"></i></a>
          </div>
        </div>
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
.footer {
  border-top: 1px solid #dee2e6;
  padding: 1rem 0;
  background-color: #f8f9fa !important;
}

.social-links a {
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.social-links a:hover {
  color: #42b983 !important;
  transform: translateY(-2px);
}
</style>