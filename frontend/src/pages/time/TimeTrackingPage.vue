<template>
  <div class="time-page page-shell">
    <div class="page-content-surface">
      <div class="time-head">
        <div>
          <h2 class="page-title"><i class="fas fa-clock me-2"></i>{{ $t('time.title') }}</h2>
          <p class="section-subtitle">{{ $t('time.subtitle') }}</p>
        </div>
      </div>

      <div class="time-grid">
      <section class="card">
        <div class="card-header"><h5 class="mb-0">{{ $t('time.activeCard') }}</h5></div>
        <div class="card-body">
          <div v-if="activeTimeEntry" class="active-timer">
            <div class="active-top">
              <div class="active-title">
                <div class="task-name">{{ activeTimeEntry.task.title }}</div>
                <div class="task-meta">{{ formatDate(activeTimeEntry.start_time) }}</div>
              </div>
              <button class="btn btn-danger" @click="stopTimer">
                <i class="fas fa-stop me-1"></i> {{ $t('time.stop') }}
              </button>
            </div>
            <div v-if="activeTimeEntry.description" class="active-desc">{{ activeTimeEntry.description }}</div>
            <div class="timer-display">
              <span class="display-4">{{ formattedTime }}</span>
            </div>
            <div v-if="activeCountdownLabel" class="countdown-banner mt-2">
              <i class="fas fa-bell me-2"></i>
              {{ $t('time.countdownUntil') }} <strong>{{ activeCountdownLabel }}</strong>
            </div>
            <div class="limit-panel mt-3">
              <div class="form-label small text-muted mb-1">{{ $t('time.limitLabel') }}</div>
              <div class="d-flex flex-wrap gap-2 align-items-center">
                <input
                  v-model.number="limitMinutes"
                  type="number"
                  class="form-control form-control-sm limit-input"
                  min="0"
                  max="720"
                  :title="$t('time.minutesTitle')"
                >
                <button type="button" class="btn btn-sm btn-primary" @click="applyActiveLimit">{{ $t('time.setLimit') }}</button>
                <button
                  v-if="hasActiveLimit"
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  @click="clearActiveLimit"
                >
                  {{ $t('time.clearLimit') }}
                </button>
              </div>
              <div class="form-check form-check-inline mt-2 me-3">
                <input id="lim-sound" v-model="limitSound" class="form-check-input" type="checkbox">
                <label class="form-check-label small" for="lim-sound">{{ $t('time.sound') }}</label>
              </div>
              <div class="form-check form-check-inline mt-2">
                <input id="lim-autostop" v-model="limitAutoStop" class="form-check-input" type="checkbox">
                <label class="form-check-label small" for="lim-autostop">{{ $t('time.autoStopEnd') }}</label>
              </div>
              <button type="button" class="btn btn-link btn-sm p-0 mt-1" @click="playTimerPreview">
                {{ $t('time.testSound') }}
              </button>
            </div>
          </div>
          <div v-else class="no-active">
            <i class="fas fa-clock"></i>
            <div class="no-text">
              <div class="no-title">{{ $t('time.noActiveTitle') }}</div>
              <div class="no-sub">{{ $t('time.noActiveSub') }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header"><h5 class="mb-0">{{ $t('time.history') }}</h5></div>
        <div class="card-body">
          <div v-if="loading" class="loading-state">
            <div class="spinner-border" role="status"></div>
          </div>
          <div v-else-if="timeEntries.length === 0" class="empty-state">
            <i class="fas fa-history"></i>
            <p>{{ $t('time.historyEmpty') }}</p>
            <router-link to="/tasks" class="btn btn-outline-secondary btn-sm mt-2">{{ $t('time.openTasks') }}</router-link>
          </div>
          <div v-else class="entry-list">
            <article v-for="entry in timeEntries" :key="entry.id" class="entry-row">
              <div class="entry-main">
                <div class="entry-title">{{ entry.task.title }}</div>
                <div class="entry-sub">
                  {{ formatDateTime(entry.start_time) }} → {{ entry.end_time ? formatDateTime(entry.end_time) : $t('time.active') }}
                  · <strong>{{ formatDuration(entry.duration) }}</strong>
                </div>
                <div v-if="entry.description" class="entry-desc">{{ truncateText(entry.description, 80) }}</div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-header"><h5 class="mb-0">{{ $t('time.pomodoro') }}</h5></div>
        <div class="card-body">
          <div class="pomodoro">
            <div class="pomodoro-time">{{ pomodoroDisplay }}</div>
            <div class="pomodoro-sub">{{ pomodoroWorkMode ? $t('time.pomodoroFocus') : $t('time.pomodoroBreak') }}</div>
            <div class="pomodoro-actions">
              <button class="btn btn-outline-success" @click="startPomodoro" :disabled="pomodoroRunning">{{ $t('time.start') }}</button>
              <button class="btn btn-outline-warning" @click="pausePomodoro" :disabled="!pomodoroRunning">{{ $t('time.pause') }}</button>
              <button class="btn btn-outline-secondary" @click="resetPomodoro">{{ $t('time.reset') }}</button>
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
import { useI18n } from 'vue-i18n'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { useTaskTimerCountdown } from '@/composables/useTaskTimerCountdown'
import { useAppDateLocale } from '@/composables/useAppDateLocale'
import { playTimerExpirySound } from '@/utils/timerAlertSound'
import { format, parseISO } from 'date-fns'

export default {
  name: 'TimeTrackingPage',
  setup() {
    const { t } = useI18n()
    const dateLocale = useAppDateLocale()
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
        toast.error(t('time.loadHistoryError'))
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
        toast.success(t('time.timerStoppedLimit'))
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
        toast.error(t('time.loadTasksError'))
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
        toast.success(t('time.timerStopped'))
        await fetchTimeEntries()
      } catch (error) {
        toast.error(t('time.timerStopError'))
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
        toast.error(t('time.minutesNonNegative'))
        return
      }
      scheduleCountdown(entry.id, m, limitSound.value, limitAutoStop.value)
      if (m > 0) toast.info(t('time.limitSet'))
    }

    const clearActiveLimit = () => {
      clearStoredCountdown()
      toast.info(t('time.limitCleared'))
    }

    const playTimerPreview = () => {
      playTimerExpirySound()
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return format(parseISO(dateString), 'dd MMM yyyy', { locale: dateLocale.value })
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      return format(parseISO(dateString), 'dd MMM yyyy, HH:mm', { locale: dateLocale.value })
    }

    const formatDuration = (durationString) => {
      if (!durationString) return t('time.active')

      // Parse duration string (assuming format like "HH:MM:SS")
      const parts = durationString.split(':')
      if (parts.length === 3) {
        const hours = parseInt(parts[0], 10)
        const minutes = parseInt(parts[1], 10)
        const seconds = parseInt(parts[2], 10)

        if (hours > 0) {
          return t('time.durHM', { h: hours, m: minutes })
        }
        if (minutes > 0) {
          return t('time.durMS', { m: minutes, s: seconds })
        }
        return t('time.durS', { s: seconds })
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
        toast.info(pomodoroWorkMode.value ? t('time.pomodoroNewFocus') : t('time.pomodoroBreakTime'))
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