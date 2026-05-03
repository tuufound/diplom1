const KEY = 'taskPlannerCountdown'

export function loadCountdown() {
  try {
    const raw = sessionStorage.getItem(KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    if (
      !data ||
      typeof data.entryId !== 'number' ||
      typeof data.endAt !== 'number'
    ) {
      return null
    }
    return {
      entryId: data.entryId,
      endAt: data.endAt,
      sound: data.sound !== false,
      autoStop: !!data.autoStop
    }
  } catch {
    return null
  }
}

export function saveCountdown(payload) {
  sessionStorage.setItem(KEY, JSON.stringify(payload))
}

export function clearCountdown() {
  sessionStorage.removeItem(KEY)
}
