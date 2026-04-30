<template>
  <div class="reports-container page-shell">
    <h2 class="mb-2 page-title">
      <i class="fas fa-chart-bar me-2"></i>Отчеты и аналитика
    </h2>
    <p class="section-subtitle mb-4">Анализ реального времени по задачам и продуктивности.</p>

    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">Фильтры</h5>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label for="dateRange" class="form-label">Период</label>
            <select class="form-select" id="dateRange" v-model="dateRange">
              <option value="week">Последняя неделя</option>
              <option value="month">Последний месяц</option>
              <option value="quarter">Последний квартал</option>
              <option value="year">Последний год</option>
              <option value="custom">Произвольный</option>
            </select>
          </div>
          <div class="col-md-3" v-if="dateRange === 'custom'">
            <label for="startDate" class="form-label">Начало</label>
            <input type="date" class="form-control" id="startDate" v-model="startDate">
          </div>
          <div class="col-md-3" v-if="dateRange === 'custom'">
            <label for="endDate" class="form-label">Конец</label>
            <input type="date" class="form-control" id="endDate" v-model="endDate">
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-primary w-100" @click="applyFilters">
              <i class="fas fa-filter me-1"></i> Применить
            </button>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-outline-success w-100" @click="exportCsv">
              <i class="fas fa-file-csv me-1"></i> CSV
            </button>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button class="btn btn-outline-danger w-100" @click="exportPdf">
              <i class="fas fa-file-pdf me-1"></i> PDF
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="stat-card">
          <div class="stat-label">Всего задач</div>
          <div class="stat-value">{{ report.total_tasks || 0 }}</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card">
          <div class="stat-label">Потрачено времени</div>
          <div class="stat-value">{{ formatSeconds(report.total_tracked_seconds || 0) }}</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card">
          <div class="stat-label">Среднее выполнение</div>
          <div class="stat-value">{{ avgCompletionLabel }}</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stat-card">
          <div class="stat-label">Закрыто задач</div>
          <div class="stat-value">{{ report.completed_tasks || 0 }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Статистика по статусам</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="statusChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-6">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Статистика по приоритетам</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="priorityChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card mt-4">
      <div class="card-header">
        <h5 class="mb-0">Самые дорогие задачи по времени</h5>
      </div>
      <div class="card-body">
        <div class="chart-container">
          <canvas ref="timeChart"></canvas>
        </div>
      </div>
    </div>

    <div class="card mt-4">
      <div class="card-header">
        <h5 class="mb-0">Продуктивность по дням недели</h5>
      </div>
      <div class="card-body">
        <div class="chart-container">
          <canvas ref="weekdayChart"></canvas>
        </div>
      </div>
    </div>

    <div class="card mt-4">
      <div class="card-header">
        <h5 class="mb-0">Детальная статистика</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Задача</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Категория</th>
                <th>Реально потратил</th>
                <th>Прогресс</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in filteredTasks" :key="task.id">
                <td>{{ task.title }}</td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(task.status)">
                    {{ getStatusText(task.status) }}
                  </span>
                </td>
                <td>
                  <span v-if="task.priority" class="badge bg-warning text-dark">
                    {{ task.priority.name }}
                  </span>
                </td>
                <td>
                  <span v-if="task.category" class="badge bg-info">
                    {{ task.category.name }}
                  </span>
                </td>
                <td>{{ getTaskTime(task) }}</td>
                <td>
                  <div class="progress" style="height: 20px;">
                    <div
                      class="progress-bar"
                      :class="getProgressBarClass(task.status)"
                      role="progressbar"
                      :style="{ width: getProgressWidth(task.status) }"
                      :aria-valuenow="getProgressValue(task.status)"
                      aria-valuemin="0"
                      aria-valuemax="100"
                    ></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { Chart, registerables } from 'chart.js'
import { format, subDays, subMonths, subQuarters, subYears, parseISO } from 'date-fns'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

Chart.register(...registerables)

export default {
  name: 'ReportPage',
  setup() {
    const toast = useToast()

    const tasks = ref([])
    const timeEntries = ref([])
    const report = ref({})
    const loading = ref(false)

    const dateRange = ref('week')
    const startDate = ref('')
    const endDate = ref('')

    const statusChart = ref(null)
    const priorityChart = ref(null)
    const timeChart = ref(null)
    const weekdayChart = ref(null)

    let statusChartInstance = null
    let priorityChartInstance = null
    let timeChartInstance = null
    let weekdayChartInstance = null

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
        updateCharts()
      } catch (error) {
        toast.error('Ошибка загрузки данных для отчетов')
        console.error('Error fetching report data:', error)
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
    const avgCompletionLabel = computed(() => {
      if (!report.value?.avg_completion_seconds) return 'Нет данных'
      return formatSeconds(report.value.avg_completion_seconds)
    })

    const getStatusText = (status) => {
      const statusMap = {
        'todo': 'К выполнению',
        'in_progress': 'В процессе',
        'done': 'Выполнено',
        'archived': 'В архиве'
      }
      return statusMap[status] || status
    }

    const getStatusBadgeClass = (status) => {
      const statusMap = {
        'todo': 'bg-secondary',
        'in_progress': 'bg-primary',
        'done': 'bg-success',
        'archived': 'bg-dark'
      }
      return statusMap[status] || 'bg-secondary'
    }

    const getProgressBarClass = (status) => {
      const statusMap = {
        'todo': 'bg-secondary',
        'in_progress': 'bg-primary',
        'done': 'bg-success',
        'archived': 'bg-dark'
      }
      return statusMap[status] || 'bg-secondary'
    }

    const getProgressWidth = (status) => {
      const statusMap = {
        'todo': '25%',
        'in_progress': '75%',
        'done': '100%',
        'archived': '100%'
      }
      return statusMap[status] || '25%'
    }

    const getProgressValue = (status) => {
      const statusMap = {
        'todo': 25,
        'in_progress': 75,
        'done': 100,
        'archived': 100
      }
      return statusMap[status] || 25
    }

    const getTaskTime = (task) => {
      // Calculate total time spent on this task
      const start = startDate.value ? parseISO(`${startDate.value}T00:00:00`) : null
      const end = endDate.value ? parseISO(`${endDate.value}T23:59:59`) : null
      const taskTimeEntries = timeEntries.value.filter(entry => {
        if (entry.task.id !== task.id) return false
        if (!start || !end) return true
        const entryStart = parseISO(entry.start_time)
        return entryStart >= start && entryStart <= end
      })
      let totalSeconds = 0

      taskTimeEntries.forEach(entry => {
        if (entry.duration) {
          const parts = entry.duration.split(':')
          if (parts.length === 3) {
            totalSeconds += parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2])
          }
        }
      })

      const hours = Math.floor(totalSeconds / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)

      if (hours > 0) {
        return `${hours}ч ${minutes}м`
      } else if (minutes > 0) {
        return `${minutes}м`
      } else {
        return '0м'
      }
    }

    const updateCharts = () => {
      // Destroy existing charts
      if (statusChartInstance) statusChartInstance.destroy()
      if (priorityChartInstance) priorityChartInstance.destroy()
      if (timeChartInstance) timeChartInstance.destroy()
      if (weekdayChartInstance) weekdayChartInstance.destroy()

      // Status chart
      const statusCounts = {
        'todo': 0,
        'in_progress': 0,
        'done': 0,
        'archived': 0
      }

      filteredTasks.value.forEach(task => {
        statusCounts[task.status]++
      })

      const statusCtx = statusChart.value.getContext('2d')
      statusChartInstance = new Chart(statusCtx, {
        type: 'doughnut',
        data: {
          labels: ['К выполнению', 'В процессе', 'Выполнено', 'В архиве'],
          datasets: [{
            data: [
              statusCounts.todo,
              statusCounts.in_progress,
              statusCounts.done,
              statusCounts.archived
            ],
            backgroundColor: [
              '#6c757d',
              '#0d6efd',
              '#198754',
              '#212529'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.raw || 0
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = total ? Math.round((value / total) * 100) : 0
                  return `${label}: ${value} (${percentage}%)`
                }
              }
            }
          }
        }
      })

      // Priority chart
      const priorityCounts = {}
      filteredTasks.value.forEach(task => {
        if (task.priority) {
          const priorityName = task.priority.name
          priorityCounts[priorityName] = (priorityCounts[priorityName] || 0) + 1
        }
      })

      const priorityCtx = priorityChart.value.getContext('2d')
      priorityChartInstance = new Chart(priorityCtx, {
        type: 'bar',
        data: {
          labels: Object.keys(priorityCounts),
          datasets: [{
            label: 'Количество задач',
            data: Object.values(priorityCounts),
            backgroundColor: '#fd7e14',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })

      // Time chart
      const topTimeTasks = report.value.top_time_tasks || []

      const timeCtx = timeChart.value.getContext('2d')
      timeChartInstance = new Chart(timeCtx, {
        type: 'bar',
        data: {
          labels: topTimeTasks.map(item => item.task_title),
          datasets: [{
            label: 'Время (минуты)',
            data: topTimeTasks.map(item => Math.round(item.seconds / 60)),
            backgroundColor: '#42b983',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              display: false
            }
          },
          indexAxis: 'y'
        }
      })

      const weekdayData = report.value.productivity_by_weekday || []
      const weekdayCtx = weekdayChart.value.getContext('2d')
      weekdayChartInstance = new Chart(weekdayCtx, {
        type: 'line',
        data: {
          labels: weekdayData.map(item => item.weekday),
          datasets: [{
            label: 'Часы',
            data: weekdayData.map(item => Number((item.seconds / 3600).toFixed(2))),
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37,99,235,0.15)',
            fill: true,
            tension: 0.35
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      })
    }

    const formatSeconds = (seconds) => {
      const safeSeconds = Math.max(0, Number(seconds) || 0)
      const hours = Math.floor(safeSeconds / 3600)
      const minutes = Math.floor((safeSeconds % 3600) / 60)
      if (hours > 0) return `${hours}ч ${minutes}м`
      return `${minutes}м`
    }

    const applyFilters = () => fetchData()

    const getRowsForExport = () => {
      return filteredTasks.value.map(task => ([
        task.title,
        getStatusText(task.status),
        task.priority?.name || '-',
        task.category?.name || '-',
        getTaskTime(task)
      ]))
    }

    const exportCsv = () => {
      const header = ['Задача', 'Статус', 'Приоритет', 'Категория', 'Время']
      const rows = getRowsForExport()
      const csv = [header, ...rows]
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
      doc.text('Отчет по задачам', 14, 16)
      autoTable(doc, {
        startY: 24,
        head: [['Задача', 'Статус', 'Приоритет', 'Категория', 'Время']],
        body: getRowsForExport(),
        styles: { fontSize: 9 }
      })
      doc.save(`report-${startDate.value || 'all'}-${endDate.value || 'all'}.pdf`)
    }

    const setDateRange = () => {
      const now = new Date()
      let start

      switch (dateRange.value) {
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

    watch(dateRange, () => {
      setDateRange()
      fetchData()
    })

    onMounted(() => {
      setDateRange()
      fetchData()
    })

    return {
      tasks,
      timeEntries,
      loading,
      report,
      dateRange,
      startDate,
      endDate,
      statusChart,
      priorityChart,
      timeChart,
      weekdayChart,
      filteredTasks,
      avgCompletionLabel,
      applyFilters,
      exportCsv,
      exportPdf,
      getStatusText,
      getStatusBadgeClass,
      getProgressBarClass,
      getProgressWidth,
      getProgressValue,
      getTaskTime,
      formatSeconds
    }
  }
}
</script>

<style scoped>
.reports-container {
  max-width: 1400px;
  margin: 0 auto;
}

.stat-card {
  padding: 16px 18px;
  border: 1px solid rgba(188, 204, 233, 0.9);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.74);
  box-shadow: 0 10px 24px rgba(35, 63, 123, 0.08);
  backdrop-filter: blur(8px);
}

.stat-label {
  font-size: 0.86rem;
  color: #5f7092;
}

.stat-value {
  font-size: 1.42rem;
  line-height: 1.1;
  font-weight: 700;
  color: #16253f;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.card {
  margin-bottom: 20px;
  box-shadow: 0 10px 24px rgba(35, 63, 123, 0.08);
}

.card-header {
  font-weight: 500;
}

.table-responsive {
  overflow-x: auto;
}

.table th {
  background-color: rgba(245, 249, 255, 0.9);
  border-bottom: 2px solid #d9e4f6;
}

.badge {
  font-size: 0.85em;
}

.progress {
  margin-bottom: 0;
}

@media (max-width: 992px) {
  .reports-container {
    padding: 0 15px;
  }
}
</style>