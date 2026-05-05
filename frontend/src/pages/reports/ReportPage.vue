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

    <section class="charts-grid mb-4">
      <div class="card report-card">
        <div class="card-header"><h5 class="mb-0">{{ $t('reports.statusTitle') }}</h5></div>
        <div class="card-body chart-body">
          <div v-if="filteredTasks.length === 0" class="empty-state">{{ $t('reports.noTasksPeriod') }}</div>
          <div v-else class="donut-wrap">
            <Doughnut :data="statusChartData" :options="statusChartOptions" />
          </div>
        </div>
      </div>

      <div class="card report-card">
        <div class="card-header"><h5 class="mb-0">{{ $t('reports.timeByProject') }}</h5></div>
        <div class="card-body chart-body">
          <div v-if="timeByProjectData.labels.length === 0" class="empty-state">{{ $t('reports.noTimeData') }}</div>
          <div v-else class="bar-wrap">
            <Bar :data="timeByProjectData" :options="timeByProjectOptions" />
          </div>
        </div>
      </div>
    </section>

    <section v-if="projectStats.length > 0" class="card report-card mb-4">
      <div class="card-header"><h5 class="mb-0">{{ $t('reports.projectsStats') }}</h5></div>
      <div class="card-body">
        <div class="projects-stats-grid">
          <article v-for="ps in projectStats" :key="ps.name" class="project-stat-card">
            <div class="ps-header">
              <h6 class="ps-name">{{ ps.name }}</h6>
              <span class="ps-total-badge">{{ ps.total }}</span>
            </div>
            <div class="ps-bar">
              <div class="ps-bar-fill ps-done" :style="{ width: `${ps.total ? Math.round(ps.done / ps.total * 100) : 0}%` }"></div>
              <div class="ps-bar-fill ps-progress" :style="{ width: `${ps.total ? Math.round(ps.inProgress / ps.total * 100) : 0}%` }"></div>
            </div>
            <div class="ps-meta">
              <span class="ps-stat"><i class="fas fa-check-circle me-1"></i>{{ ps.done }}</span>
              <span class="ps-stat"><i class="fas fa-spinner me-1"></i>{{ ps.inProgress }}</span>
              <span class="ps-stat"><i class="fas fa-clock me-1"></i>{{ ps.todo }}</span>
            </div>
          </article>
        </div>
      </div>
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
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { format, subDays, subMonths, subQuarters, subYears, parseISO, startOfDay } from 'date-fns'
import jsPDF from 'jspdf'
import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale, BarElement)

