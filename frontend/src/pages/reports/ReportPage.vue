<template>
  <div class="reports-container page-shell">
    <div class="page-content-surface">
    <div class="page-head">
      <div>
        <h2 class="page-title"><i class="fas fa-chart-pie me-2"></i>{{ $t('reports.title') }}</h2>
        <p class="section-subtitle">{{ $t('reports.subtitle') }}</p>
      </div>
      <div class="head-actions">
        <button class="btn btn-outline-success" @click="exportCsv"><i class="fas fa-file-csv me-1"></i>{{ $t('reports.csv') }}</button>
        <button class="btn btn-outline-danger" @click="exportPdf"><i class="fas fa-file-pdf me-1"></i>{{ $t('reports.pdf') }}</button>
      </div>
    </div>

    <section class="card controls-card mb-4">
      <div class="card-body">
        <div class="period-tabs">
          <button v-for="option in periodOptions" :key="option.value" class="period-tab" :class="{ active: dateRange === option.value }" @click="setPresetRange(option.value)">
            {{ option.label }}
          </button>
        </div>
        <div v-if="dateRange === 'custom'" class="custom-range">
          <div>
            <label class="form-label">{{ $t('reports.start') }}</label>
            <input v-model="startDate" type="date" class="form-control">
          </div>
          <div>
            <label class="form-label">{{ $t('reports.end') }}</label>
            <input v-model="endDate" type="date" class="form-control">
          </div>
          <button class="btn btn-primary align-self-end" @click="applyFilters">{{ $t('reports.apply') }}</button>
        </div>
      </div>
    </section>

    <section v-if="loading" class="card loading-card mb-4">
      <div class="card-body">
        <div class="skeleton"></div>
        <div class="skeleton short"></div>
      </div>
    </section>

    <section class="metrics-grid mb-4">
      <article class="metric-card">
        <span>{{ $t('reports.totalTasks') }}</span>
        <strong>{{ report.total_tasks || 0 }}</strong>
      </article>
      <article class="metric-card">
        <span>{{ $t('reports.closed') }}</span>
        <strong>{{ report.completed_tasks || 0 }}</strong>
      </article>
      <article class="metric-card">
        <span>{{ $t('reports.timeSpent') }}</span>
        <strong>{{ formatSeconds(report.total_tracked_seconds || 0) }}</strong>
      </article>
      <article class="metric-card">
        <span>{{ $t('reports.avgTime') }}</span>
        <strong>{{ avgCompletionLabel }}</strong>
      </article>
    </section>

    <section class="content-grid mb-4">
      <div class="card report-card">
        <div class="card-header"><h5 class="mb-0">{{ $t('reports.statusTitle') }}</h5></div>
        <div class="card-body">
          <div class="status-list">
            <article v-for="item in statusSummary" :key="item.key" class="status-row">
              <div class="status-row-head">
                <span class="status-name">{{ item.label }}</span>
                <span class="status-count">{{ item.count }} · {{ item.percent }}%</span>
              </div>
              <div class="status-track">
                <div class="status-fill" :class="`status-${item.key}`" :style="{ width: `${item.percent}%` }"></div>
              </div>
            </article>
          </div>
        </div>
      </div>

      <div class="card report-card">
        <div class="card-header"><h5 class="mb-0">{{ $t('reports.topTasks') }}</h5></div>
        <div class="card-body">
          <div v-if="topTimeTasks.length === 0" class="empty-state">{{ $t('reports.noTimeData') }}</div>
          <div v-else class="top-list">
            <article v-for="item in topTimeTasks" :key="item.task_id" class="top-row">
              <div class="top-title">{{ item.task_title }}</div>
              <div class="top-time">{{ formatSeconds(item.seconds) }}</div>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section class="card report-card">
      <div class="card-header"><h5 class="mb-0">{{ $t('reports.tasksPeriod') }}</h5></div>
      <div class="card-body">
        <div v-if="filteredTasks.length === 0" class="empty-state">{{ $t('reports.noTasksPeriod') }}</div>
        <div v-else class="task-grid">
          <article v-for="task in filteredTasks" :key="task.id" class="task-card">
            <div class="task-head">
              <h6>{{ task.title }}</h6>
              <span class="status-pill" :class="statusPillClass(task.status)">{{ getStatusText(task.status) }}</span>
            </div>
            <div class="task-meta">
              <span v-if="task.priority" class="meta-pill">{{ task.priority.name }}</span>
              <span v-if="task.category" class="meta-pill">{{ task.category.name }}</span>
              <span class="meta-pill">{{ getTaskTime(task) }}</span>
            </div>
            <div class="task-progress">
              <div class="task-progress-fill" :class="statusBarClass(task.status)" :style="{ width: progressWidth(task.status) }"></div>
            </div>
          </article>
        </div>
      </div>
    </section>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { format, subDays, subMonths, subQuarters, subYears, parseISO, startOfDay } from 'date-fns'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

