<template>
  <div class="task-form-container page-shell">
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0">
          <i class="fas" :class="isEditing ? 'fa-edit' : 'fa-plus'"></i>
          {{ isEditing ? 'Редактировать задачу' : 'Создать новую задачу' }}
        </h4>
        <p class="section-subtitle mt-2 mb-0">Новый стиль формы: минимум шума, максимум читаемости.</p>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="title" class="form-label">Название задачи</label>
            <input
              type="text"
              class="form-control"
              id="title"
              v-model="form.title"
              placeholder="Введите название задачи"
              required
            >
          </div>

          <div class="mb-3">
            <label for="description" class="form-label">Описание</label>
            <textarea
              class="form-control"
              id="description"
              v-model="form.description"
              rows="4"
              placeholder="Введите описание задачи"
            ></textarea>
          </div>

          <div class="row mb-3">
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
                <option value="">Выберите приоритет</option>
                <option v-for="priority in priorities" :key="priority.id" :value="priority.id">
                  {{ priority.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
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
                <option value="">Выберите категорию</option>
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>
            <div class="col-md-6 mt-3 mt-md-0">
              <label for="parent_task" class="form-label">Родительская задача</label>
              <select class="form-select" id="parent_task" v-model="form.parent_task">
                <option value="">Без родительской задачи</option>
                <option v-for="task in availableParentTasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
            </div>
            <div class="col-md-6">
              <label for="due_date" class="form-label">Срок выполнения</label>
              <input
                type="datetime-local"
                class="form-control"
                id="due_date"
                v-model="form.due_date"
              >
            </div>
          </div>

          <div class="mb-3 form-check">
            <input type="checkbox" class="form-check-input" id="is_active" v-model="form.is_active">
            <label class="form-check-label" for="is_active">Активная задача</label>
          </div>

          <div class="d-flex gap-2 mt-4">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <span>{{ isEditing ? 'Сохранить' : 'Создать' }}</span>
            </button>
            <button type="button" class="btn btn-outline-secondary" @click="cancel">
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
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
  max-width: 900px;
  margin: 0 auto;
}

.card {
  border: 1px solid rgba(188, 204, 233, 0.9);
  box-shadow: 0 12px 30px rgba(35, 63, 123, 0.11);
  border-radius: 18px;
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  font-size: 1.25rem;
}

.card-body {
  padding: 2rem;
}

.form-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1b2a46;
}

.form-control, .form-select {
  border-radius: 12px;
  border: 1px solid #c6d3ed;
  padding: 0.75rem 1rem;
  transition: all 0.2s ease;
}

.form-control:focus, .form-select:focus {
  border-color: #8aa7ff;
  box-shadow: 0 0 0 0.22rem rgba(119, 146, 255, 0.22);
}

.btn-primary {
  padding: 0.75rem 1.5rem;
}

.btn-outline-secondary {
  padding: 0.75rem 1.5rem;
}

@media (max-width: 768px) {
  .task-form-container {
    padding: 0 15px;
  }

  .d-flex.gap-2 {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>