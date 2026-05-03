import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { loadCountdown, saveCountdown, clearCountdown } from '@/utils/taskCountdownStorage'
import { playTimerExpirySound } from '@/utils/timerAlertSound'

/**
 * Обратный отсчёт для активной записи времени + сигнал по окончании.
 * @param {import('vue').Ref} timeEntriesRef
 * @param {{ stopEntry: (entryId: number) => Promise<void> }} options
 */
export function useTaskTimerCountdown(timeEntriesRef, options = {}) {
  const toast = useToast()
  const { stopEntry } = options
  const tick = ref(0)
  let intervalId = null
  let expiryHandled = false

  const bump = () => {
    tick.value = Date.now()
  }

  const checkExpiry = () => {
    const cfg = loadCountdown()
    if (!cfg) {
      expiryHandled = false
      return
    }
    const active = timeEntriesRef.value.filter((e) => !e.end_time)
    const entry = active.find((e) => e.id === cfg.entryId)
    if (!entry) {
      clearCountdown()
      expiryHandled = false
      return
    }
    if (Date.now() < cfg.endAt) return
    if (expiryHandled) return
    expiryHandled = true
    if (cfg.sound) playTimerExpirySound()
    toast.warning('Время таймера по задаче истекло')
    clearCountdown()
    if (cfg.autoStop && typeof stopEntry === 'function') {
      stopEntry(cfg.entryId).finally(() => {
        expiryHandled = false
      })
    } else {
      expiryHandled = false
    }
  }

  const scheduleCountdown = (entryId, minutes, sound = true, autoStop = false) => {
    if (!minutes || minutes <= 0) {
      clearCountdown()
      return
    }
    const endAt = Date.now() + Math.round(minutes * 60 * 1000)
    saveCountdown({ entryId, endAt, sound, autoStop })
    expiryHandled = false
    bump()
  }

  const clearStoredCountdown = () => {
    clearCountdown()
    expiryHandled = false
    bump()
  }

  const remainingSecondsForEntry = (entryId) => {
    const cfg = loadCountdown()
    if (!cfg || cfg.entryId !== entryId) return null
    return Math.max(0, Math.ceil((cfg.endAt - tick.value) / 1000))
  }

  const formatCountdown = (totalSec) => {
    if (totalSec == null) return ''
    const m = Math.floor(totalSec / 60)
    const s = totalSec % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }

  onMounted(() => {
    bump()
    intervalId = setInterval(() => {
      bump()
      checkExpiry()
    }, 1000)
  })

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId)
  })

  return {
    tick,
    scheduleCountdown,
    clearStoredCountdown,
    remainingSecondsForEntry,
    formatCountdown,
    loadCountdown
  }
}
