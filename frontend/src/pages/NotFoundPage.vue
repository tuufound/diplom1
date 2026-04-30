<template>
  <div class="not-found-container">
    <div class="not-found-content text-center">
      <i class="fas fa-exclamation-triangle fa-5x text-warning mb-4"></i>
      <h1 class="display-1 fw-bold">404</h1>
      <h2 class="mb-3">Страница не найдена</h2>
      <p class="text-muted mb-4">Извините, запрашиваемая страница не существует.</p>
      <router-link to="/tasks" class="btn btn-primary btn-lg">
        <i class="fas fa-home me-2"></i>Вернуться на главную
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundPage'
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.not-found-content {
  max-width: 600px;
  padding: 40px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.display-1 {
  font-size: 5rem;
  color: #6c757d;
}

.btn-primary {
  background-color: #42b983;
  border-color: #42b983;
  padding: 12px 24px;
  font-size: 1.1rem;
}

.btn-primary:hover {
  background-color: #3aa876;
  border-color: #3aa876;
}

@media (max-width: 576px) {
  .not-found-content {
    padding: 30px 20px;
  }

  .display-1 {
    font-size: 4rem;
  }
}
</style>