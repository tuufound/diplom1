<template>
  <div class="time-page page-shell">
    <div class="time-surface">
      <div class="time-head">
        <div>
          <h2 class="page-title"><i class="fas fa-clock me-2"></i>Время</h2>
          <p class="section-subtitle">Быстрый старт таймера, чистая история, простой Pomodoro.</p>
        </div>
      </div>

      <div class="time-grid">
      <section class="card">
        <div class="card-header"><h5 class="mb-0">Активный таймер</h5></div>
        <div class="card-body">
          <div v-if="activeTimeEntry" class="active-timer">
            <div class="active-top">
              <div class="active-title">
                <div class="task-name">{{ activeTimeEntry.task.title }}</div>
                <div class="task-meta">{{ formatDate(activeTimeEntry.start_time) }}</div>
              </div>
              <button class="btn btn-danger" @click="stopTimer">
                <i class="fas fa-stop me-1"></i> Стоп
              </button>
            </div>
            <div v-if="activeTimeEntry.description" class="active-desc">{{ activeTimeEntry.description }}</div>
            <div class="timer-display">
              <span class="display-4">{{ formattedTime }}</span>
            </div>
          </div>
          <div v-else class="no-active">
            <i class="fas fa-clock"></i>
            <div>
              <div class="no-title">Нет активного таймера</div>
              <div class="no-sub">Запусти таймер справа или из списка задач.</div>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header"><h5 class="mb-0">Запустить таймер</h5></div>
        <div class="card-body">
          <form @submit.prevent="startNewTimer" class="start-form">
            <div class="mb-3">
              <label for="task" class="form-label">Задача</label>
              <select class="form-select" id="task" v-model="newTimer.task" required>
                <option value="">Выберите задачу</option>
                <option v-for="task in tasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label for="description" class="form-label">Описание</label>
              <textarea
                class="form-control"
                id="description"
                v-model="newTimer.description"
                rows="3"
                placeholder="Коротко: чем занимаешься?"
              ></textarea>
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="startingTimer">
              <span v-if="startingTimer" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <span>Старт</span>
            </button>
          </form>
        </div>
      </section>

      <section class="card">
        <div class="card-header"><h5 class="mb-0">История</h5></div>
        <div class="card-body">
          <div v-if="loading" class="loading-state">
            <div class="spinner-border" role="status"></div>
          </div>
          <div v-else-if="timeEntries.length === 0" class="empty-state">
            <i class="fas fa-history"></i>
            <p>История пуста</p>
          </div>
          <div v-else class="entry-list">
            <article v-for="entry in timeEntries" :key="entry.id" class="entry-row">
              <div class="entry-main">
                <div class="entry-title">{{ entry.task.title }}</div>
                <div class="entry-sub">
                  {{ formatDateTime(entry.start_time) }} → {{ entry.end_time ? formatDateTime(entry.end_time) : 'Активно' }}
                  · <strong>{{ formatDuration(entry.duration) }}</strong>
                </div>
                <div v-if="entry.description" class="entry-desc">{{ truncateText(entry.description, 80) }}</div>
              </div>
              <div class="entry-actions">
                <button class="icon-btn" @click="openEditEntry(entry)" title="Редактировать">
                  <i class="fas fa-pen"></i>
                </button>
                <button class="icon-btn danger" @click="requestDeleteEntry(entry.id)" title="Удалить">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header"><h5 class="mb-0">Pomodoro</h5></div>
        <div class="card-body">
          <div class="pomodoro">
            <div class="pomodoro-time">{{ pomodoroDisplay }}</div>
            <div class="pomodoro-sub">{{ pomodoroWorkMode ? 'Фокус 25 минут' : 'Перерыв 5 минут' }}</div>
            <div class="pomodoro-actions">
              <button class="btn btn-outline-success" @click="startPomodoro" :disabled="pomodoroRunning">Старт</button>
              <button class="btn btn-outline-warning" @click="pausePomodoro" :disabled="!pomodoroRunning">Пауза</button>
              <button class="btn btn-outline-secondary" @click="resetPomodoro">Сброс</button>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header"><h5 class="mb-0">Ручной ввод</h5></div>
        <div class="card-body">
          <form @submit.prevent="saveManualEntry">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label" for="manualTask">Задача</label>
                <select id="manualTask" class="form-select" v-model="manualEntry.task" required>
                  <option value="">Выберите задачу</option>
                  <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.title }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label" for="manualDescription">Описание</label>
                <input id="manualDescription" class="form-control" v-model="manualEntry.description" placeholder="Опционально">
              </div>
              <div class="col-md-6">
                <label class="form-label" for="manualStart">Начало</label>
                <input id="manualStart" type="datetime-local" class="form-control" v-model="manualEntry.start_time" required>
              </div>
              <div class="col-md-6">
                <label class="form-label" for="manualEnd">Конец</label>
                <input id="manualEnd" type="datetime-local" class="form-control" v-model="manualEntry.end_time" required>
              </div>
            </div>
            <button type="submit" class="btn btn-outline-secondary w-100 mt-3" :disabled="savingManual">
              <span v-if="savingManual" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Сохранить
            </button>
          </form>
        </div>
      </section>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-backdrop-custom">
      <div class="modal-card">
        <h5 class="mb-3">Редактирование записи времени</h5>
        <div class="mb-2">
          <label class="form-label">Задача</label>
          <select class="form-select" v-model="editEntryForm.task">
            <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.title }}</option>
          </select>
        </div>
        <div class="mb-2">
          <label class="form-label">Начало</label>
          <input type="datetime-local" class="form-control" v-model="editEntryForm.start_time">
        </div>
        <div class="mb-2">
          <label class="form-label">Конец</label>
          <input type="datetime-local" class="form-control" v-model="editEntryForm.end_time">
        </div>
        <div class="mb-3">
          <label class="form-label">Описание</label>
          <textarea class="form-control" rows="2" v-model="editEntryForm.description"></textarea>
        </div>
        <div class="d-flex gap-2 justify-content-end">
          <button class="btn btn-outline-secondary" @click="showEditModal = false">Отмена</button>
          <button class="btn btn-primary" @click="saveEditedEntry">Сохранить</button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="modal-backdrop-custom">
      <div class="modal-card">
        <h5 class="mb-2">Удалить запись?</h5>
        <p class="text-muted mb-3">Это действие нельзя отменить.</p>
        <div class="d-flex gap-2 justify-content-end">
          <button class="btn btn-outline-secondary" @click="showDeleteModal = false">Отмена</button>
          <button class="btn btn-danger" @click="confirmDeleteEntry">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'

