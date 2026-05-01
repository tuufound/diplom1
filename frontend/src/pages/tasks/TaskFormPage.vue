<template>
  <div class="task-form-container page-shell">
    <div class="form-head">
      <div>
        <h2 class="page-title">
          <i class="fas" :class="isEditing ? 'fa-edit' : 'fa-plus'"></i>
          {{ isEditing ? 'Редактирование' : 'Новая задача' }}
        </h2>
        <p class="section-subtitle">Заполни только важное — остальное можно добавить позже.</p>
      </div>
      <div class="form-head-actions">
        <button type="button" class="btn btn-outline-secondary" @click="cancel">
          <i class="fas fa-arrow-left me-1"></i> К списку
        </button>
      </div>
    </div>

    <form class="form-grid" @submit.prevent="handleSubmit">
      <div class="card form-card">
        <div class="card-body">
          <div class="form-section-title">Основное</div>
          <div class="mb-3">
            <label for="title" class="form-label">Название</label>
            <input
              type="text"
              class="form-control"
              id="title"
              v-model="form.title"
              placeholder="Например: Подготовить отчет"
              required
            >
            <small class="form-help">Коротко: так задачу проще найти.</small>
          </div>

          <div class="mb-3">
            <label for="description" class="form-label">Описание</label>
            <textarea
              class="form-control"
              id="description"
              v-model="form.description"
              rows="4"
              placeholder="Контекст, критерии готовности, ссылки…"
            ></textarea>
          </div>
        </div>
      </div>

      <div class="card form-card">
        <div class="card-body">
          <div class="form-section-title">Статус и приоритет</div>
          <div class="row g-3">
            <div class="col-md-6">
              <label for="status" class="form-label">Статус</label>
              <select class="form-select" id="status" v-model="form.status" required>
                <option value="todo">К выполнению</option>
                <option value="in_progress">В процессе</option>
                <option value="done">Выполнено</option>
                <option value="archived">В архиве</option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="priority" class="form-label">Приоритет</label>
              <select class="form-select" id="priority" v-model="form.priority">
                <option value="">Без приоритета</option>
                <option v-for="priority in priorities" :key="priority.id" :value="priority.id">
                  {{ priority.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="divider"></div>

          <div class="form-section-title">Контекст</div>
          <div class="row g-3">
            <div class="col-md-6">
              <label for="project" class="form-label">Проект</label>
              <select class="form-select" id="project" v-model="form.project">
                <option value="">Личная задача</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="category" class="form-label">Категория</label>
              <select class="form-select" id="category" v-model="form.category">
                <option value="">Без категории</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.icon || '📁' }} {{ category.name }}
                </option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="due_date" class="form-label">Срок</label>
              <input
                type="datetime-local"
                class="form-control"
                id="due_date"
                v-model="form.due_date"
              >
            </div>
            <div class="col-md-6">
              <label for="parent_task" class="form-label">Родитель</label>
              <select class="form-select" id="parent_task" v-model="form.parent_task">
                <option value="">Без родительской задачи</option>
                <option v-for="task in availableParentTasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
              <small class="form-help">Если это подзадача — выбери родителя.</small>
            </div>
          </div>

          <div class="divider"></div>

          <div class="form-section-title">Активность</div>
          <div class="form-check">
            <input type="checkbox" class="form-check-input" id="is_active" v-model="form.is_active">
            <label class="form-check-label" for="is_active">Активная задача</label>
          </div>
        </div>
      </div>

      <div class="card form-actions">
        <div class="card-body action-bar">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <span>{{ isEditing ? 'Сохранить' : 'Создать' }}</span>
          </button>
          <button type="button" class="btn btn-outline-secondary" @click="cancel">
            Отмена
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'

export default {
  name: 'TaskFormPage',
  setup() {
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
    const isEditing = computed(() => !!route.params.id)
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
        } catch (error) {
          toast.error('Ошибка загрузки задачи')
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
        if (isEditing.value) {
          await api.updateTask(route.params.id, payload)
          toast.success('Задача успешно обновлена')
        } else {
          await api.createTask(payload)
          toast.success('Задача успешно создана')
        }
        router.push('/tasks')
      } catch (error) {
        toast.error(isEditing.value ? 'Ошибка обновления задачи' : 'Ошибка создания задачи')
        console.error('Error saving task:', error)
      } finally {
        loading.value = false
      }
    }

    const cancel = () => {
      router.push('/tasks')
    }

    onMounted(() => {
      if (!isEditing.value && route.query.parent) {
        form.value.parent_task = Number(route.query.parent)
      }
      fetchTask()
      fetchPriorities()
      fetchCategories()
      fetchProjects()
      fetchAllTasks()
    })

    return {
      form,
      priorities,
      categories,
      projects,
      availableParentTasks,
      loading,
      isEditing,
      handleSubmit,
      cancel
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