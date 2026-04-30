<template>
  <div class="time-tracking-container page-shell">
    <h2 class="mb-2 page-title">
      <i class="fas fa-clock me-2"></i>Отслеживание времени
    </h2>
    <p class="section-subtitle mb-4">Сфокусированный режим: учет времени + Pomodoro в одном месте.</p>

    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Активный таймер</h5>
          </div>
          <div class="card-body">
            <div v-if="activeTimeEntry" class="active-timer">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>{{ activeTimeEntry.task.title }}</h4>
                <button class="btn btn-danger" @click="stopTimer">
                  <i class="fas fa-stop me-1"></i> Остановить
                </button>
              </div>
              <p class="text-muted mb-3">{{ activeTimeEntry.description }}</p>
              <div class="timer-display">
                <span class="display-4">{{ formattedTime }}</span>
              </div>
              <div class="mt-3">
                <span class="badge bg-info me-2">
                  <i class="fas fa-calendar me-1"></i>
                  {{ formatDate(activeTimeEntry.start_time) }}
                </span>
              </div>
            </div>
            <div v-else class="no-active-timer text-center py-5">
              <i class="fas fa-clock fa-3x text-muted mb-3"></i>
              <h4>Нет активного таймера</h4>
              <p class="text-muted">Выберите задачу для начала отслеживания времени</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">История времени</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>

            <div v-else>
              <div v-if="timeEntries.length === 0" class="text-center py-5">
                <i class="fas fa-history fa-3x text-muted mb-3"></i>
                <h4>История пуста</h4>
                <p class="text-muted">Начните отслеживать время для задач</p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Задача</th>
                      <th>Начало</th>
                      <th>Конец</th>
                      <th>Длительность</th>
                      <th>Описание</th>
                      <th>Действия</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="entry in timeEntries" :key="entry.id">
                      <td>{{ entry.task.title }}</td>
                      <td>{{ formatDateTime(entry.start_time) }}</td>
                      <td>{{ entry.end_time ? formatDateTime(entry.end_time) : 'Активно' }}</td>
                      <td>{{ formatDuration(entry.duration) }}</td>
                      <td>{{ truncateText(entry.description, 30) }}</td>
                      <td>
                        <div class="d-flex gap-2">
                          <button class="btn btn-sm btn-outline-primary" @click="editTimeEntry(entry)">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-danger" @click="deleteTimeEntry(entry.id)">
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Запустить новый таймер</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="startNewTimer">
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
                  placeholder="Чем вы занимаетесь?"
                ></textarea>
              </div>

              <button type="submit" class="btn btn-primary w-100" :disabled="startingTimer">
                <span v-if="startingTimer" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <span>Запустить таймер</span>
              </button>
            </form>
          </div>
        </div>
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">Ручной ввод времени</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveManualEntry">
              <div class="mb-3">
                <label class="form-label" for="manualTask">Задача</label>
                <select id="manualTask" class="form-select" v-model="manualEntry.task" required>
                  <option value="">Выберите задачу</option>
                  <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.title }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label" for="manualStart">Начало</label>
                <input id="manualStart" type="datetime-local" class="form-control" v-model="manualEntry.start_time" required>
              </div>
              <div class="mb-3">
                <label class="form-label" for="manualEnd">Конец</label>
                <input id="manualEnd" type="datetime-local" class="form-control" v-model="manualEntry.end_time" required>
              </div>
              <div class="mb-3">
                <label class="form-label" for="manualDescription">Описание</label>
                <textarea id="manualDescription" class="form-control" rows="2" v-model="manualEntry.description"></textarea>
              </div>
              <button type="submit" class="btn btn-secondary w-100" :disabled="savingManual">
                <span v-if="savingManual" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Сохранить вручную
              </button>
            </form>
          </div>
        </div>
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">Pomodoro режим</h5>
          </div>
          <div class="card-body text-center">
            <div class="pomodoro-time mb-3">{{ pomodoroDisplay }}</div>
            <div class="btn-group w-100 mb-2">
              <button class="btn btn-outline-success" @click="startPomodoro" :disabled="pomodoroRunning">Старт</button>
              <button class="btn btn-outline-warning" @click="pausePomodoro" :disabled="!pomodoroRunning">Пауза</button>
              <button class="btn btn-outline-secondary" @click="resetPomodoro">Сброс</button>
            </div>
            <small class="text-muted">
              {{ pomodoroWorkMode ? 'Фокус 25 минут' : 'Перерыв 5 минут' }}
            </small>
          </div>
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

    const editTimeEntry = async (entry) => {
      const newDescription = prompt('Изменить описание записи:', entry.description || '')
      if (newDescription === null) return
      try {
        await api.updateTimeEntry(entry.id, {
          task: entry.task.id,
          start_time: entry.start_time,
          end_time: entry.end_time,
          description: newDescription
        })
        toast.success('Запись обновлена')
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка обновления записи')
      }
    }

    const deleteTimeEntry = async (id) => {
      if (confirm('Вы уверены, что хотите удалить эту запись времени?')) {
        try {
          await api.deleteTimeEntry(id)
          toast.success('Запись времени удалена')
          await fetchTimeEntries()
        } catch (error) {
          toast.error('Ошибка удаления записи времени')
          console.error('Error deleting time entry:', error)
        }
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
      startNewTimer,
      stopTimer,
      editTimeEntry,
      deleteTimeEntry,
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
.time-tracking-container {
  max-width: 1400px;
  margin: 0 auto;
}

.active-timer {
  padding: 20px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(236, 244, 255, 0.9) 100%);
  border-radius: 14px;
  border-left: 4px solid #7282ff;
  border: 1px solid rgba(193, 208, 234, 0.8);
}

.timer-display {
  font-family: 'Courier New', monospace;
  color: #1a2944;
  text-align: center;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(40, 68, 132, 0.08);
  border: 1px solid rgba(198, 211, 236, 0.85);
}

.no-active-timer {
  color: #6c757d;
}

.table-responsive {
  overflow-x: auto;
}

.table {
  margin-bottom: 0;
}

.table th {
  background-color: rgba(245, 249, 255, 0.85);
  border-bottom: 2px solid #d9e4f6;
}

.btn-danger {
  background-color: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
}

.pomodoro-time {
  font-size: 2.2rem;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  color: #273b63;
}

@media (max-width: 992px) {
  .time-tracking-container {
    padding: 0 15px;
  }
}
</style>