export default {
  name: 'ReportPage',
  setup() {
    const { t, locale } = useI18n()
    const toast = useToast()
    const tasks = ref([])
    const timeEntries = ref([])
    const report = ref({})
    const loading = ref(false)
    const dateRange = ref('week')
    const startDate = ref('')
    const endDate = ref('')

    const periodOptions = computed(() => {
      void locale.value
      return [
      { value: 'day', label: t('reports.periodDay') },
      { value: 'week', label: t('reports.periodWeek') },
      { value: 'month', label: t('reports.periodMonth') },
      { value: 'quarter', label: t('reports.periodQuarter') },
      { value: 'year', label: t('reports.periodYear') },
      { value: 'custom', label: t('reports.periodCustom') }
    ]
    })

    const fetchData = async () => {
      try {
        loading.value = true
        const [tasksResponse, timeEntriesResponse, reportResponse] = await Promise.all([
          api.getTasks(),
          api.getTimeEntries(),
          api.getReports({
            start_date: startDate.value || undefined,
            end_date: endDate.value || undefined
          })
        ])
        tasks.value = tasksResponse.data
        timeEntries.value = timeEntriesResponse.data
        report.value = reportResponse.data
      } catch (error) {
        toast.error(t('reports.loadError'))
      } finally {
        loading.value = false
      }
    }

    const filteredTasks = computed(() => {
      const start = startDate.value ? parseISO(`${startDate.value}T00:00:00`) : null
      const end = endDate.value ? parseISO(`${endDate.value}T23:59:59`) : null
      return tasks.value.filter(task => {
        if (!start || !end) return true
        const createdAt = parseISO(task.created_at)
        return createdAt >= start && createdAt <= end
      })
    })

    const topTimeTasks = computed(() => (report.value?.top_time_tasks || []).slice(0, 6))

    const statusSummary = computed(() => {
      void locale.value
      const counts = { todo: 0, in_progress: 0, done: 0, archived: 0 }
      filteredTasks.value.forEach(task => {
        if (counts[task.status] !== undefined) counts[task.status] += 1
      })
      const total = filteredTasks.value.length || 1
      return [
        { key: 'todo', label: t('taskStatus.todo') },
        { key: 'in_progress', label: t('taskStatus.in_progress') },
        { key: 'done', label: t('taskStatus.done') },
        { key: 'archived', label: t('taskStatus.archived') }
      ].map(item => ({
        ...item,
        count: counts[item.key],
        percent: Math.round((counts[item.key] / total) * 100)
      }))
    })

    const avgCompletionLabel = computed(() => {
      void locale.value
      const v = report.value?.avg_completion_seconds
      if (v == null) return t('common.noData')
      return formatSeconds(v)
    })

    const getStatusText = (status) =>
      ['todo', 'in_progress', 'done', 'archived'].includes(status)
        ? t(`taskStatus.${status}`)
        : status

    const statusPillClass = (status) => `pill-${status || 'todo'}`
    const statusBarClass = (status) => `fill-${status || 'todo'}`

    const progressWidth = (status) => {
      const map = { todo: '25%', in_progress: '70%', done: '100%', archived: '100%' }
      return map[status] || '25%'
    }

    const getTaskTime = (task) => {
      const related = timeEntries.value.filter(entry => entry.task.id === task.id && entry.duration)
      const total = related.reduce((sum, entry) => {
        const parts = String(entry.duration).split(':')
        if (parts.length !== 3) return sum
        return sum + Number(parts[0]) * 3600 + Number(parts[1]) * 60 + Number(parts[2])
      }, 0)
      return formatSeconds(total)
    }

    const formatSeconds = (seconds) => {
      const safeSeconds = Math.max(0, Number(seconds) || 0)
      const h = Math.floor(safeSeconds / 3600)
      const m = Math.floor((safeSeconds % 3600) / 60)
      if (h > 0) return t('reports.fmtHm', { h, m })
      if (m > 0) return t('reports.fmtM', { m })
      if (safeSeconds > 0) return t('reports.fmtS', { s: safeSeconds })
      return t('common.zeroMin')
    }

    const setDateRange = () => {
      const now = new Date()
      let start
      switch (dateRange.value) {
        case 'day':
          start = startOfDay(now)
          break
        case 'week':
          start = subDays(now, 7)
          break
        case 'month':
          start = subMonths(now, 1)
          break
        case 'quarter':
          start = subQuarters(now, 1)
          break
        case 'year':
          start = subYears(now, 1)
          break
        default:
          return
      }
      startDate.value = format(start, 'yyyy-MM-dd')
      endDate.value = format(now, 'yyyy-MM-dd')
    }

    const setPresetRange = (preset) => {
      dateRange.value = preset
    }

    const applyFilters = () => fetchData()

    const getRowsForExport = () => filteredTasks.value.map(task => ([
      task.title,
      getStatusText(task.status),
      task.priority?.name || '-',
      task.category?.name || '-',
      getTaskTime(task)
    ]))

    const exportCsv = () => {
      const header = [
        t('reports.exportTask'),
        t('reports.exportStatus'),
        t('reports.exportPriority'),
        t('reports.exportCategory'),
        t('reports.exportTime')
      ]
      const csv = [header, ...getRowsForExport()]
        .map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(','))
        .join('\n')
      const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `report-${startDate.value || 'all'}-${endDate.value || 'all'}.csv`
      link.click()
      URL.revokeObjectURL(url)
    }

    const exportPdf = () => {
      const doc = new jsPDF()
      doc.setFontSize(14)
      doc.text(t('reports.pdfTitle'), 14, 16)
      autoTable(doc, {
        startY: 24,
        head: [
          [
            t('reports.exportTask'),
            t('reports.exportStatus'),
            t('reports.exportPriority'),
            t('reports.exportCategory'),
            t('reports.exportTime')
          ]
        ],
        body: getRowsForExport(),
        styles: { fontSize: 9 }
      })
      doc.save(`report-${startDate.value || 'all'}-${endDate.value || 'all'}.pdf`)
    }

    watch(dateRange, () => {
      if (dateRange.value !== 'custom') {
        setDateRange()
        fetchData()
      }
    })

    onMounted(() => {
      setDateRange()
      fetchData()
    })

    return {
      loading,
      report,
      filteredTasks,
      topTimeTasks,
      statusSummary,
      dateRange,
      startDate,
      endDate,
      periodOptions,
      avgCompletionLabel,
      setPresetRange,
      applyFilters,
      exportCsv,
      exportPdf,
      getStatusText,
      statusPillClass,
      statusBarClass,
      progressWidth,
      getTaskTime,
      formatSeconds
    }
  }
}
</script>