export default {
  name: 'ReportPage',
  components: { Doughnut, Bar },
  setup() {
    const { t, locale } = useI18n()
    const toast = useToast()
    const tasks = ref([])
    const projects = ref([])
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
        const [tasksResponse, projectsResponse, timeEntriesResponse, reportResponse] = await Promise.all([
          api.getTasks(),
          api.getProjects(),
          api.getTimeEntries(),
          api.getReports({
            start_date: startDate.value || undefined,
            end_date: endDate.value || undefined
          })
        ])
        tasks.value = Array.isArray(tasksResponse.data) ? tasksResponse.data : []
        projects.value = Array.isArray(projectsResponse.data) ? projectsResponse.data : []
        timeEntries.value = Array.isArray(timeEntriesResponse.data) ? timeEntriesResponse.data : []
        const rep = reportResponse.data
        report.value = rep && typeof rep === 'object' && !Array.isArray(rep) ? rep : {}
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

    const formatSeconds = (seconds) => {
      const safeSeconds = Math.max(0, Number(seconds) || 0)
      const h = Math.floor(safeSeconds / 3600)
      const m = Math.floor((safeSeconds % 3600) / 60)
      if (h > 0) return t('reports.fmtHm', { h, m })
      if (m > 0) return t('reports.fmtM', { m })
      if (safeSeconds > 0) return t('reports.fmtS', { s: safeSeconds })
      return t('common.zeroMin')
    }

    const avgCompletionLabel = computed(() => {
      void locale.value
      const v = report.value?.avg_completion_seconds
      if (v == null) return t('common.noData')
      return formatSeconds(v)
    })

    // --- Charts ---
    const statusChartData = computed(() => {
      void locale.value
      const summary = statusSummary.value
      return {
        labels: summary.map(s => s.label),
        datasets: [{
          data: summary.map(s => s.count),
          backgroundColor: ['#c4d7f2', '#b0a1d8', '#a5ddc4', '#d0c0da'],
          borderColor: ['#8faad4', '#9080b8', '#82c8a4', '#b0a0c0'],
          borderWidth: 1.5,
          hoverOffset: 6
        }]
      }
    })

    const statusChartOptions = computed(() => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { font: { size: 12 }, color: '#5f4d83', padding: 14 }
        },
        tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.parsed} задач` } }
      },
      cutout: '62%'
    }))

    const timeByProjectData = computed(() => {
      void locale.value
      const projectMap = {}
      for (const entry of timeEntries.value) {
        const tid = typeof entry.task === 'object' && entry.task ? entry.task.id : entry.task
        const task = tasks.value.find(t => t.id === tid)
        const pid = task?.project?.id ?? 'personal'
        const pname = task?.project?.name ?? t('tasksList.personal')
        const secs = parseDuration(entry.duration)
        if (!projectMap[pid]) projectMap[pid] = { name: pname, seconds: 0 }
        projectMap[pid].seconds += secs
      }
      const entries = Object.values(projectMap).sort((a, b) => b.seconds - a.seconds).slice(0, 8)
      return {
        labels: entries.map(e => e.name),
        datasets: [{
          label: t('reports.timeSpent'),
          data: entries.map(e => +(e.seconds / 3600).toFixed(2)),
          backgroundColor: 'rgba(155, 123, 255, 0.45)',
          borderColor: 'rgba(155, 123, 255, 0.85)',
          borderWidth: 1.5,
          borderRadius: 8,
          hoverBackgroundColor: 'rgba(155, 123, 255, 0.7)'
        }]
      }
    })

    const timeByProjectOptions = computed(() => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y.toFixed(1)}ч`
          }
        }
      },
      scales: {
        x: { ticks: { color: '#65567d', font: { size: 11 } }, grid: { display: false } },
        y: {
          ticks: { color: '#65567d', font: { size: 11 }, callback: v => `${v}ч` },
          grid: { color: 'rgba(224, 206, 232, 0.4)' },
          beginAtZero: true
        }
      }
    }))

    const parseDuration = (d) => {
      if (!d) return 0
      const parts = String(d).split(':')
      if (parts.length !== 3) return 0
      return Number(parts[0]) * 3600 + Number(parts[1]) * 60 + Number(parts[2])
    }

    // --- Project stats ---
    const projectStats = computed(() => {
      const map = {}
      for (const task of filteredTasks.value) {
        const pid = task.project?.id ?? 'none'
        const pname = task.project?.name ?? t('reports.noProject')
        if (!map[pid]) map[pid] = { name: pname, total: 0, done: 0, inProgress: 0, todo: 0 }
        map[pid].total++
        if (task.status === 'done') map[pid].done++
        else if (task.status === 'in_progress') map[pid].inProgress++
        else if (task.status === 'todo') map[pid].todo++
      }
      return Object.values(map).sort((a, b) => b.total - a.total)
    })

    const getTaskTime = (task) => {
      const tid = task?.id
      if (tid == null) return formatSeconds(0)
      const related = timeEntries.value.filter((entry) => {
        const et = entry?.task
        const eid = typeof et === 'object' && et != null ? et.id : et
        return eid === tid && entry.duration
      })
      const total = related.reduce((sum, entry) => {
        const parts = String(entry.duration).split(':')
        if (parts.length !== 3) return sum
        return sum + Number(parts[0]) * 3600 + Number(parts[1]) * 60 + Number(parts[2])
      }, 0)
      return formatSeconds(total)
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

    const getRowsForExport = () =>
      filteredTasks.value.map((task) => [
        task.title,
        getStatusText(task.status),
        task.priority?.name || '—',
        task.category?.name || '—',
        getTaskTime(task)
      ])

    const escapeHtmlForPdf = (str) =>
      String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')

    /** Временный DOM для html2canvas: инлайн-стили, без scoped Vue — стабильнее снимок и кириллица */
    const buildPdfExportHost = () => {
      void locale.value
      const thStyle =
        'background:#2563eb;color:#fff;font-weight:600;padding:10px 12px;text-align:left;font-size:11px;'
      const tdBase =
        'padding:9px 12px;border-bottom:1px solid #e2e8f0;vertical-align:top;word-break:break-word;'
      const title = escapeHtmlForPdf(t('reports.pdfTitle'))
      const period = escapeHtmlForPdf(
        `${t('reports.start')}: ${startDate.value || '—'} · ${t('reports.end')}: ${endDate.value || '—'}`
      )
      const columns = [
        t('reports.exportTask'),
        t('reports.exportStatus'),
        t('reports.exportPriority'),
        t('reports.exportCategory'),
        t('reports.exportTime')
      ]
      const thead = `<tr>${columns.map((c) => `<th style="${thStyle}">${escapeHtmlForPdf(c)}</th>`).join('')}</tr>`
      const rows = getRowsForExport()
      let tbody
      if (!rows.length) {
        tbody = `<tr><td colspan="5" style="${tdBase}">${escapeHtmlForPdf(t('reports.noTasksPeriod'))}</td></tr>`
      } else {
        tbody = rows
          .map(
            (row, ri) =>
              `<tr>${row
                .map((cell) => {
                  const bg = ri % 2 === 1 ? 'background:#f8fafc;' : ''
                  return `<td style="${tdBase}${bg}">${escapeHtmlForPdf(String(cell))}</td>`
                })
                .join('')}</tr>`
          )
          .join('')
      }
      const wrap = document.createElement('div')
      wrap.setAttribute('data-report-pdf-export', '1')
      wrap.style.cssText = [
        'box-sizing:border-box',
        'width:720px',
        'padding:28px 32px 36px',
        'background:#ffffff',
        'color:#0f172a',
        'font:13px/1.5 system-ui,Segoe UI,Roboto,Helvetica Neue,Arial,sans-serif',
        'text-align:left'
      ].join(';')
      wrap.innerHTML = `
    <div style="margin-bottom:18px">
      <h1 style="margin:0 0 8px;font-size:22px;font-weight:700;color:#0f172a">${title}</h1>
      <p style="margin:0;font-size:12px;color:#64748b">${period}</p>
    </div>
    <table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0">
      <thead>${thead}</thead>
      <tbody>${tbody}</tbody>
    </table>`
      return wrap
    }

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

    const exportPdf = async () => {
      let host = null
      try {
        const { default: html2canvas } = await import('html2canvas')
        host = buildPdfExportHost()
        // Нельзя opacity < 1: html2canvas переносит прозрачность в растр — PDF выглядит пустым.
        host.style.position = 'fixed'
        host.style.left = '-14000px'
        host.style.top = '0'
        host.style.opacity = '1'
        host.style.visibility = 'visible'
        host.style.pointerEvents = 'none'
        host.style.zIndex = '2147483646'
        document.body.appendChild(host)
        await nextTick()
        if (document.fonts?.ready) {
          await document.fonts.ready.catch(() => {})
        }
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))

        const canvas = await html2canvas(host, {
          scale: 2,
          backgroundColor: '#ffffff',
          logging: false,
          useCORS: false,
          foreignObjectRendering: false,
          removeContainer: true
        })

        if (!canvas.width || !canvas.height) {
          throw new Error('PDF canvas is empty')
        }

        let imgData
        let imgFmt = 'PNG'
        try {
          imgData = canvas.toDataURL('image/png')
        } catch {
          imgData = canvas.toDataURL('image/jpeg', 0.92)
          imgFmt = 'JPEG'
        }

        const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
        const pageWidth = pdf.internal.pageSize.getWidth()
        const pageHeight = pdf.internal.pageSize.getHeight()
        const imgWidth = pageWidth
        const imgHeight = (canvas.height * imgWidth) / canvas.width

        let heightLeft = imgHeight
        let position = 0

        pdf.addImage(imgData, imgFmt, 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight

        while (heightLeft >= 0) {
          position = heightLeft - imgHeight
          pdf.addPage()
          pdf.addImage(imgData, imgFmt, 0, position, imgWidth, imgHeight)
          heightLeft -= pageHeight
        }

        pdf.save(`report-${startDate.value || 'all'}-${endDate.value || 'all'}.pdf`)
      } catch (err) {
        console.error(err)
        toast.error(t('reports.pdfError'))
      } finally {
        if (host?.parentNode) {
          host.parentNode.removeChild(host)
        }
      }
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
      formatSeconds,
      // Charts
      statusChartData,
      statusChartOptions,
      timeByProjectData,
      timeByProjectOptions,
      // Project stats
      projectStats
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
  background: var(--card-bg);
  box-shadow: 0 10px 24px rgba(136, 110, 149, 0.14);
}

