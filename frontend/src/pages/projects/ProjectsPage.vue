<template>
  <div class="projects-page page-shell">
    <div class="page-content-surface">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">
          <i class="fas fa-folder me-2"></i>Проекты
        </h2>
        <p class="section-subtitle">Организуй задачи по пространствам и пригласи команду</p>
      </div>
      <div class="header-stats">
        <div class="stat-badge">
          <i class="fas fa-layer-group"></i>
          <span>{{ projects.length }}</span>
          <small>проектов</small>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <!-- Left Column: Create Project -->
      <div class="col-xl-4 col-lg-5">
        <div class="card create-card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-plus-circle me-2"></i>Новый проект
            </h5>
          </div>
          <div class="card-body">
            <div class="form-group">
              <label class="form-label">
                <i class="fas fa-tag me-1"></i>Название
              </label>
              <input
                v-model.trim="createForm.name"
                type="text"
                class="form-control"
                maxlength="120"
                placeholder="Например: Диплом, Релиз 2.0"
              >
            </div>
            <div class="form-group">
              <label class="form-label">
                <i class="fas fa-align-left me-1"></i>Описание
              </label>
              <textarea
                v-model.trim="createForm.description"
                class="form-control"
                rows="3"
                placeholder="Краткое описание проекта..."
              />
            </div>
            <button
              type="button"
              class="btn btn-primary w-100"
              :disabled="!createForm.name || creating"
              @click="submitCreate"
            >
              <span v-if="creating" class="spinner-border spinner-border-sm me-2" />
              <i v-else class="fas fa-rocket me-2"></i>
              Создать проект
            </button>
          </div>
        </div>
      </div>

      <!-- Right Column: Projects List -->
      <div class="col-xl-8 col-lg-7">
        <!-- Loading State -->
        <div v-if="loading" class="card">
          <div class="card-body text-center py-5">
            <div class="loading-spinner">
              <i class="fas fa-circle-notch fa-spin fa-2x"></i>
            </div>
            <p class="mt-2 mb-0 text-muted">Загрузка проектов...</p>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!projects.length" class="card">
          <div class="card-body text-center py-5">
            <div class="empty-icon">
              <i class="fas fa-folder-tree"></i>
            </div>
            <h5 class="mt-3 mb-2">Пока нет проектов</h5>
            <p class="text-muted mb-0">Создай первый проект слева и начни организовывать задачи</p>
          </div>
        </div>

        <!-- Projects Grid -->
        <div v-else class="projects-grid">
          <div v-for="project in projects" :key="project.id" class="project-card">
            <!-- Card Header -->
            <div class="project-card-header">
              <div class="project-icon">
                <i class="fas fa-folder"></i>
              </div>
              <div class="project-title-area">
                <template v-if="editingId !== project.id">
                  <h5 class="project-name">{{ project.name }}</h5>
                  <p class="project-desc">{{ project.description || 'Без описания' }}</p>
                </template>
                <template v-else>
                  <div class="edit-form">
                    <input v-model.trim="editForm.name" type="text" class="form-control mb-2" placeholder="Название">
                    <textarea v-model.trim="editForm.description" class="form-control" rows="2" placeholder="Описание" />
                    <div class="edit-actions mt-2">
                      <button class="btn btn-sm btn-primary" :disabled="saving" @click="saveEdit(project.id)">
                        <i class="fas fa-check me-1"></i>Сохранить
                      </button>
                      <button class="btn btn-sm btn-outline-secondary" :disabled="saving" @click="cancelEdit">
                        <i class="fas fa-times me-1"></i>Отмена
                      </button>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <!-- Card Meta -->
            <div class="project-card-meta">
              <div class="meta-item">
                <i class="fas fa-crown"></i>
                <span>{{ project.owner?.username }}</span>
              </div>
              <div class="meta-item">
                <i class="fas fa-users"></i>
                <span>{{ participantCount(project) }} участ.</span>
              </div>
            </div>

            <!-- Members Preview -->
            <div v-if="participantCount(project) > 1" class="members-preview">
              <div class="members-list">
                <div class="member-avatar owner-avatar" :title="project.owner?.username">
                  {{ getInitials(project.owner?.username) }}
                </div>
                <div
                  v-for="m in membershipsWithoutOwner(project).slice(0, 3)"
                  :key="m.id"
                  class="member-avatar"
                  :title="m.user?.username"
                >
                  {{ getInitials(m.user?.username) }}
                </div>
                <div
                  v-if="membershipsWithoutOwner(project).length > 3"
                  class="member-avatar more-avatar"
                >
                  +{{ membershipsWithoutOwner(project).length - 3 }}
                </div>
              </div>
            </div>

            <!-- Card Actions -->
            <div v-if="editingId !== project.id" class="project-card-actions">
              <router-link class="btn btn-sm btn-primary" :to="`/tasks/create?project=${project.id}`">
                <i class="fas fa-plus me-1"></i>Задача
              </router-link>
              <button
                v-if="canEditProject(project)"
                class="btn btn-sm btn-outline-secondary"
                title="Редактировать"
                @click="startEdit(project)"
              >
                <i class="fas fa-pen"></i>
              </button>
              <button
                v-if="isProjectOwner(project)"
                class="btn btn-sm btn-outline-danger"
                title="Удалить"
                @click="confirmDelete(project)"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>

            <!-- Invite Block (Owner Only) -->
            <div v-if="isProjectOwner(project)" class="invite-section">
              <button
                class="invite-toggle"
                :class="{ active: expandedProject === project.id }"
                @click="toggleInvite(project.id)"
              >
                <i class="fas fa-user-plus me-2"></i>
                {{ expandedProject === project.id ? 'Скрыть' : 'Пригласить' }}
                <i class="fas fa-chevron-down ms-auto"></i>
              </button>

              <div v-if="expandedProject === project.id" class="invite-form">
                <div class="invite-field">
                  <label class="invite-label" :for="`invite-role-${project.id}`">Роль</label>
                  <select
                    :id="`invite-role-${project.id}`"
                    v-model="inviteRoleByProject[project.id]"
                    class="form-select"
                  >
                    <option value="editor">Редактор</option>
                    <option value="viewer">Наблюдатель</option>
                  </select>
                </div>
                <div class="invite-field">
                  <label class="invite-label" :for="`invite-login-${project.id}`">Логин</label>
                  <input
                    :id="`invite-login-${project.id}`"
                    v-model.trim="inviteQueryByProject[project.id]"
                    type="text"
                    class="form-control"
                    placeholder="Введите логин"
                    autocomplete="username"
                    @input="onInviteInput(project.id)"
                    @keydown.enter.prevent="inviteByLogin(project)"
                  >
                </div>
                <button
                  type="button"
                  class="btn btn-primary w-100 invite-submit-btn"
                  :disabled="inviteLoading === project.id"
                  @click="inviteByLogin(project)"
                >
                  <span v-if="inviteLoading === project.id" class="spinner-border spinner-border-sm" />
                  <template v-else>
                    <i class="fas fa-user-plus me-1" />Пригласить
                  </template>
                </button>

                <div v-if="(inviteHitsByProject[project.id] || []).length" class="invite-results">
                  <div
                    v-for="u in inviteHitsByProject[project.id]"
                    :key="u.id"
                    class="invite-result-item"
                  >
                    <div class="result-avatar">{{ getInitials(u.username) }}</div>
                    <span class="result-name">{{ u.username }}</span>
                    <button
                      class="btn btn-sm btn-primary"
                      :disabled="inviteLoading === project.id"
                      @click="addMember(project, u)"
                    >
                      <i class="fas fa-plus"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Members List (collapsible) -->
            <div v-if="participantCount(project) >= 1" class="members-section">
              <button
                class="members-toggle"
                :class="{ active: expandedMembers === project.id }"
                @click="toggleMembers(project.id)"
              >
                <i class="fas fa-users me-2"></i>Участники
                <span class="members-count">{{ participantCount(project) }}</span>
                <i class="fas fa-chevron-down ms-auto"></i>
              </button>

              <div v-if="expandedMembers === project.id" class="members-full-list">
                <div class="member-row owner-row">
                  <div class="member-avatar-lg owner-avatar">{{ getInitials(project.owner?.username) }}</div>
                  <div class="member-info">
                    <span class="member-name">{{ project.owner?.username }}</span>
                    <span class="member-role-badge owner-badge">владелец</span>
                  </div>
                </div>
                <div
                  v-for="m in membershipsWithoutOwner(project)"
                  :key="m.id"
                  class="member-row"
                >
                  <div class="member-avatar-lg">{{ getInitials(m.user?.username) }}</div>
                  <div class="member-info">
                    <span class="member-name">{{ m.user?.username }}</span>
                    <span class="member-role-badge" :class="m.role === 'editor' ? 'editor-badge' : 'viewer-badge'">
                      {{ roleLabel(m.role) }}
                    </span>
                  </div>
                  <button
                    v-if="isProjectOwner(project)"
                    type="button"
                    class="btn btn-sm btn-outline-danger remove-btn"
                    title="Удалить из проекта"
                    @click="removeMember(project, m)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
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
    const expandedProject = ref(null)
    const expandedMembers = ref(null)
    const inviteQueryByProject = reactive({})
    const inviteHitsByProject = reactive({})
    const inviteRoleByProject = reactive({})
    let inviteTimers = {}

    const getInitials = (name) => {
      if (!name) return '?'
      return name.slice(0, 2).toUpperCase()
    }

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

    /** Участники без дубликата владельца (владелец показывается отдельной строкой). */
    const membershipsWithoutOwner = (p) =>
      (p.memberships || []).filter((m) => m.user?.id && m.user?.id !== p.owner?.id)

    const participantCount = (p) => membershipsWithoutOwner(p).length + (p.owner ? 1 : 0)

    const toggleInvite = (projectId) => {
      expandedProject.value = expandedProject.value === projectId ? null : projectId
    }

    const toggleMembers = (projectId) => {
      expandedMembers.value = expandedMembers.value === projectId ? null : projectId
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
        const memberIds = new Set((p?.memberships || []).map((m) => m.user?.id).filter(Boolean))
        if (p?.owner?.id) memberIds.add(p.owner.id)
        inviteHitsByProject[projectId] = data.filter(
          (u) => u.id !== user.value?.id && !memberIds.has(u.id)
        )
      } catch {
        inviteHitsByProject[projectId] = []
      }
    }

    const membershipErrorMessage = (d) => {
      if (!d || typeof d !== 'object') return null
      const pick = (v) => (Array.isArray(v) ? v[0] : v)
      return (
        pick(d.username) ||
        pick(d.user_id) ||
        pick(d.non_field_errors) ||
        (typeof d.detail === 'string' ? d.detail : null)
      )
    }

    const inviteByLogin = async (p) => {
      const login = String(inviteQueryByProject[p.id] || '').trim()
      if (!login) {
        toast.error('Введите логин пользователя')
        return
      }
      const role = inviteRoleByProject[p.id] || 'editor'
      inviteLoading.value = p.id
      try {
        await api.addProjectMembership(p.id, { username: login, role })
        toast.success(`Приглашён: ${login}`)
        inviteQueryByProject[p.id] = ''
        inviteHitsByProject[p.id] = []
        await loadProjects()
      } catch (e) {
        const msg = membershipErrorMessage(e.response?.data) || 'Не удалось добавить участника'
        toast.error(typeof msg === 'string' ? msg : 'Ошибка')
      } finally {
        inviteLoading.value = null
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
        const msg = membershipErrorMessage(e.response?.data) || 'Не удалось добавить участника'
        toast.error(typeof msg === 'string' ? msg : 'Ошибка')
      } finally {
        inviteLoading.value = null
      }
    }

    const removeMember = async (p, m) => {
      if (!window.confirm(`Удалить ${m.user?.username} из проекта?`)) return
      try {
        await api.removeProjectMembership(p.id, m.id)
        toast.success(`Участник удалён`)
        await loadProjects()
      } catch (e) {
        toast.error(e.response?.data?.detail || 'Не удалось удалить участника')
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
      expandedProject,
      expandedMembers,
      inviteQueryByProject,
      inviteHitsByProject,
      inviteRoleByProject,
      isProjectOwner,
      canEditProject,
      roleLabel,
      membershipsWithoutOwner,
      participantCount,
      getInitials,
      toggleInvite,
      toggleMembers,
      submitCreate,
      startEdit,
      cancelEdit,
      saveEdit,
      confirmDelete,
      onInviteInput,
      inviteByLogin,
      addMember,
      removeMember
    }
  }
}
</script>