export default {
  name: 'TimeTrackingPage',
  setup() {
    const toast = useToast()

    const timeEntries = ref([])
    const tasks = ref([])
    const loading = ref(false)
    const startingTimer = ref(false)
    const savingManual = ref(false)

    const newTimer = ref({
      task: '',
      description: ''
    })
    const manualEntry = ref({
      task: '',
      start_time: '',
      end_time: '',
      description: ''
    })

    const activeTimeEntry = computed(() => {
      return timeEntries.value.find(entry => !entry.end_time)
    })

    const formattedTime = ref('00:00:00')
    let timerInterval = null
    const pomodoroSeconds = ref(25 * 60)
    const pomodoroRunning = ref(false)
    const pomodoroWorkMode = ref(true)
    let pomodoroInterval = null
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const deleteEntryId = ref(null)
    const editEntryForm = ref({
      id: null,
      task: '',
      start_time: '',
      end_time: '',
      description: ''
    })
    const pomodoroDisplay = computed(() => {
      const mm = Math.floor(pomodoroSeconds.value / 60).toString().padStart(2, '0')
      const ss = (pomodoroSeconds.value % 60).toString().padStart(2, '0')
      return `${mm}:${ss}`
    })

    const fetchTimeEntries = async () => {
      try {
        loading.value = true
        const response = await api.getTimeEntries()
        timeEntries.value = response.data
      } catch (error) {
        toast.error('Ошибка загрузки истории времени')
        console.error('Error fetching time entries:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchTasks = async () => {
      try {
        const response = await api.getTasks()
        tasks.value = response.data.filter(task => task.is_active)
      } catch (error) {
        toast.error('Ошибка загрузки задач')
        console.error('Error fetching tasks:', error)
      }
    }

    const startNewTimer = async () => {
      if (!newTimer.value.task) {
        toast.error('Пожалуйста, выберите задачу')
        return
      }

      try {
        startingTimer.value = true
        await api.startTimeEntry(newTimer.value.task, {
          description: newTimer.value.description
        })
        toast.success('Таймер запущен')
        await fetchTimeEntries()
        newTimer.value = {
          task: '',
          description: ''
        }
      } catch (error) {
        toast.error('Ошибка запуска таймера')
        console.error('Error starting timer:', error)
      } finally {
        startingTimer.value = false
      }
    }

    const stopTimer = async () => {
      if (!activeTimeEntry.value) return

      try {
        await api.stopTimeEntry(activeTimeEntry.value.id)
        toast.success('Таймер остановлен')
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка остановки таймера')
        console.error('Error stopping timer:', error)
      }
    }

    const toLocalDateTime = (value) => {
      if (!value) return ''
      return new Date(value).toISOString().slice(0, 16)
    }

    const openEditEntry = (entry) => {
      editEntryForm.value = {
        id: entry.id,
        task: entry.task.id,
        start_time: toLocalDateTime(entry.start_time),
        end_time: toLocalDateTime(entry.end_time),
        description: entry.description || ''
      }
      showEditModal.value = true
    }

    const saveEditedEntry = async () => {
      try {
        await api.updateTimeEntry(editEntryForm.value.id, {
          task: Number(editEntryForm.value.task),
          start_time: toIsoString(editEntryForm.value.start_time),
          end_time: toIsoString(editEntryForm.value.end_time),
          description: editEntryForm.value.description || ''
        })
        toast.success('Запись обновлена')
        showEditModal.value = false
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка обновления записи')
      }
    }

    const requestDeleteEntry = (id) => {
      deleteEntryId.value = id
      showDeleteModal.value = true
    }

    const confirmDeleteEntry = async () => {
      try {
        await api.deleteTimeEntry(deleteEntryId.value)
        showDeleteModal.value = false
        deleteEntryId.value = null
        toast.success('Запись времени удалена')
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка удаления записи времени')
        console.error('Error deleting time entry:', error)
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return format(parseISO(dateString), 'dd MMM yyyy', { locale: ru })
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      return format(parseISO(dateString), 'dd MMM yyyy, HH:mm', { locale: ru })
    }

    const formatDuration = (durationString) => {
      if (!durationString) return 'Активно'

      // Parse duration string (assuming format like "HH:MM:SS")
      const parts = durationString.split(':')
      if (parts.length === 3) {
        const hours = parseInt(parts[0])
        const minutes = parseInt(parts[1])
        const seconds = parseInt(parts[2])

        if (hours > 0) {
          return `${hours}ч ${minutes}м`
        } else if (minutes > 0) {
          return `${minutes}м ${seconds}с`
        } else {
          return `${seconds}с`
        }
      }

      return durationString
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const toIsoString = (localDateTime) => {
      return localDateTime ? new Date(localDateTime).toISOString() : null
    }

    const saveManualEntry = async () => {
      const start = new Date(manualEntry.value.start_time)
      const end = new Date(manualEntry.value.end_time)
      if (end <= start) {
        toast.error('Время окончания должно быть позже времени начала')
        return
      }

      try {
        savingManual.value = true
        await api.createTimeEntry({
          task: Number(manualEntry.value.task),
          start_time: toIsoString(manualEntry.value.start_time),
          end_time: toIsoString(manualEntry.value.end_time),
          description: manualEntry.value.description || ''
        })
        toast.success('Запись времени добавлена')
        manualEntry.value = { task: '', start_time: '', end_time: '', description: '' }
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка ручного ввода времени')
      } finally {
        savingManual.value = false
      }
    }

    const updateTimerDisplay = () => {
      if (activeTimeEntry.value && activeTimeEntry.value.start_time) {
        const startTime = new Date(activeTimeEntry.value.start_time)
        const now = new Date()
        const diff = now - startTime

        const hours = Math.floor(diff / (1000 * 60 * 60))
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
        const seconds = Math.floor((diff % (1000 * 60)) / 1000)

        formattedTime.value = [
          hours.toString().padStart(2, '0'),
          minutes.toString().padStart(2, '0'),
          seconds.toString().padStart(2, '0')
        ].join(':')
      }
    }

    const pomodoroTick = () => {
      if (pomodoroSeconds.value <= 1) {
        pomodoroWorkMode.value = !pomodoroWorkMode.value
        pomodoroSeconds.value = pomodoroWorkMode.value ? 25 * 60 : 5 * 60
        toast.info(pomodoroWorkMode.value ? 'Новая фокус-сессия' : 'Время перерыва')
        return
      }
      pomodoroSeconds.value -= 1
    }

    const startPomodoro = () => {
      if (pomodoroRunning.value) return
      pomodoroRunning.value = true
      pomodoroInterval = setInterval(pomodoroTick, 1000)
    }

    const pausePomodoro = () => {
      pomodoroRunning.value = false
      if (pomodoroInterval) {
        clearInterval(pomodoroInterval)
        pomodoroInterval = null
      }
    }

    const resetPomodoro = () => {
      pausePomodoro()
      pomodoroWorkMode.value = true
      pomodoroSeconds.value = 25 * 60
    }

    onMounted(() => {
      fetchTimeEntries()
      fetchTasks()

      // Start timer update interval
      timerInterval = setInterval(updateTimerDisplay, 1000)
    })

    onUnmounted(() => {
      // Clean up interval
      if (timerInterval) {
        clearInterval(timerInterval)
      }
      if (pomodoroInterval) {
        clearInterval(pomodoroInterval)
      }
    })

    return {
      timeEntries,
      tasks,
      loading,
      startingTimer,
      savingManual,
      newTimer,
      manualEntry,
      activeTimeEntry,
      formattedTime,
      pomodoroDisplay,
      pomodoroRunning,
      pomodoroWorkMode,
      showEditModal,
      showDeleteModal,
      editEntryForm,
      startNewTimer,
      stopTimer,
      openEditEntry,
      requestDeleteEntry,
      saveEditedEntry,
      confirmDeleteEntry,
      formatDate,
      formatDateTime,
      formatDuration,
      truncateText,
      saveManualEntry,
      startPomodoro,
      pausePomodoro,
      resetPomodoro
    }
  }
}
</script>

<style scoped>
.time-page {
  max-width: 1320px;
  margin: 0 auto;
}

.time-surface {
  position: relative;
  border-radius: 24px;
  padding: 16px;
  border: 1px solid rgba(224, 206, 232, 0.7);
  background:
    radial-gradient(circle at 10% 16%, rgba(245, 195, 210, 0.25), transparent 42%),
    radial-gradient(circle at 94% 10%, rgba(213, 193, 246, 0.22), transparent 46%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(252, 241, 248, 0.66));
  box-shadow: 0 16px 36px rgba(136, 110, 149, 0.12);
  backdrop-filter: blur(10px);
}

.time-head {
  margin-bottom: 14px;
}

.time-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: 12px;
  align-items: start;
}

.time-grid > section:nth-child(3),
.time-grid > section:nth-child(5) {
  grid-column: 1 / -1;
}

.active-timer {
  padding: 14px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(252, 241, 248, 0.92));
  border-radius: 16px;
  border: 1px solid rgba(219, 199, 230, 0.82);
  border-left: 4px solid #9b7bff;
}

.active-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.task-name {
  font-weight: 700;
  color: #2a2f4d;
  font-size: 1.05rem;
}

.task-meta {
  color: #7a6991;
  font-size: 0.85rem;
}

.active-desc {
  color: #6f5d88;
  margin-bottom: 10px;
}

.timer-display {
  font-family: 'Courier New', monospace;
  color: #1f2f57;
  text-align: center;
  padding: 16px;
  background-color: rgba(255, 255, 255, 0.88);
  border-radius: 14px;
  border: 1px solid rgba(219, 199, 230, 0.75);
}

.no-active {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 12px;
  border: 1px dashed rgba(220, 181, 214, 0.85);
  border-radius: 14px;
  color: #7a6991;
}

.no-active i {
  font-size: 1.2rem;
}

.no-title {
  font-weight: 700;
  color: #2a2f4d;
}

.no-sub {
  font-size: 0.9rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 18px 0;
}

.empty-state {
  text-align: center;
  color: #7f6a8e;
  padding: 14px 0;
}

.empty-state i {
  font-size: 1.4rem;
  margin-bottom: 6px;
  opacity: 0.85;
}

.pomodoro-time {
  font-size: 2.2rem;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  color: #273b63;
  text-align: center;
}

.pomodoro-sub {
  text-align: center;
  color: #7a6991;
  margin-top: 2px;
  margin-bottom: 12px;
}

.pomodoro-actions {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.entry-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.entry-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  border: 1px solid rgba(226, 209, 236, 0.82);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  padding: 10px;
}

.entry-title {
  font-weight: 700;
  color: #2a2f4d;
}

.entry-sub {
  color: #7a6991;
  font-size: 0.86rem;
  margin-top: 2px;
}

.entry-desc {
  color: #6f5d88;
  font-size: 0.9rem;
  margin-top: 6px;
}

.entry-actions {
  display: inline-flex;
  gap: 6px;
  flex-shrink: 0;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(216, 198, 229, 0.9);
  background: #ffffff;
  color: #5f4b84;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-btn.danger {
  color: #a33745;
  border-color: rgba(255, 189, 199, 0.95);
  background: rgba(255, 235, 238, 0.85);
}

.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(22, 30, 49, 0.38);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
  padding: 16px;
}

.modal-card {
  width: min(520px, 100%);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(219, 199, 230, 0.9);
  box-shadow: 0 18px 36px rgba(136, 110, 149, 0.22);
  padding: 16px;
}

@media (max-width: 992px) {
  .time-page {
    padding: 0 15px;
  }

  .time-grid {
    grid-template-columns: 1fr;
  }

  .time-grid > section:nth-child(3),
  .time-grid > section:nth-child(5) {
    grid-column: auto;
  }
}
</style>