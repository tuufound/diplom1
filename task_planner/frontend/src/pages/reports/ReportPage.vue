<template>
  <div class="reports-container">
    <h2 class="mb-4">
      <i class="fas fa-chart-bar me-2"></i>Отчеты и аналитика
    </h2>

    <div class="card mb-4">
      <div class="card-header bg-primary text-white">
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
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header bg-primary text-white">
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
          <div class="card-header bg-primary text-white">
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
      <div class="card-header bg-primary text-white">
        <h5 class="mb-0">Время, затраченное на задачи</h5>
      </div>
      <div class="card-body">
        <div class="chart-container">
          <canvas ref="timeChart"></canvas>
        </div>
      </div>
    </div>

    <div class="card mt-4">
      <div class="card-header bg-primary text-white">
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
                <th>Время</th>
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
import { ru } from 'date-fns/locale'

Chart.register(...registerables)

export default {
  name: 'ReportPage',
  setup() {
    const toast = useToast()

    const tasks = ref([])
    const timeEntries = ref([])
    const loading = ref(false)

    const dateRange = ref('week')
    const startDate = ref('')
    const endDate = ref('')

    const statusChart = ref(null)
    const priorityChart = ref(null)
    const timeChart = ref(null)

    let statusChartInstance = null
    let priorityChartInstance = null
    let timeChartInstance = null

    const fetchData = async () => {
      try {
        loading.value = true
        const [tasksResponse, timeEntriesResponse] = await Promise.all([
          api.getTasks(),
          api.getTimeEntries()
        ])
        tasks.value = tasksResponse.data
        timeEntries.value = timeEntriesResponse.data
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
      const taskTimeEntries = timeEntries.value.filter(entry => entry.task.id === task.id)
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
      const timeData = filteredTasks.value.map(task => {
        return {
          task: task.title,
          time: getTaskTimeInMinutes(task)
        }
      }).sort((a, b) => b.time - a.time).slice(0, 10) // Top 10 tasks by time

      const timeCtx = timeChart.value.getContext('2d')
      timeChartInstance = new Chart(timeCtx, {
        type: 'bar',
        data: {
          labels: timeData.map(item => item.task),
          datasets: [{
            label: 'Время (минуты)',
            data: timeData.map(item => item.time),
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
    }

    const getTaskTimeInMinutes = (task) => {
      const taskTimeEntries = timeEntries.value.filter(entry => entry.task.id === task.id)
      let totalSeconds = 0

      taskTimeEntries.forEach(entry => {
        if (entry.duration) {
          const parts = entry.duration.split(':')
          if (parts.length === 3) {
            totalSeconds += parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2])
          }
        }
      })

      return Math.floor(totalSeconds / 60)
    }

    const applyFilters = () => updateCharts()

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
      updateCharts()
    })

    onMounted(() => {
      fetchData()
      setDateRange()
    })

    return {
      tasks,
      timeEntries,
      loading,
      dateRange,
      startDate,
      endDate,
      statusChart,
      priorityChart,
      timeChart,
      filteredTasks,
      applyFilters,
      getStatusText,
      getStatusBadgeClass,
      getProgressBarClass,
      getProgressWidth,
      getProgressValue,
      getTaskTime
    }
  }
}
</script>

<style scoped>
.reports-container {
  max-width: 1400px;
  margin: 0 auto;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.card {
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: 500;
}

.table-responsive {
  overflow-x: auto;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
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