<style scoped lang="scss">
.projects-page {
  max-width: 1400px;
  margin: 0 auto;
}

// Page Header
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
}

.header-stats {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: var(--surface-1);
  border: 1px solid var(--glass-border);
  border-radius: 50px;
  font-weight: 600;
  font-size: 1rem;
  color: var(--text-primary);

  i {
    color: var(--accent-primary);
  }

  small {
    color: var(--text-muted);
    font-size: 0.85rem;
    font-weight: 400;
  }
}

// Create Card
.create-card {
  position: sticky;
  top: 100px;
}

.create-card .card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  h5 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    font-size: 1rem;

    i {
      color: var(--accent-primary);
    }
  }
}

.form-group {
  margin-bottom: 1.25rem;
}

// Loading State
.loading-spinner {
  color: var(--accent-primary);
}

// Empty State
.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: var(--surface-1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--accent-primary);
}

// Projects Grid
.projects-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

// Project Card
.project-card {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  min-width: 0;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: var(--glass-border-strong);
    box-shadow: var(--glass-shadow-hover);
    transform: translateY(-2px);
  }
}

.project-card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.project-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.project-title-area {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.35rem;
}

.project-desc {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

.edit-form {
  .edit-actions {
    display: flex;
    gap: 0.5rem;
  }
}

.project-card-meta {
  display: flex;
  gap: 1.25rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--glass-border);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.875rem;

  i {
    color: var(--accent-primary);
    font-size: 0.85rem;
  }
}

