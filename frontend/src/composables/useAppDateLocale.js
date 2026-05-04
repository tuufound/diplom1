import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { enUS, ru } from 'date-fns/locale'

/**
 * date-fns locale matching current UI language.
 */
export function useAppDateLocale() {
  const { locale } = useI18n()
  return computed(() => (locale.value === 'en' ? enUS : ru))
}
