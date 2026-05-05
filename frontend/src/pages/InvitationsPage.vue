<template>
  <div class="invitations-page page-shell">
    <div class="page-content-surface">
      <div class="page-header">
        <h2 class="page-title">
          <i class="fas fa-envelope me-2"></i>Приглашения
        </h2>
      </div>

      <div v-if="loading" class="card">
        <div class="card-body text-center py-5">
          <i class="fas fa-circle-notch fa-spin fa-2x"></i>
        </div>
      </div>

      <div v-else-if="!invitations.length" class="card">
        <div class="card-body text-center py-5">
          <i class="fas fa-inbox fa-3x mb-3 text-muted"></i>
          <p class="text-muted">Нет приглашений</p>
        </div>
      </div>

      <div v-else class="invitations-list">
        <div v-for="inv in invitations" :key="inv.id" class="card mb-3">
          <div class="card-body">
            <div class="d-flex align-items-center gap-3">
              <div class="flex-grow-1">
                <h5 class="mb-1">{{ inv.project_name }}</h5>
                <small class="text-muted">От: {{ inv.inviter?.username }} · Роль: {{ inv.role }}</small>
              </div>
              <button class="btn btn-sm btn-success" @click="respond(inv.id, 'accept')">
                <i class="fas fa-check"></i>
              </button>
              <button class="btn btn-sm btn-outline-secondary" @click="respond(inv.id, 'decline')">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export default {
  setup() {
    const toast = useToast()
    const invitations = ref([])
    const loading = ref(true)

    const load = async () => {
      loading.value = true
      try {
        const { data } = await api.getInvitations()
        invitations.value = data
      } catch (e) {
        toast.error('Ошибка загрузки')
      } finally {
        loading.value = false
      }
    }

    const respond = async (id, action) => {
      try {
        await api.respondInvitation(id, action)
        toast.success(action === 'accept' ? 'Приглашение принято' : 'Отклонено')
        await load()
      } catch (e) {
        toast.error('Ошибка')
      }
    }

    onMounted(load)

    return { invitations, loading, respond }
  }
}
</script>

<style scoped>
.invitations-list {
  max-width: 800px;
}
</style>