// Members Preview
.members-preview {
  margin-bottom: 1rem;
}

.members-list {
  display: flex;
  gap: -8px;
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  border: 2px solid var(--glass-bg);
  margin-left: -8px;
  cursor: default;

  &:first-child {
    margin-left: 0;
  }
}

.owner-avatar {
  background: linear-gradient(135deg, #f6e05e, #d69e2e);
}

.more-avatar {
  background: var(--surface-2);
  color: var(--text-secondary);
  font-size: 0.65rem;
}

// Card Actions
.project-card-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

// Invite Section
.invite-section {
  border-top: 1px solid var(--glass-border);
  padding-top: 1rem;
  margin-bottom: 0.5rem;
  min-width: 0;
  max-width: 100%;
}

.invite-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: var(--surface-1);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover,
  &.active {
    background: var(--surface-2);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
  }

  i.fa-chevron-down {
    transition: transform 0.3s ease;
  }

  &.active i.fa-chevron-down {
    transform: rotate(180deg);
  }
}

.invite-form {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--surface-1);
  border-radius: 12px;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;

  .form-control,
  .form-select {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }
}

.invite-field {
  margin-bottom: 0.75rem;
}

.invite-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.35rem;
}

.invite-submit-btn {
  margin-top: 0.25rem;
}