<style scoped>
.reports-container {
  max-width: 1260px;
  margin: 0 auto;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.head-actions {
  display: inline-flex;
  gap: 8px;
}

.controls-card,
.report-card,
.metric-card {
  border: 1px solid rgba(224, 206, 232, 0.84);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 24px rgba(136, 110, 149, 0.14);
}

.period-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.period-tab {
  border: 1px solid rgba(216, 196, 226, 0.8);
  background: #fff;
  border-radius: 999px;
  color: #65567d;
  padding: 7px 12px;
  font-size: 0.83rem;
}

.period-tab.active {
  background: linear-gradient(135deg, #f6e8f5, #f1e2f7);
  color: #3a4c78;
  border-color: rgba(194, 170, 211, 0.9);
}

.custom-range {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
}

.loading-card .card-body {
  padding: 16px;
}

.skeleton {
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, #ebe3f2, #f7f2fa, #ebe3f2);
  background-size: 220% 100%;
  animation: shimmer 1.1s linear infinite;
}

.skeleton.short {
  margin-top: 8px;
  width: 65%;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  padding: 12px 14px;
}

.metric-card span {
  display: block;
  color: #7a6991;
  font-size: 0.82rem;
}

.metric-card strong {
  color: #2f3f6d;
  font-size: 1.3rem;
  line-height: 1.1;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 12px;
}

.report-card .card-header {
  background: linear-gradient(180deg, rgba(251, 246, 252, 0.95), rgba(247, 238, 250, 0.9));
  border-bottom: 1px solid rgba(224, 208, 233, 0.85);
  color: #2f3e68;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-row-head {
  display: flex;
  justify-content: space-between;
  color: #5f4d83;
  margin-bottom: 6px;
  font-size: 0.86rem;
}

.status-track {
  height: 8px;
  border-radius: 999px;
  background: #eee8f3;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  border-radius: inherit;
}

.status-todo { background: linear-gradient(90deg, #8d98a9, #7d899a); }
.status-in_progress { background: linear-gradient(90deg, #4f89f0, #2f74e3); }
.status-done { background: linear-gradient(90deg, #47bf86, #2f9f6a); }
.status-archived { background: linear-gradient(90deg, #7b8493, #636d7c); }

.top-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(245, 238, 250, 0.8);
}

.top-title {
  color: #3c4c76;
}

.top-time {
  color: #66557f;
  font-weight: 600;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.task-card {
  border: 1px solid rgba(224, 209, 233, 0.88);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.94);
  padding: 10px;
}

.task-head {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.task-head h6 {
  margin: 0;
  font-size: 0.9rem;
  color: #34466d;
}

.status-pill,
.meta-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 0.74rem;
  font-weight: 600;
}

.pill-todo { background: #ece9f2; color: #5f6676; }
.pill-in_progress { background: #e5efff; color: #3657a4; }
.pill-done { background: #e8f8ef; color: #2f7b59; }
.pill-archived { background: #f1ecf5; color: #66577d; }

.task-meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-pill {
  background: #f3edf8;
  color: #685a83;
}

.task-progress {
  margin-top: 10px;
  height: 8px;
  border-radius: 999px;
  background: #ebeef3;
  overflow: hidden;
}

.task-progress-fill {
  height: 100%;
  border-radius: inherit;
}

.fill-todo { background: linear-gradient(90deg, #8d98a9, #7d899a); }
.fill-in_progress { background: linear-gradient(90deg, #4f89f0, #2f74e3); }
.fill-done { background: linear-gradient(90deg, #47bf86, #2f9f6a); }
.fill-archived { background: linear-gradient(90deg, #7b8493, #636d7c); }

.empty-state {
  color: #7f6a8e;
  text-align: center;
  padding: 14px 0;
}

@keyframes shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

@media (max-width: 992px) {
  .page-head {
    flex-direction: column;
  }

  .metrics-grid,
  .content-grid,
  .task-grid,
  .custom-range {
    grid-template-columns: 1fr;
  }
}
</style>