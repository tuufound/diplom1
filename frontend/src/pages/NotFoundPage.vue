<template>
  <div class="nf-shell page-shell">
    <div class="card nf-card">
      <div class="card-body text-center">
        <div class="nf-badge">404</div>
        <h2 class="mb-2">Страница не найдена</h2>
        <p class="section-subtitle mb-4">Похоже, ссылка устарела или была введена с ошибкой.</p>
        <router-link to="/tasks" class="btn btn-primary">
          <i class="fas fa-home me-2"></i>К задачам
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundPage'
}
</script>

<style scoped>
.nf-shell {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 170px);
  padding: 18px;
}

.nf-card {
  width: min(640px, 100%);
}

.nf-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 86px;
  height: 86px;
  border-radius: 26px;
  color: #ffffff;
  background: linear-gradient(135deg, var(--brand-a), var(--brand-b));
  box-shadow: 0 16px 30px rgba(136, 110, 149, 0.24);
  font-weight: 800;
  font-size: 1.5rem;
  margin-bottom: 14px;
}

@media (max-width: 576px) {
  .nf-shell {
    min-height: auto;
    padding: 12px;
  }
}
</style>