.invite-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.invite-result-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: var(--glass-bg);
  border-radius: 10px;
}

.result-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
}

.result-name {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
}

// Members Section
.members-section {
  border-top: 1px solid var(--glass-border);
  padding-top: 0.75rem;
}

.members-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s ease;

  &:hover,
  &.active {
    color: var(--accent-primary);
  }

  .members-count {
    background: var(--surface-2);
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    font-size: 0.75rem;
  }

  i.fa-chevron-down {
    transition: transform 0.3s ease;
  }

  &.active i.fa-chevron-down {
    transform: rotate(180deg);
  }
}

.members-full-list {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.member-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem;
  background: var(--surface-1);
  border-radius: 12px;
  transition: background 0.2s ease;

  &:hover {
    background: var(--surface-2);
  }
}

.owner-row {
  background: rgba(246, 224, 94, 0.08);
}

.member-avatar-lg {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  flex-shrink: 0;
}

.owner-avatar {
  background: linear-gradient(135deg, #f6e05e, #d69e2e);
}

.member-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.member-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.member-role-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.owner-badge {
  background: rgba(246, 224, 94, 0.2);
  color: #b7791f;
}

.editor-badge {
  background: rgba(72, 187, 120, 0.15);
  color: var(--success-color);
}

.viewer-badge {
  background: rgba(99, 179, 237, 0.15);
  color: var(--info-color);
}

.remove-btn {
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.2s ease;

  &:hover {
    opacity: 1;
  }
}

// Responsive
@media (max-width: 992px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-stats {
    justify-content: flex-start;
  }

  .create-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .project-card {
    padding: 1rem;
  }

  .project-card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .project-icon {
    width: 44px;
    height: 44px;
    font-size: 1.25rem;
  }

  .project-card-meta {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .project-card-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 576px) {
  .member-row {
    padding: 0.5rem;
  }

  .member-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>