.period-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.period-tab {
  border: 1px solid rgba(216, 196, 226, 0.8);
  background: var(--surface-1);
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

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.chart-body {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
}

.donut-wrap,
.bar-wrap {
  width: 100%;
  max-width: 320px;
  height: 220px;
  position: relative;
}

.bar-wrap {
  max-width: 100%;
  height: 240px;
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
  background: var(--glass-panel-bg);
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

/* Project Stats */
.projects-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.project-stat-card {
  border: 1px solid rgba(224, 209, 233, 0.88);
  border-radius: 12px;
  background: var(--glass-panel-bg);
  padding: 12px;
}

/* Dark theme: отчёты рисовали белые карточки вручную */
:global([data-theme="dark"]) .controls-card,
:global([data-theme="dark"]) .report-card,
:global([data-theme="dark"]) .metric-card {
  border-color: rgba(255, 255, 255, 0.09);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
}

:global([data-theme="dark"]) .metric-card span,
:global([data-theme="dark"]) .top-time,
:global([data-theme="dark"]) .status-row-head,
:global([data-theme="dark"]) .meta-pill {
  color: var(--text-muted);
}

:global([data-theme="dark"]) .metric-card strong,
:global([data-theme="dark"]) .top-title,
:global([data-theme="dark"]) .task-head h6,
:global([data-theme="dark"]) .ps-name {
  color: var(--text-primary);
}

:global([data-theme="dark"]) .period-tab {
  border-color: rgba(255, 255, 255, 0.12);
  color: var(--text-secondary);
}

.ps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.ps-name {
  margin: 0;
  font-size: 0.9rem;
  color: #34466d;
  font-weight: 600;
}

.ps-total-badge {
  background: #efe7ff;
  border: 1px solid #d4c1ff;
  color: #6846a8;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.ps-bar {
  display: flex;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: #ebeef3;
  margin-bottom: 8px;
}

.ps-bar-fill {
  height: 100%;
}

.ps-done { background: linear-gradient(90deg, #47bf86, #2f9f6a); }
.ps-progress { background: linear-gradient(90deg, #4f89f0, #2f74e3); }

.ps-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ps-stat {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 0.72rem;
  font-weight: 600;
  background: #f3edf8;
  color: #685a83;
}

.ps-stat .fa-check-circle { color: #2c8059; }
.ps-stat .fa-spinner { color: #3657a4; }
.ps-stat .fa-clock { color: #5f6676; }

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
  .charts-grid,
  .content-grid,
  .task-grid,
  .custom-range {
    grid-template-columns: 1fr;
  }
}

</style>