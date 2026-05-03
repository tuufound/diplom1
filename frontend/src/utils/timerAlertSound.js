/**
 * Короткий сигнал окончания таймера (Web Audio API, без внешних файлов).
 */
let sharedCtx = null

function getAudioContext() {
  const Ctx = window.AudioContext || window.webkitAudioContext
  if (!Ctx) return null
  if (!sharedCtx || sharedCtx.state === 'closed') {
    sharedCtx = new Ctx()
  }
  return sharedCtx
}

export function playTimerExpirySound() {
  try {
    const ctx = getAudioContext()
    if (!ctx) return
    const resume = () => (ctx.state === 'suspended' ? ctx.resume() : Promise.resolve())
    resume().then(() => {
      const beep = (when, freq, dur = 0.18, vol = 0.11) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.frequency.value = freq
        osc.type = 'sine'
        const t0 = ctx.currentTime + when
        gain.gain.setValueAtTime(vol, t0)
        gain.gain.exponentialRampToValueAtTime(0.008, t0 + dur)
        osc.start(t0)
        osc.stop(t0 + dur)
      }
      beep(0, 880)
      beep(0.22, 660)
      beep(0.44, 880)
    })
  } catch (e) {
    console.warn('timer sound', e)
  }
}
