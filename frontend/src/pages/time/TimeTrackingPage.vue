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
            <div v-if="activeCountdownLabel" class="countdown-banner mt-2">
              <i class="fas fa-bell me-2"></i>
              До сигнала: <strong>{{ activeCountdownLabel }}</strong>
            </div>
            <div class="limit-panel mt-3">
              <div class="form-label small text-muted mb-1">Лимит и сигнал</div>
              <div class="d-flex flex-wrap gap-2 align-items-center">
                <input
                  v-model.number="limitMinutes"
                  type="number"
                  class="form-control form-control-sm limit-input"
                  min="0"
                  max="720"
                  title="Минуты до сигнала"
                >
                <button type="button" class="btn btn-sm btn-primary" @click="applyActiveLimit">Задать</button>
                <button
                  v-if="hasActiveLimit"
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  @click="clearActiveLimit"
                >
                  Сбросить лимит
                </button>
              </div>
              <div class="form-check form-check-inline mt-2 me-3">
                <input id="lim-sound" v-model="limitSound" class="form-check-input" type="checkbox">
                <label class="form-check-label small" for="lim-sound">Звук</label>
              </div>
              <div class="form-check form-check-inline mt-2">
                <input id="lim-autostop" v-model="limitAutoStop" class="form-check-input" type="checkbox">
                <label class="form-check-label small" for="lim-autostop">Стоп учёта в конце</label>
              </div>
              <button type="button" class="btn btn-link btn-sm p-0 mt-1" @click="playTimerPreview">
                Проверить звук
              </button>
            </div>
          </div>
          <div v-else class="no-active">
            <i class="fas fa-clock"></i>
            <div class="no-text">
              <div class="no-title">Нет активного таймера</div>
              <div class="no-sub">Запусти таймер из списка задач.</div>
            </div>
          </div>
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
            <router-link to="/tasks" class="btn btn-outline-secondary btn-sm mt-2">Открыть задачи</router-link>
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

      </div>
    </div>

  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { useTaskTimerCountdown } from '@/composables/useTaskTimerCountdown'
import { playTimerExpirySound } from '@/utils/timerAlertSound'
import { format, parseISO } from 'date-fns'
import { ru } from 'date-fns/locale'

export default {
  name: 'TimeTrackingPage',
  setup() {
    const toast = useToast()

    const timeEntries = ref([])
    const tasks = ref([])
    const loading = ref(false)

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

    const {
      tick,
      scheduleCountdown,
      clearStoredCountdown,
      remainingSecondsForEntry,
      formatCountdown,
      loadCountdown
    } = useTaskTimerCountdown(timeEntries, {
      stopEntry: async (entryId) => {
        await api.stopTimeEntry(entryId)
        toast.success('Таймер остановлен по лимиту')
        await fetchTimeEntries()
      }
    })

    const limitMinutes = ref(25)
    const limitSound = ref(true)
    const limitAutoStop = ref(false)

    const fetchTasks = async () => {
      try {
        const response = await api.getTasks()
        tasks.value = response.data.filter(task => task.is_active)
      } catch (error) {
        toast.error('Ошибка загрузки задач')
        console.error('Error fetching tasks:', error)
      }
    }

    const stopTimer = async () => {
      if (!activeTimeEntry.value) return

      try {
        const cfg = loadCountdown()
        if (cfg && cfg.entryId === activeTimeEntry.value.id) {
          clearStoredCountdown()
        }
        await api.stopTimeEntry(activeTimeEntry.value.id)
        toast.success('Таймер остановлен')
        await fetchTimeEntries()
      } catch (error) {
        toast.error('Ошибка остановки таймера')
        console.error('Error stopping timer:', error)
      }
    }

    const activeCountdownLabel = computed(() => {
      void tick.value
      const entry = activeTimeEntry.value
      if (!entry) return ''
      const sec = remainingSecondsForEntry(entry.id)
      if (sec == null) return ''
      return formatCountdown(sec)
    })

    const hasActiveLimit = computed(() => {
      void tick.value
      const entry = activeTimeEntry.value
      if (!entry) return false
      const cfg = loadCountdown()
      return !!(cfg && cfg.entryId === entry.id)
    })

    const applyActiveLimit = () => {
      const entry = activeTimeEntry.value
      if (!entry) return
      const m = Number(limitMinutes.value)
      if (!Number.isFinite(m) || m < 0) {
        toast.error('Укажите неотрицательное число минут')
        return
      }
      scheduleCountdown(entry.id, m, limitSound.value, limitAutoStop.value)
      if (m > 0) toast.info('Лимит установлен')
    }

    const clearActiveLimit = () => {
      clearStoredCountdown()
      toast.info('Лимит снят')
    }

    const playTimerPreview = () => {
      playTimerExpirySound()
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
        playTimerExpirySound()
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
      activeTimeEntry,
      formattedTime,
      activeCountdownLabel,
      hasActiveLimit,
      limitMinutes,
      limitSound,
      limitAutoStop,
      applyActiveLimit,
      clearActiveLimit,
      playTimerPreview,
      pomodoroDisplay,
      pomodoroRunning,
      pomodoroWorkMode,
      stopTimer,
      formatDate,
      formatDateTime,
      formatDuration,
      truncateText,
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
  grid-template-columns: 1fr;
  gap: 12px;
  align-items: start;
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

.countdown-banner {
  text-align: center;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 248, 230, 0.92);
  border: 1px solid rgba(220, 180, 90, 0.45);
  color: #6a4810;
  font-size: 0.95rem;
}

.limit-panel {
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.65);
  border: 1px dashed rgba(200, 180, 220, 0.75);
}

.limit-input {
  width: 88px;
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

.no-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
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

@media (max-width: 992px) {
  .time-page {
    padding: 0 15px;
  }

  .time-grid {
    grid-template-columns: 1fr;
  }
}
</style>