<template>
  <div class="task-form-container page-shell">
    <div class="page-content-surface">
    <div class="form-head">
      <div>
        <h2 class="page-title">
          <i class="fas" :class="isEditing ? 'fa-edit' : 'fa-plus'"></i>
          {{ isEditing ? $t('taskForm.editTitle') : $t('taskForm.newTitle') }}
        </h2>
        <p class="section-subtitle">{{ $t('taskForm.subtitle') }}</p>
      </div>
      <div class="form-head-actions">
        <button
          v-if="isEditing"
          type="button"
          class="btn btn-outline-secondary favorite-head-btn"
          :class="{ active: isFavorited }"
          :disabled="favoriteLoading"
          :title="$t('taskForm.favorite')"
          @click="toggleFavorite"
        >
          <i class="fas fa-star me-1"></i>
          {{ isFavorited ? $t('taskForm.inFavorites') : $t('taskForm.addFavorite') }}
        </button>
        <button type="button" class="btn btn-outline-secondary" @click="cancel">
          <i class="fas fa-arrow-left me-1"></i> {{ $t('taskForm.backList') }}
        </button>
      </div>
    </div>

    <form class="form-grid" @submit.prevent="handleSubmit">
      <div class="card form-card">
        <div class="card-body">
          <div class="form-section-title">{{ $t('taskForm.mainSection') }}</div>
          <div class="mb-3">
            <label for="title" class="form-label">{{ $t('taskForm.titleLabel') }}</label>
            <input
              type="text"
              class="form-control"
              id="title"
              v-model="form.title"
              :placeholder="$t('taskForm.titlePh')"
              required
            >
            <small class="form-help">{{ $t('taskForm.titleHelp') }}</small>
          </div>

          <div class="mb-3">
            <label for="description" class="form-label">{{ $t('taskForm.descLabel') }}</label>
            <textarea
              class="form-control"
              id="description"
              v-model="form.description"
              rows="4"
              :placeholder="$t('taskForm.descPh')"
            ></textarea>
          </div>
        </div>
      </div>

      <div class="card form-card">
        <div class="card-body">
          <div class="form-section-title">{{ $t('taskForm.statusPriority') }}</div>
          <div class="row g-3">
            <div class="col-md-6">
              <label for="status" class="form-label">{{ $t('taskForm.statusLabel') }}</label>
              <select class="form-select" id="status" v-model="form.status" required>
                <option value="todo">{{ $t('taskStatus.todo') }}</option>
                <option value="in_progress">{{ $t('taskStatus.in_progress') }}</option>
                <option value="done">{{ $t('taskStatus.done') }}</option>
                <option value="archived">{{ $t('taskStatus.archived') }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="priority" class="form-label">{{ $t('taskForm.priorityLabel') }}</label>
              <select class="form-select" id="priority" v-model="form.priority">
                <option value="">{{ $t('taskForm.noPriority') }}</option>
                <option v-for="priority in priorities" :key="priority.id" :value="priority.id">
                  {{ priority.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="divider"></div>

          <div class="form-section-title">{{ $t('taskForm.contextSection') }}</div>
          <div class="row g-3">
            <div class="col-md-6">
              <label for="project" class="form-label">{{ $t('taskForm.projectLabel') }}</label>
              <select
                class="form-select"
                id="project"
                v-model="form.project"
                :disabled="!isEditing && !!form.parent_task"
              >
                <option value="">{{ $t('taskForm.personalProject') }}</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
              <small class="form-help d-block mt-1">
                <template v-if="!isEditing && form.parent_task">{{ $t('taskForm.projectLockedByParent') }}</template>
                <template v-else>{{ $t('taskForm.noProjectHint') }}</template>
                <router-link v-if="!form.parent_task || isEditing" to="/projects">{{ $t('taskForm.goProjectsPage') }}</router-link>
              </small>
            </div>
            <div class="col-md-6">
              <label for="category" class="form-label">{{ $t('taskForm.categoryLabel') }}</label>
              <select class="form-select" id="category" v-model="form.category">
                <option value="">{{ $t('taskForm.noCategory') }}</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.icon || '📁' }} {{ category.name }}
                </option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="due_date" class="form-label">{{ $t('taskForm.dueLabel') }}</label>
              <input
                type="datetime-local"
                class="form-control"
                id="due_date"
                v-model="form.due_date"
              >
            </div>
            <div class="col-md-6">
              <label for="parent_task" class="form-label">{{ $t('taskForm.parentShortLabel') }}</label>
              <select class="form-select" id="parent_task" v-model="form.parent_task">
                <option value="">{{ $t('taskForm.noParentTask') }}</option>
                <option v-for="task in availableParentTasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
              <small class="form-help">{{ $t('taskForm.parentHelp') }}</small>
            </div>
          </div>

          <template v-if="canManageCollaborators">
            <div class="divider"></div>
            <div class="form-section-title">{{ $t('taskForm.coworkers') }}</div>
            <div class="mb-3">
              <label class="form-label" for="coworker-search">{{ $t('taskForm.coworkersLabel') }}</label>
              <small class="form-help d-block mb-2">{{ $t('taskForm.coworkersHelp') }}</small>
              <input
                id="coworker-search"
                v-model="userSearchQuery"
                type="text"
                class="form-control"
                autocomplete="off"
                :placeholder="$t('taskForm.coworkerPh')"
                @input="onSearchInput"
              >
              <ul v-if="searchResults.length" class="coworker-hits list-unstyled mb-0 mt-2">
                <li v-for="u in searchResults" :key="u.id">
                  <button type="button" class="btn btn-sm btn-outline-primary hit-btn" @click="addCollaborator(u)">
                    <i class="fas fa-user-plus me-1"></i>{{ u.username }}
                  </button>
                </li>
              </ul>
              <div v-if="selectedCollaborators.length" class="coworker-chips mt-2">
                <span v-for="c in selectedCollaborators" :key="c.id" class="coworker-chip">
                  {{ c.username }}
                  <button type="button" class="chip-remove" :title="$t('taskForm.removeCoworker')" @click="removeCollaborator(c.id)">×</button>
                </span>
              </div>
            </div>
          </template>
          <div v-else-if="isEditing && selectedCollaborators.length" class="mt-2">
            <div class="form-section-title">{{ $t('taskForm.coworkersLabel') }}</div>
            <p class="form-help mb-0">{{ selectedCollaborators.map((c) => c.username).join(', ') }}</p>
          </div>

          <div class="divider"></div>

          <div class="form-section-title">{{ $t('taskForm.activity') }}</div>
          <div class="form-check">
            <input type="checkbox" class="form-check-input" id="is_active" v-model="form.is_active">
            <label class="form-check-label" for="is_active">{{ $t('taskForm.activeTask') }}</label>
          </div>
        </div>
      </div>

      <div class="card form-actions">
        <div class="card-body action-bar">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <span>{{ isEditing ? $t('common.save') : $t('taskForm.create') }}</span>
          </button>
          <button type="button" class="btn btn-outline-secondary" @click="cancel">
            {{ $t('common.cancel') }}
          </button>
        </div>
      </div>
    </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'

export default {
  name: 'TaskFormPage',
  setup() {
    const { t } = useI18n()
    const route = useRoute()
    const router = useRouter()
    const toast = useToast()

    const form = ref({
      title: '',
      description: '',
      status: 'todo',
      priority: '',
      project: '',
      category: '',
      parent_task: '',
      due_date: '',
      is_active: true
    })

    const priorities = ref([])
    const categories = ref([])
    const projects = ref([])
    const loading = ref(false)
    const favoriteLoading = ref(false)
    const isFavorited = ref(false)
    const isEditing = computed(() => !!route.params.id)
    const taskAccessRole = ref(null)
    const selectedCollaborators = ref([])
    const userSearchQuery = ref('')
    const searchResults = ref([])
    let searchDebounce = null

    const canManageCollaborators = computed(() => {
      if (!isEditing.value) return true
      return taskAccessRole.value === 'owner'
    })

    const allTasks = ref([])
    const availableParentTasks = computed(() => {
      const currentTaskId = isEditing.value ? Number(route.params.id) : null
      return allTasks.value.filter((task) => task.id !== currentTaskId)
    })

    const fetchTask = async () => {
      if (isEditing.value) {
        try {
          const response = await api.getTask(route.params.id)
          const task = response.data
          form.value = {
            title: task.title,
            description: task.description,
            status: task.status,
            priority: task.priority?.id || '',
            project: task.project?.id || '',
            category: task.category?.id || '',
            parent_task: task.parent_task?.id || '',
            due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : '',
            is_active: task.is_active
          }
          isFavorited.value = !!task.is_favorited
          taskAccessRole.value = task.access_role
          selectedCollaborators.value = (task.collaborators || []).map((c) => ({
            id: c.id,
            username: c.username
          }))
        } catch (error) {
          toast.error(t('taskForm.loadError'))
          console.error('Error fetching task:', error)
        }
      }
    }

    const fetchPriorities = async () => {
      try {
        const response = await api.getPriorities()
        priorities.value = response.data
      } catch (error) {
        console.error('Error fetching priorities:', error)
      }
    }

    const fetchCategories = async () => {
      try {
        const response = await api.getCategories()
        categories.value = response.data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const fetchProjects = async () => {
      try {
        const response = await api.getProjects()
        projects.value = response.data
      } catch (error) {
        console.error('Error fetching projects:', error)
      }
    }

    const fetchAllTasks = async () => {
      try {
        const response = await api.getTasks()
        allTasks.value = response.data
      } catch (error) {
        console.error('Error fetching tasks for parent select:', error)
      }
    }

    /** Бэкенд требует совпадения project с родительской задачей — подтягиваем проект при выборе родителя. */
    const syncProjectFromParent = async (parentId) => {
      const id = Number(parentId)
      if (!parentId || Number.isNaN(id)) return
      try {
        const { data } = await api.getTask(id)
        form.value.project = data.project?.id ?? ''
      } catch (error) {
        console.error('syncProjectFromParent', error)
        toast.error(t('taskForm.loadError'))
      }
    }

    const runUserSearch = async () => {
      const q = userSearchQuery.value.trim()
      if (q.length < 2) {
        searchResults.value = []
        return
      }
      try {
        const { data } = await api.searchUsers({ q })
        const taken = new Set(selectedCollaborators.value.map((c) => c.id))
        searchResults.value = data.filter((u) => !taken.has(u.id))
      } catch (error) {
        console.error('searchUsers', error)
      }
    }

    const onSearchInput = () => {
      if (searchDebounce) clearTimeout(searchDebounce)
      searchDebounce = setTimeout(runUserSearch, 320)
    }

    const addCollaborator = (u) => {
      if (selectedCollaborators.value.some((c) => c.id === u.id)) return
      selectedCollaborators.value = [...selectedCollaborators.value, { id: u.id, username: u.username }]
      searchResults.value = searchResults.value.filter((x) => x.id !== u.id)
      userSearchQuery.value = ''
      searchResults.value = []
    }

    const removeCollaborator = (id) => {
      selectedCollaborators.value = selectedCollaborators.value.filter((c) => c.id !== id)
    }

    const handleSubmit = async () => {
      try {
        loading.value = true
        const payload = {
          ...form.value,
          priority: form.value.priority ? Number(form.value.priority) : null,
          project: form.value.project ? Number(form.value.project) : null,
          category: form.value.category ? Number(form.value.category) : null,
          parent_task: form.value.parent_task ? Number(form.value.parent_task) : null,
          due_date: form.value.due_date ? new Date(form.value.due_date).toISOString() : null
        }
        if (canManageCollaborators.value) {
          payload.collaborator_ids = selectedCollaborators.value.map((c) => c.id)
        }
        if (isEditing.value) {
          await api.updateTask(route.params.id, payload)
          toast.success(t('taskForm.updateOk'))
        } else {
          await api.createTask(payload)
          toast.success(t('taskForm.createOk'))
        }
        router.push('/tasks')
      } catch (error) {
        toast.error(isEditing.value ? t('taskForm.saveError') : t('taskForm.createError'))
        console.error('Error saving task:', error)
      } finally {
        loading.value = false
      }
    }

    const cancel = () => {
      router.push('/tasks')
    }

    const toggleFavorite = async () => {
      if (!isEditing.value) return
      try {
        favoriteLoading.value = true
        const { data } = await api.toggleTaskFavorite(route.params.id)
        isFavorited.value = data.is_favorited
      } catch (error) {
        toast.error(t('taskForm.favoriteError'))
        console.error('toggleFavorite', error)
      } finally {
        favoriteLoading.value = false
      }
    }

    watch(
      () => form.value.parent_task,
      (newParent) => {
        if (isEditing.value) return
        if (!newParent) return
        syncProjectFromParent(newParent)
      }
    )

    onMounted(async () => {
      if (!isEditing.value && route.query.parent) {
        form.value.parent_task = Number(route.query.parent)
      }
      if (!isEditing.value && route.query.project) {
        const pid = Number(route.query.project)
        if (!Number.isNaN(pid)) form.value.project = pid
      }
      fetchTask()
      fetchPriorities()
      fetchCategories()
      fetchProjects()
      await fetchAllTasks()
    })

    onUnmounted(() => {
      if (searchDebounce) clearTimeout(searchDebounce)
    })

    return {
      form,
      priorities,
      categories,
      projects,
      availableParentTasks,
      loading,
      favoriteLoading,
      isFavorited,
      isEditing,
      taskAccessRole,
      canManageCollaborators,
      selectedCollaborators,
      userSearchQuery,
      searchResults,
      onSearchInput,
      addCollaborator,
      removeCollaborator,
      handleSubmit,
      cancel,
      toggleFavorite
    }
  }
}
</script>

<style scoped>
.task-form-container {
  max-width: 1100px;
  margin: 0 auto;
}

.form-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.form-head-actions {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
}

.favorite-head-btn.active {
  color: #9a7b0a;
  border-color: rgba(212, 175, 55, 0.75);
  background: rgba(255, 248, 220, 0.95);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: start;
}

.form-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #29314f;
}

.form-section-title {
  font-size: 0.92rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6f5d88;
  margin-bottom: 10px;
}

.form-help {
  color: #7a6991;
  font-size: 0.78rem;
}

.form-control, .form-select {
  border-radius: 12px;
  border: 1px solid rgba(219, 199, 230, 0.85);
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}

.form-control:focus, .form-select:focus {
  border-color: rgba(168, 132, 206, 0.9);
  box-shadow: 0 0 0 0.22rem rgba(176, 131, 200, 0.24);
}

.form-card .card-body {
  padding: 16px;
}

.divider {
  height: 1px;
  background: rgba(224, 206, 232, 0.7);
  margin: 14px 0;
}

.form-actions {
  grid-column: 1 / -1;
}

.action-bar {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 12px 14px;
}

.coworker-hits .hit-btn {
  margin-bottom: 6px;
}

.coworker-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.coworker-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px 4px 10px;
  border-radius: 999px;
  background: rgba(232, 245, 255, 0.95);
  border: 1px solid rgba(140, 190, 230, 0.55);
  color: #2d5f87;
  font-size: 0.88rem;
}

.coworker-chip .chip-remove {
  border: none;
  background: transparent;
  color: #5a7a9a;
  line-height: 1;
  padding: 0 2px;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .task-form-container {
    padding: 0 15px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .btn {
    width: 100%;
  }

  .action-bar {
    position: sticky;
    bottom: 0;
    background: rgba(255, 255, 255, 0.96);
    border-top: 1px solid rgba(224, 206, 232, 0.7);
    margin: -2px -2px -2px;
    padding: 12px 12px;
    z-index: 2;
    border-radius: 0 0 16px 16px;
  }

  .form-head {
    flex-direction: column;
  }

}
</style>