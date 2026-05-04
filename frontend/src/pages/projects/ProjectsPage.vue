<template>
  <div class="projects-page page-shell">
    <div class="projects-head">
      <div>
        <h2 class="page-title"><i class="fas fa-folder-open me-2"></i>Проекты</h2>
        <p class="section-subtitle">
          Совместные пространства для задач: создай проект, пригласи участников, выбирай проект при создании задачи.
        </p>
      </div>
      <router-link to="/tasks/create" class="btn btn-primary">
        <i class="fas fa-plus me-1"></i> Новая задача
      </router-link>
    </div>

    <div class="row g-3">
      <div class="col-lg-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="form-section-title mb-3">Новый проект</div>
            <div class="mb-3">
              <label class="form-label" for="new-project-name">Название</label>
              <input
                id="new-project-name"
                v-model.trim="createForm.name"
                type="text"
                class="form-control"
                maxlength="120"
                placeholder="Например: Диплом, Релиз 2.0"
              >
            </div>
            <div class="mb-3">
              <label class="form-label" for="new-project-desc">Описание</label>
              <textarea
                id="new-project-desc"
                v-model.trim="createForm.description"
                class="form-control"
                rows="3"
                placeholder="Необязательно"
              />
            </div>
            <button
              type="button"
              class="btn btn-primary w-100"
              :disabled="!createForm.name || creating"
              @click="submitCreate"
            >
              <span v-if="creating" class="spinner-border spinner-border-sm me-2" />
              Создать проект
            </button>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div v-if="loading" class="card">
          <div class="card-body text-center py-5 text-muted">Загрузка…</div>
        </div>
        <div v-else-if="!projects.length" class="card">
          <div class="card-body text-center py-5">
            <i class="fas fa-folder-plus fa-2x text-muted mb-3 d-block" />
            <p class="mb-2">Пока нет проектов</p>
            <p class="text-muted small mb-0">Создай первый слева — он появится в списке и в поле «Проект» при создании задачи.</p>
          </div>
        </div>
        <div v-else class="project-cards">
          <div v-for="p in projects" :key="p.id" class="card project-card mb-3">
            <div class="card-body">
              <div class="project-card-top">
                <div class="project-card-main">
                  <template v-if="editingId !== p.id">
                    <h5 class="mb-1">{{ p.name }}</h5>
                    <p class="text-muted small mb-2">{{ p.description || 'Без описания' }}</p>
                  </template>
                  <template v-else>
                    <div class="mb-2">
                      <label class="form-label small mb-1">Название</label>
                      <input v-model.trim="editForm.name" type="text" class="form-control form-control-sm" maxlength="120">
                    </div>
                    <div class="mb-2">
                      <label class="form-label small mb-1">Описание</label>
                      <textarea v-model.trim="editForm.description" class="form-control form-control-sm" rows="2" />
                    </div>
                    <div class="d-flex gap-2">
                      <button type="button" class="btn btn-sm btn-primary" :disabled="saving" @click="saveEdit(p.id)">
                        Сохранить
                      </button>
                      <button type="button" class="btn btn-sm btn-outline-secondary" :disabled="saving" @click="cancelEdit">
                        Отмена
                      </button>
                    </div>
                  </template>
                </div>
                <div v-if="editingId !== p.id" class="project-card-actions">
                  <router-link
                    class="btn btn-sm btn-primary"
                    :to="`/tasks/create?project=${p.id}`"
                  >
                    <i class="fas fa-plus me-1" /> Задача
                  </router-link>
                  <button
                    v-if="canEditProject(p)"
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    @click="startEdit(p)"
                  >
                    <i class="fas fa-pen" />
                  </button>
                  <button
                    v-if="isProjectOwner(p)"
                    type="button"
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDelete(p)"
                  >
                    <i class="fas fa-trash" />
                  </button>
                </div>
              </div>

              <div class="project-meta small text-muted mb-2">
                <span><i class="fas fa-user-shield me-1" />Владелец: {{ p.owner?.username }}</span>
                <span class="ms-3"><i class="fas fa-users me-1" />{{ (p.memberships || []).length }} участн.</span>
              </div>

              <div v-if="(p.memberships || []).length" class="member-chips mb-2">
                <span v-for="m in p.memberships" :key="m.id" class="member-chip">
                  {{ m.user?.username }}
                  <span class="role">{{ roleLabel(m.role) }}</span>
                </span>
              </div>

              <div v-if="isProjectOwner(p)" class="invite-block border-top pt-3 mt-2">
                <div class="form-section-title small mb-2">Пригласить участника</div>
                <div class="row g-2 align-items-end">
                  <div class="col-md-7">
                    <label class="form-label small mb-1">Поиск по логину</label>
                    <input
                      v-model="inviteQueryByProject[p.id]"
                      type="text"
                      class="form-control form-control-sm"
                      autocomplete="off"
                      placeholder="от 2 символов — затем нажмите на пользователя"
                      @input="onInviteInput(p.id)"
                    >
                  </div>
                  <div class="col-md-5">
                    <label class="form-label small mb-1">Роль для нового участника</label>
                    <select v-model="inviteRoleByProject[p.id]" class="form-select form-select-sm">
                      <option value="editor">Редактор</option>
                      <option value="viewer">Наблюдатель</option>
                    </select>
                  </div>
                </div>
                <ul v-if="(inviteHitsByProject[p.id] || []).length" class="invite-hits list-unstyled mb-0 mt-2">
                  <li v-for="u in inviteHitsByProject[p.id]" :key="u.id">
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-primary"
                      :disabled="inviteLoading === p.id"
                      @click="addMember(p, u)"
                    >
                      <i class="fas fa-user-plus me-1" />{{ u.username }}
                    </button>
                  </li>
                </ul>
                <p class="form-help small mb-0 mt-2">Добавлять участников может только владелец. Повтор одного пользователя недопустим.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export default {
  name: 'ProjectsPage',
  setup() {
    const authStore = useAuthStore()
    const toast = useToast()
    const user = computed(() => authStore.user)

    const projects = ref([])
    const loading = ref(true)
    const creating = ref(false)
    const saving = ref(false)
    const editingId = ref(null)
    const editForm = ref({ name: '', description: '' })
    const createForm = ref({ name: '', description: '' })
    const inviteLoading = ref(null)
    const inviteQueryByProject = reactive({})
    const inviteHitsByProject = reactive({})
    const inviteRoleByProject = reactive({})
    let inviteTimers = {}

    const myRoleOnProject = (p) => {
      const uid = user.value?.id
      if (!uid) return null
      if (p.owner?.id === uid) return 'owner'
      const m = (p.memberships || []).find((x) => x.user?.id === uid)
      return m?.role || null
    }

    const isProjectOwner = (p) => myRoleOnProject(p) === 'owner'

    const canEditProject = (p) => {
      const r = myRoleOnProject(p)
      return r === 'owner' || r === 'editor'
    }

    const roleLabel = (role) => {
      const map = { owner: 'владелец', editor: 'редактор', viewer: 'наблюдатель' }
      return map[role] || role
    }

    const loadProjects = async () => {
      loading.value = true
      try {
        const { data } = await api.getProjects()
        projects.value = Array.isArray(data) ? data : []
        for (const p of projects.value) {
          if (inviteRoleByProject[p.id] === undefined) {
            inviteRoleByProject[p.id] = 'editor'
          }
        }
      } catch (e) {
        toast.error(e.response?.data?.detail || 'Не удалось загрузить проекты')
        projects.value = []
      } finally {
        loading.value = false
      }
    }

    const submitCreate = async () => {
      const name = createForm.value.name.trim()
      if (!name) return
      creating.value = true
      try {
        await api.createProject({
          name,
          description: createForm.value.description.trim() || ''
        })
        toast.success('Проект создан')
        createForm.value = { name: '', description: '' }
        await loadProjects()
      } catch (e) {
        const msg =
          e.response?.data?.name?.[0] ||
          e.response?.data?.detail ||
          'Ошибка создания проекта'
        toast.error(typeof msg === 'string' ? msg : 'Ошибка создания проекта')
      } finally {
        creating.value = false
      }
    }

    const startEdit = (p) => {
      editingId.value = p.id
      editForm.value = { name: p.name, description: p.description || '' }
    }

    const cancelEdit = () => {
      editingId.value = null
    }

    const saveEdit = async (id) => {
      const name = editForm.value.name.trim()
      if (!name) {
        toast.error('Укажите название')
        return
      }
      saving.value = true
      try {
        await api.updateProject(id, {
          name,
          description: editForm.value.description.trim() || ''
        })
        toast.success('Проект обновлён')
        editingId.value = null
        await loadProjects()
      } catch (e) {
        toast.error(e.response?.data?.detail || 'Ошибка сохранения')
      } finally {
        saving.value = false
      }
    }

    const confirmDelete = (p) => {
      if (!window.confirm(`Удалить проект «${p.name}»? Задачи останутся без проекта.`)) return
      deleteProject(p.id)
    }

    const deleteProject = async (id) => {
      try {
        await api.deleteProject(id)
        toast.success('Проект удалён')
        await loadProjects()
      } catch (e) {
        toast.error(e.response?.data?.detail || 'Не удалось удалить')
      }
    }

    const onInviteInput = (projectId) => {
      if (inviteTimers[projectId]) clearTimeout(inviteTimers[projectId])
      inviteTimers[projectId] = setTimeout(() => runInviteSearch(projectId), 320)
    }

    const runInviteSearch = async (projectId) => {
      const q = String(inviteQueryByProject[projectId] || '').trim()
      if (q.length < 2) {
        inviteHitsByProject[projectId] = []
        return
      }
      try {
        const { data } = await api.searchUsers({ q })
        const p = projects.value.find((x) => x.id === projectId)
        const memberIds = new Set((p?.memberships || []).map((m) => m.user?.id))
        inviteHitsByProject[projectId] = data.filter(
          (u) => u.id !== user.value?.id && !memberIds.has(u.id)
        )
      } catch {
        inviteHitsByProject[projectId] = []
      }
    }

    const addMember = async (p, u) => {
      const role = inviteRoleByProject[p.id] || 'editor'
      inviteLoading.value = p.id
      try {
        await api.addProjectMembership(p.id, { user_id: u.id, role })
        toast.success(`Добавлен: ${u.username}`)
        inviteQueryByProject[p.id] = ''
        inviteHitsByProject[p.id] = []
        await loadProjects()
      } catch (e) {
        const d = e.response?.data
        const msg =
          (d?.user_id && d.user_id[0]) ||
          (d?.non_field_errors && d.non_field_errors[0]) ||
          d?.detail ||
          'Не удалось добавить участника'
        toast.error(typeof msg === 'string' ? msg : 'Ошибка')
      } finally {
        inviteLoading.value = null
      }
    }

    onMounted(() => {
      loadProjects()
    })

    return {
      user,
      projects,
      loading,
      creating,
      saving,
      editingId,
      editForm,
      createForm,
      inviteLoading,
      inviteQueryByProject,
      inviteHitsByProject,
      inviteRoleByProject,
      isProjectOwner,
      canEditProject,
      roleLabel,
      submitCreate,
      startEdit,
      cancelEdit,
      saveEdit,
      confirmDelete,
      onInviteInput,
      addMember
    }
  }
}
</script>

<style scoped>
.projects-page {
  max-width: 1100px;
  margin: 0 auto;
}

.projects-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.form-section-title {
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6f5d88;
  font-weight: 600;
}

.form-label {
  font-weight: 600;
  color: #29314f;
  font-size: 0.85rem;
}

.form-control,
.form-select {
  border-radius: 12px;
  border: 1px solid rgba(219, 199, 230, 0.85);
}

.project-card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.project-card-main {
  flex: 1;
  min-width: 200px;
}

.project-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: flex-start;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.member-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.member-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  background: rgba(246, 232, 245, 0.65);
  border: 1px solid rgba(216, 196, 226, 0.75);
  color: #4a3f63;
}

.member-chip .role {
  opacity: 0.75;
  font-size: 0.72rem;
}

.invite-hits li {
  margin-bottom: 4px;
}

.form-help {
  color: #7a6991;
}

@media (max-width: 768px) {
  .projects-head {
    flex-direction: column;
  }
}
</style>
