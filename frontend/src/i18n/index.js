import { createI18n } from 'vue-i18n'
import ru from './locales/ru.js'
import en from './locales/en.js'

function getInitialLocale() {
  if (typeof localStorage === 'undefined') return 'ru'
  const v = localStorage.getItem('locale')
  return v === 'en' ? 'en' : 'ru'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'ru',
  messages: { ru, en },
  globalInjection: true
})

export default i18n
