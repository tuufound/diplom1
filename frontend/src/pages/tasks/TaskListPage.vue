<template>
  <div class="tasks-page page-shell">
    <div class="page-content-surface">
      <div class="tasks-head">
        <div>
          <h2 class="page-title"><i class="fas fa-list-check me-2"></i>{{ $t('tasksList.title') }}</h2>
          <p class="section-subtitle">{{ $t('tasksList.subtitle') }}</p>
        </div>
        <div class="tasks-actions">
          <router-link to="/tasks/create" class="btn btn-primary">
            <i class="fas fa-plus me-1"></i> {{ $t('tasksList.newTask') }}
          </router-link>
        </div>
      </div>

      <div class="tasks-toolbar card">
        <div class="card-body">
          <!-- Primary row: search + quick scope + new task -->
          <div class="toolbar-primary">
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input v-model="query" class="form-control" type="text" :placeholder="$t('tasksList.searchPlaceholder')">
              <button v-if="query" class="search-clear-btn" type="button" @click="query = ''" title="Clear search">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="scope-pills">
              <button type="button" class="scope-pill" :class="{ active: taskScope === 'all' }" @click="setTaskScope('all')">
                <i class="fas fa-layer-group me-1"></i>{{ $t('tasksList.allTasks') }}
              </button>
              <button type="button" class="scope-pill" :class="{ active: taskScope === 'collaborative' }" @click="setTaskScope('collaborative')">
                <i class="fas fa-users me-1"></i>{{ $t('tasksList.collaborative') }}
              </button>
              <button type="button" class="scope-pill" :class="{ active: taskScope === 'favorites' }" @click="setTaskScope('favorites')">
                <i class="fas fa-star me-1"></i>{{ $t('tasksList.favorites') }}
              </button>
            </div>
            <div class="view-toggle">
              <button
                type="button"
                class="view-btn"
                :class="{ active: groupMode === 'flat' }"
                @click="groupMode = 'flat'"
                :title="$t('tasksList.viewList')"
              >
                <i class="fas fa-list"></i>
              </button>
              <button
                type="button"
                class="view-btn"
                :class="{ active: groupMode === 'project' }"
                @click="groupMode = 'project'"
                :title="$t('tasksList.viewByProject')"
              >
                <i class="fas fa-layer-group"></i>
              </button>
            </div>
            <router-link to="/tasks/create" class="btn btn-primary btn-new-task">
              <i class="fas fa-plus me-1"></i>{{ $t('tasksList.newTask') }}
            </router-link>
          </div>

          <!-- Filter row: status + project quick chips -->
          <div class="toolbar-filters-row">
            <div class="filter-group">
              <label class="filter-label"><i class="fas fa-filter me-1"></i>Статус:</label>
              <div class="status-quick-chips">
                <button
                  v-for="s in quickStatusOptions"
                  :key="s.value"
                  class="quick-chip"
                  :class="[getQuickChipClass(s.value), { active: statusFilter === s.value }]"
                  @click="toggleStatusFilter(s.value)"
                >
                  <i :class="s.icon"></i>{{ s.label }}
                  <span v-if="getStatusCount(s.value) !== null" class="chip-count">{{ getStatusCount(s.value) }}</span>
                </button>
              </div>
            </div>
            <div v-if="hasActiveFilters" class="clear-filters-btn" @click="clearAllFilters" role="button" tabindex="0">
              <i class="fas fa-times-circle me-1"></i>Сбросить фильтры
            </div>
          </div>

          <!-- Active filter chips bar -->
          <div v-if="hasActiveFilters" class="active-filters-bar">
            <span class="active-filters-label"><i class="fas fa-tag me-1"></i>Фильтры:</span>
            <span v-if="statusFilter !== 'all'" class="active-chip">
              <i class="fas fa-circle status-dot" :class="'dot-' + statusFilter"></i>
              {{ getStatusText(statusFilter) }}
              <button type="button" class="active-chip-remove" @click="statusFilter = 'all'"><i class="fas fa-times"></i></button>
            </span>
            <span v-if="projectFilter !== 'all'" class="active-chip">
              <i class="fas fa-folder-open me-1"></i>{{ projectFilter === 'none' ? $t('tasksList.noProject') : getProjectName(projectFilter) }}
              <button type="button" class="active-chip-remove" @click="projectFilter = 'all'"><i class="fas fa-times"></i></button>
            </span>
          </div>

          <!-- Advanced filters toggle -->
          <div class="advanced-toggle-row">
            <button class="advanced-toggle-btn" type="button" :class="{ active: showAdvancedFilters }" @click="showAdvancedFilters = !showAdvancedFilters">
              <i class="fas fa-sliders-h me-1"></i>Все фильтры
              <i class="fas fa-chevron-down ms-auto" :class="{ 'rotate-180': showAdvancedFilters }"></i>
            </button>
          </div>

          <!-- Advanced filters panel -->
          <div v-if="showAdvancedFilters" class="advanced-filters-panel">
            <div class="advanced-grid">
              <div class="adv-filter-group">
                <label class="adv-label">Проект</label>
                <select v-model="projectFilter" class="form-select">
                  <option value="all">{{ $t('tasksList.allProjects') }}</option>
                  <option value="none">{{ $t('tasksList.noProject') }}</option>
                  <option v-for="proj in projects" :key="proj.id" :value="proj.id">{{ proj.name }}</option>
                </select>
              </div>
              <div class="adv-filter-group">
                <label class="adv-label">Статус (полный)</label>
                <select v-model="statusFilter" class="form-select">
                  <option value="all">{{ $t('tasksList.allStatuses') }}</option>
                  <option value="todo">{{ $t('taskStatus.todo') }}</option>
                  <option value="in_progress">{{ $t('taskStatus.in_progress') }}</option>
                  <option value="done">{{ $t('taskStatus.done') }}</option>
                  <option value="archived">{{ $t('taskStatus.archived') }}</option>
                </select>
              </div>
            </div>
          </div>

          <!-- KPIs -->
          <div class="kpis">
            <span class="kpi"><i class="fas fa-bolt me-1"></i>{{ $t('tasksList.kpiActive') }} <strong>{{ activeTasksCount }}</strong></span>
            <span class="kpi"><i class="fas fa-calendar-day me-1"></i>{{ $t('tasksList.kpiToday') }} <strong>{{ todayTasksCount }}</strong></span>
            <span class="kpi kpi-overdue"><i class="fas fa-exclamation-triangle me-1"></i>{{ $t('tasksList.kpiOverdue') }} <strong>{{ overdueTasksCount }}</strong></span>
          </div>
        </div>
      </div>

      <div v-if="visibleTasksFiltered.length === 0" class="empty-state card">
        <div class="card-body">
          <i class="fas fa-inbox"></i>
          <p>{{ $t('tasksList.empty') }}</p>
        </div>
      </div>

      <div v-else class="task-rows">
        <!-- Flat grouped view (subtask blocks) -->
        <template v-if="groupMode === 'flat'">
          <template v-for="block in groupedFilteredRows" :key="blockKey(block)">
            <div v-if="block.kind === 'block'" class="task-block">
            <article
              v-for="item in [block.parentItem]"
              :key="'p-' + item.task.id"
              class="task-row"
              :class="[getRowClass(item.task), { 'is-child': item.isChild }]"
              @click="goToTaskDetail(item.task.id)"
            >
            <div class="task-main">
              <div class="title-row">
                <button
                  v-if="hasSubtasks(item.task.id)"
                  class="collapse-btn"
                  type="button"
                  :aria-expanded="isExpanded(item.task.id)"
                  @click.stop="toggleSubtasks(item.task.id)"
                >
                  <i class="fas fa-chevron-right collapse-chevron" :class="{ 'is-open': isExpanded(item.task.id) }"></i>
                </button>
                <span v-else class="collapse-placeholder"></span>
                <h6 class="task-title">{{ item.task.title }}</h6>
              </div>
              <p v-if="item.task.description" class="task-sub">{{ truncateText(item.task.description, 110) }}</p>
              <div class="chips">
                <span class="chip" :class="getStatusChipClass(item.task.status)">{{ getStatusText(item.task.status) }}</span>
                <span class="chip muted">{{ formatDate(item.task.created_at) }}</span>
                <span v-if="!item.task.project" class="chip chip-personal">{{ $t('tasksList.personal') }}</span>
                <span v-if="item.task.project" class="chip chip-collaborative">{{ $t('tasksList.collaborativeChip') }}</span>
                <span v-if="item.task.project" class="chip" :class="getProjectChipClass(item.task.project?.id)">{{ item.task.project.name }}</span>
                <span v-if="item.task.category" class="chip" :class="getCategoryChipClass(item.task.category?.id)">
                  <span class="me-1">{{ item.task.category.icon || '📁' }}</span>{{ item.task.category.name }}
                </span>
                <span v-if="item.task.priority" class="chip" :class="getPriorityChipClass(item.task.priority)">{{ item.task.priority.name }}</span>
                <span v-if="item.isChild" class="chip child">{{ $t('tasksList.subtaskChip') }}</span>
                <span v-if="item.task.collaborators?.length" class="chip chip-coworkers">
                  <i class="fas fa-users me-1"></i>{{ item.task.collaborators.map((u) => u.username).join(', ') }}
                </span>
                <span v-if="countdownLabelForTask(item.task.id)" class="chip chip-timer-countdown">
                  <i class="fas fa-bell me-1"></i>{{ $t('tasksList.countdownBell') }} {{ countdownLabelForTask(item.task.id) }}
                </span>
              </div>
            </div>
            <div class="task-actions">
              <button
                class="icon-btn star-btn"
                :class="{ active: item.task.is_favorited }"
                type="button"
                @click.stop="toggleFavorite(item.task)"
                :title="$t('tasksList.favorite')"
              >
                <i class="fas fa-star"></i>
              </button>
              <button class="icon-btn" @click.stop="toggleTimeTracking(item.task)" :disabled="!item.task.can_edit" :title="$t('tasksList.timer')">
                <i class="fas" :class="getTimeTrackingIcon(item.task)"></i>
              </button>
              <button class="icon-btn" @click.stop="editTask(item.task.id)" :disabled="!item.task.can_edit" :title="$t('common.edit')">
                <i class="fas fa-pen"></i>
              </button>
              <button class="icon-btn danger" @click.stop="deleteTask(item.task.id)" :disabled="!item.task.can_delete" :title="$t('common.delete')">
                <i class="fas fa-trash"></i>
              </button>
              <router-link class="icon-btn" :to="`/tasks/create?parent=${item.task.id}`" :title="$t('tasksList.subtask')">
                <i class="fas fa-folder"></i>
              </router-link>
            </div>
            </article>
            <div
              v-if="hasSubtasks(block.parentItem.task.id)"
              class="subtask-panel"
              :class="{ 'subtask-panel--open': isExpanded(block.parentItem.task.id) }"
              :aria-hidden="!isExpanded(block.parentItem.task.id)"
            >
              <div class="subtask-panel-inner">
                <TaskListSubtaskNode
                  v-for="st in filteredSubtasksFor(block.parentItem.task.id)"
                  :key="st.id"
                  :task="st"
                  :depth="1"
                />
              </div>
            </div>
          </div>
          <div v-else class="task-block task-block--orphan">
            <article
              v-for="item in [block.row]"
              :key="'o-' + item.task.id"
              class="task-row"
              :class="[getRowClass(item.task), { 'is-child': item.isChild }]"
              @click="goToTaskDetail(item.task.id)"
            >
            <div class="task-main">
              <div class="title-row">
                <button
                  v-if="hasSubtasks(item.task.id)"
                  class="collapse-btn"
                  type="button"
                  :aria-expanded="isExpanded(item.task.id)"
                  @click.stop="toggleSubtasks(item.task.id)"
                >
                  <i class="fas fa-chevron-right collapse-chevron" :class="{ 'is-open': isExpanded(item.task.id) }"></i>
                </button>
                <span v-else class="collapse-placeholder"></span>
                <h6 class="task-title">{{ item.task.title }}</h6>
              </div>
              <p v-if="item.task.description" class="task-sub">{{ truncateText(item.task.description, 110) }}</p>
              <div class="chips">
                <span class="chip" :class="getStatusChipClass(item.task.status)">{{ getStatusText(item.task.status) }}</span>
                <span class="chip muted">{{ formatDate(item.task.created_at) }}</span>
                <span v-if="!item.task.project" class="chip chip-personal">{{ $t('tasksList.personal') }}</span>
                <span v-if="item.task.project" class="chip chip-collaborative">{{ $t('tasksList.collaborativeChip') }}</span>
                <span v-if="item.task.project" class="chip" :class="getProjectChipClass(item.task.project?.id)">{{ item.task.project.name }}</span>
                <span v-if="item.task.category" class="chip" :class="getCategoryChipClass(item.task.category?.id)">
                  <span class="me-1">{{ item.task.category.icon || '📁' }}</span>{{ item.task.category.name }}
                </span>
                <span v-if="item.task.priority" class="chip" :class="getPriorityChipClass(item.task.priority)">{{ item.task.priority.name }}</span>
                <span v-if="item.isChild" class="chip child">{{ $t('tasksList.subtaskChip') }}</span>
                <span v-if="item.task.collaborators?.length" class="chip chip-coworkers">
                  <i class="fas fa-users me-1"></i>{{ item.task.collaborators.map((u) => u.username).join(', ') }}
                </span>
                <span v-if="countdownLabelForTask(item.task.id)" class="chip chip-timer-countdown">
                  <i class="fas fa-bell me-1"></i>{{ $t('tasksList.countdownBell') }} {{ countdownLabelForTask(item.task.id) }}
                </span>
              </div>
            </div>
            <div class="task-actions">
              <button
                class="icon-btn star-btn"
                :class="{ active: item.task.is_favorited }"
                type="button"
                @click.stop="toggleFavorite(item.task)"
                :title="$t('tasksList.favorite')"
              >
                <i class="fas fa-star"></i>
              </button>
              <button class="icon-btn" @click.stop="toggleTimeTracking(item.task)" :disabled="!item.task.can_edit" :title="$t('tasksList.timer')">
                <i class="fas" :class="getTimeTrackingIcon(item.task)"></i>
              </button>
              <button class="icon-btn" @click.stop="editTask(item.task.id)" :disabled="!item.task.can_edit" :title="$t('common.edit')">
                <i class="fas fa-pen"></i>
              </button>
              <button class="icon-btn danger" @click.stop="deleteTask(item.task.id)" :disabled="!item.task.can_delete" :title="$t('common.delete')">
                <i class="fas fa-trash"></i>
              </button>
              <router-link class="icon-btn" :to="`/tasks/create?parent=${item.task.id}`" :title="$t('tasksList.subtask')">
                <i class="fas fa-folder"></i>
              </router-link>
            </div>
            </article>
            <div
              v-if="hasSubtasks(block.row.task.id)"
              class="subtask-panel"
              :class="{ 'subtask-panel--open': isExpanded(block.row.task.id) }"
              :aria-hidden="!isExpanded(block.row.task.id)"
            >
              <div class="subtask-panel-inner">
                <TaskListSubtaskNode
                  v-for="st in filteredSubtasksFor(block.row.task.id)"
                  :key="st.id"
                  :task="st"
                  :depth="1"
                />
              </div>
            </div>
          </div>
        </template>
        </template>

        <!-- Project-grouped view -->
        <template v-if="groupMode === 'project'">
          <div
            v-for="group in groupedByProjectRows"
            :key="group.groupKey"
            class="project-group"
          >
            <!-- Project group header -->
            <button
              class="project-group-header"
              type="button"
              @click="toggleProject(group.projectId)"
            >
              <i class="fas fa-chevron-right group-chevron" :class="{ 'is-open': isProjectExpanded(group.projectId) }"></i>
              <i class="fas fa-folder-open group-icon"></i>
              <span class="group-name">{{ group.projectName }}</span>
              <span class="group-count">{{ group.tasks.length }}</span>
            </button>

            <!-- Project group tasks -->
            <div
              class="project-tasks-panel"
              :class="{ 'is-open': isProjectExpanded(group.projectId) }"
            >
              <div class="project-tasks-inner">
                <template v-for="item in group.tasks" :key="'g-' + item.task.id">
                  <article
                    class="task-row"
                    :class="getRowClass(item.task)"
                    @click="goToTaskDetail(item.task.id)"
                  >
                    <div class="task-main">
                      <div class="title-row">
                        <button
                          v-if="hasSubtasks(item.task.id)"
                          class="collapse-btn"
                          type="button"
                          :aria-expanded="isExpanded(item.task.id)"
                          @click.stop="toggleSubtasks(item.task.id)"
                        >
                          <i class="fas fa-chevron-right collapse-chevron" :class="{ 'is-open': isExpanded(item.task.id) }"></i>
                        </button>
                        <span v-else class="collapse-placeholder"></span>
                        <h6 class="task-title">{{ item.task.title }}</h6>
                      </div>
                      <p v-if="item.task.description" class="task-sub">{{ truncateText(item.task.description, 110) }}</p>
                      <div class="chips">
                        <span class="chip" :class="getStatusChipClass(item.task.status)">{{ getStatusText(item.task.status) }}</span>
                        <span class="chip muted">{{ formatDate(item.task.created_at) }}</span>
                        <span v-if="item.task.category" class="chip" :class="getCategoryChipClass(item.task.category?.id)">
                          <span class="me-1">{{ item.task.category.icon || '📁' }}</span>{{ item.task.category.name }}
                        </span>
                        <span v-if="item.task.priority" class="chip" :class="getPriorityChipClass(item.task.priority)">{{ item.task.priority.name }}</span>
                        <span v-if="countdownLabelForTask(item.task.id)" class="chip chip-timer-countdown">
                          <i class="fas fa-bell me-1"></i>{{ $t('tasksList.countdownBell') }} {{ countdownLabelForTask(item.task.id) }}
                        </span>
                      </div>
                    </div>
                    <div class="task-actions">
                      <button
                        class="icon-btn star-btn"
                        :class="{ active: item.task.is_favorited }"
                        type="button"
                        @click.stop="toggleFavorite(item.task)"
                        :title="$t('tasksList.favorite')"
                      >
                        <i class="fas fa-star"></i>
                      </button>
                      <button class="icon-btn" @click.stop="toggleTimeTracking(item.task)" :disabled="!item.task.can_edit" :title="$t('tasksList.timer')">
                        <i class="fas" :class="getTimeTrackingIcon(item.task)"></i>
                      </button>
                      <button class="icon-btn" @click.stop="editTask(item.task.id)" :disabled="!item.task.can_edit" :title="$t('common.edit')">
                        <i class="fas fa-pen"></i>
                      </button>
                      <button class="icon-btn danger" @click.stop="deleteTask(item.task.id)" :disabled="!item.task.can_delete" :title="$t('common.delete')">
                        <i class="fas fa-trash"></i>
                      </button>
                      <router-link class="icon-btn" :to="`/tasks/create?parent=${item.task.id}`" :title="$t('tasksList.subtask')">
                        <i class="fas fa-folder"></i>
                      </router-link>
                    </div>
                  </article>

                  <!-- Subtasks panel for project-group view -->
                  <div
                    v-if="hasSubtasks(item.task.id)"
                    class="subtask-panel"
                    :class="{ 'subtask-panel--open': isExpanded(item.task.id) }"
                    :aria-hidden="!isExpanded(item.task.id)"
                  >
                    <div class="subtask-panel-inner">
                      <TaskListSubtaskNode
                        v-for="st in filteredSubtasksFor(item.task.id)"
                        :key="st.id"
                        :task="st"
                        :depth="1"
                      />
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div v-if="timerModalOpen" class="timer-modal-backdrop" @click.self="timerModalOpen = false">
        <div class="timer-modal card shadow" @click.stop>
          <div class="card-body">
            <h5 class="card-title mb-2">
              <i class="fas fa-clock me-2 text-primary"></i>{{ $t('tasksList.timerModalTitle') }}
            </h5>
            <p v-if="timerModalTask" class="text-muted small mb-3">
              {{ $t('tasksList.timerTaskLabel') }} <strong>{{ timerModalTask.title }}</strong>
            </p>
            <div class="mb-3">
              <label class="form-label">{{ $t('tasksList.limitMinutes') }}</label>
              <input
                v-model.number="timerModalMinutes"
                type="number"
                class="form-control"
                min="0"
                max="720"
                :placeholder="$t('tasksList.limitPlaceholder')"
              >
              <small class="form-text text-muted">{{ $t('tasksList.limitHint') }}</small>
            </div>
            <div class="form-check mb-2">
              <input id="tm-sound" v-model="timerModalSound" class="form-check-input" type="checkbox">
              <label class="form-check-label" for="tm-sound">{{ $t('tasksList.soundEnd') }}</label>
            </div>
            <div class="form-check mb-3">
              <input id="tm-stop" v-model="timerModalAutoStop" class="form-check-input" type="checkbox">
              <label class="form-check-label" for="tm-stop">{{ $t('tasksList.autoStop') }}</label>
            </div>
            <div class="d-flex flex-wrap gap-2 justify-content-between">
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="playTimerPreview">
                <i class="fas fa-volume-high me-1"></i>{{ $t('tasksList.previewSound') }}
              </button>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-outline-secondary" @click="timerModalOpen = false">{{ $t('tasksList.timerCancel') }}</button>
                <button type="button" class="btn btn-primary" @click="confirmStartTimer">{{ $t('tasksList.timerStart') }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, provide } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import { useToast } from 'vue-toastification'
import { useTaskTimerCountdown } from '@/composables/useTaskTimerCountdown'
import { playTimerExpirySound } from '@/utils/timerAlertSound'
import { useAppDateLocale } from '@/composables/useAppDateLocale'
import { format, startOfMonth, endOfMonth, startOfWeek, addDays, isSameMonth, isSameDay } from 'date-fns'
import TaskListSubtaskNode from './TaskListSubtaskNode.vue'

export default {
  name: 'TaskListPage',
  components: { TaskListSubtaskNode },
  setup() {
    const { t } = useI18n()
    const dateLocale = useAppDateLocale()
    const router = useRouter()
    const toast = useToast()

    const tasks = ref([])
    const categories = ref([])
    const priorities = ref([])
    const projects = ref([])
    const timeEntries = ref([])
    const loading = ref(false)
    const currentDate = ref(new Date())
    const weekDays = computed(() => [
      t('tasksList.wd0'),
      t('tasksList.wd1'),
      t('tasksList.wd2'),
      t('tasksList.wd3'),
      t('tasksList.wd4'),
      t('tasksList.wd5'),
      t('tasksList.wd6')
    ])
    const expandedParents = ref({})
    const expandedProjects = ref({})
    const groupMode = ref('flat') // 'flat' | 'project'
    const query = ref('')
    const statusFilter = ref('all')
    const projectFilter = ref('all')
    const taskScope = ref('all')

    const timerModalOpen = ref(false)
    const timerModalTask = ref(null)
    const timerModalMinutes = ref(25)
    const timerModalSound = ref(true)
    const timerModalAutoStop = ref(false)
    const showAdvancedFilters = ref(false)

    const fetchTasks = async () => {
      try {
        loading.value = true
        const params = {}
        if (taskScope.value === 'collaborative') params.collaborative = 1
        if (taskScope.value === 'favorites') params.favorites = 1
        const response = await api.getTasks(params)
        tasks.value = response.data
      } catch (error) {
        toast.error(t('tasksList.loadError'))
        console.error('Error fetching tasks:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchCategories = async () => {
      try {
        const response = await api.getCategories()
        categories.value = response.data
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }

    const fetchPriorities = async () => {
      try {
        const response = await api.getPriorities()
        priorities.value = response.data
      } catch (error) {
        console.error('Error fetching priorities:', error)
      }
    }

    const fetchProjects = async () => {
      try {
        const response = await api.getProjects()
        projects.value = response.data
      } catch (error) {
        console.error('Error fetching projects:', error)
      }
    }

    const filteredTasks = computed(() => tasks.value)
    const tasksByParent = computed(() => {
      const map = {}
      for (const task of tasks.value) {
        const parentId = task.parent_task?.id || null
        if (!map[parentId]) {
          map[parentId] = []
        }
        map[parentId].push(task)
      }
      return map
    })
    const visibleTasks = computed(() => {
      const result = []
      const knownIds = new Set(tasks.value.map(task => task.id))
      const roots = [
        ...(tasksByParent.value[null] || []),
        ...tasks.value.filter(task => task.parent_task?.id && !knownIds.has(task.parent_task.id))
      ]

      const visit = (task, isChild) => {
        result.push({ task, isChild })
        if (expandedParents.value[task.id]) {
          const subs = tasksByParent.value[task.id] || []
          for (const sub of subs) {
            visit(sub, true)
          }
        }
      }

      for (const root of roots) {
        visit(root, false)
      }
      return result
    })
    const visibleTasksFiltered = computed(() => {
      const q = query.value.trim().toLowerCase()
      return visibleTasks.value.filter(item => {
        const task = item.task
        if (statusFilter.value !== 'all' && task.status !== statusFilter.value) return false
        if (projectFilter.value !== 'all') {
          if (projectFilter.value === 'none' && task.project) return false
          if (projectFilter.value !== 'none' && task.project?.id !== projectFilter.value) return false
        }
        if (!q) return true
        const hay = `${task.title || ''} ${task.description || ''}`.toLowerCase()
        return hay.includes(q)
      })
    })

    const taskPassesFilters = (task) => {
      if (statusFilter.value !== 'all' && task.status !== statusFilter.value) return false
      const q = query.value.trim().toLowerCase()
      if (!q) return true
      const hay = `${task.title || ''} ${task.description || ''}`.toLowerCase()
      return hay.includes(q)
    }

    const filteredSubtasksFor = (parentId) => {
      const subs = tasksByParent.value[parentId] || []
      return subs.filter(taskPassesFilters)
    }

    const groupedFilteredRows = computed(() => {
      const rows = visibleTasksFiltered.value
      const groups = []
      let i = 0
      while (i < rows.length) {
        const row = rows[i]
        if (!row.isChild) {
          const parentItem = row
          i++
          while (i < rows.length && rows[i].isChild) {
            i++
          }
          groups.push({ kind: 'block', parentItem })
        } else {
          groups.push({ kind: 'orphan', row })
          i++
        }
      }
      return groups
    })

    const blockKey = (block) =>
      block.kind === 'block' ? `b-${block.parentItem.task.id}` : `o-${block.row.task.id}`

    const groupedByProjectRows = computed(() => {
      const rows = visibleTasksFiltered.value.filter(item => !item.isChild)
      const projectsMap = {}
      const noProjectRows = []

      for (const item of rows) {
        if (item.task.project) {
          const pid = item.task.project.id
          if (!projectsMap[pid]) {
            projectsMap[pid] = {
              projectId: pid,
              project: item.task.project,
              tasks: []
            }
          }
          projectsMap[pid].tasks.push(item)
        } else {
          noProjectRows.push(item)
        }
      }

      const result = []
      // Personal tasks first
      if (noProjectRows.length > 0) {
        result.push({ kind: 'project-group', groupKey: 'personal', projectName: t('tasksList.groupPersonal'), projectId: null, tasks: noProjectRows })
      }
      // Then project groups sorted alphabetically
      const sortedProjects = Object.values(projectsMap).sort((a, b) =>
        (a.project.name || '').localeCompare(b.project.name || '')
      )
      for (const group of sortedProjects) {
        result.push({ kind: 'project-group', groupKey: `proj-${group.projectId}`, projectName: group.project.name, projectId: group.projectId, tasks: group.tasks })
      }
      return result
    })

    const isProjectExpanded = (projectId) => !!expandedProjects.value[projectId]
    const toggleProject = (projectId) => {
      expandedProjects.value = {
        ...expandedProjects.value,
        [projectId]: !expandedProjects.value[projectId]
      }
    }

    const monthLabel = computed(() => format(currentDate.value, 'LLLL yyyy', { locale: dateLocale.value }))
    const calendarDays = computed(() => {
      const startMonth = startOfMonth(currentDate.value)
      const endMonth = endOfMonth(currentDate.value)
      const startDate = startOfWeek(startMonth, { weekStartsOn: 1 })
      const days = []
      let day = startDate
      while (days.length < 42) {
        days.push(day)
        if (day > endMonth && days.length >= 35) break
        day = addDays(day, 1)
      }
      return days
    })
    const activeTasksCount = computed(() => tasks.value.filter(t => t.status === 'in_progress' || t.status === 'todo').length)
    const todayTasksCount = computed(() => tasks.value.filter(t => t.due_date && isSameDay(new Date(t.due_date), new Date())).length)
    const overdueTasksCount = computed(() => tasks.value.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== 'done').length)

    const fetchTimeEntries = async () => {
      try {
        const response = await api.getTimeEntries()
        timeEntries.value = response.data
      } catch (error) {
        console.error('Error fetching time entries:', error)
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
        toast.success(t('tasksList.timerStoppedLimit'))
        await fetchTimeEntries()
      }
    })

    const goToTaskDetail = (taskId) => {
      router.push(`/tasks/${taskId}/edit`)
    }

    const editTask = (taskId) => {
      const task = tasks.value.find(item => item.id === taskId)
      if (task && !task.can_edit) {
        toast.error(t('tasksList.viewOnlyEdit'))
        return
      }
      router.push(`/tasks/${taskId}/edit`)
    }

    const deleteTask = async (taskId) => {
      if (confirm(t('tasksList.deleteConfirm'))) {
        const task = tasks.value.find(item => item.id === taskId)
        if (task && !task.can_delete) {
          toast.error(t('tasksList.deleteDenied'))
          return
        }
        try {
          await api.deleteTask(taskId)
          toast.success(t('tasksList.deleteOk'))
          await fetchTasks()
        } catch (error) {
          toast.error(t('tasksList.deleteError'))
          console.error('Error deleting task:', error)
        }
      }
    }

    const stopTimeTracking = async (entryId) => {
      try {
        const cfg = loadCountdown()
        if (cfg && cfg.entryId === entryId) {
          clearStoredCountdown()
        }
        await api.stopTimeEntry(entryId)
        toast.success(t('tasksList.timerStopped'))
        await fetchTimeEntries()
      } catch (error) {
        toast.error(t('tasksList.timerStopError'))
        console.error('Error stopping time tracking:', error)
      }
    }

    const getActiveEntry = (taskId) => {
      return timeEntries.value.find(entry => entry.task?.id === taskId && !entry.end_time)
    }

    const countdownLabelForTask = (taskId) => {
      void tick.value
      const entry = getActiveEntry(taskId)
      if (!entry) return ''
      const sec = remainingSecondsForEntry(entry.id)
      if (sec == null) return ''
      return formatCountdown(sec)
    }

    const confirmStartTimer = async () => {
      const task = timerModalTask.value
      if (!task?.can_edit) return
      const mins = Number(timerModalMinutes.value)
      if (!Number.isFinite(mins) || mins < 0) {
        toast.error(t('tasksList.minutesNonNegative'))
        return
      }
      try {
        const { data } = await api.startTimeEntry(task.id, { description: t('tasksList.timer') })
        toast.success(t('tasksList.timerStarted'))
        if (mins > 0) {
          scheduleCountdown(data.id, mins, timerModalSound.value, timerModalAutoStop.value)
        } else {
          clearStoredCountdown()
        }
        timerModalOpen.value = false
        await fetchTimeEntries()
      } catch (error) {
        toast.error(t('tasksList.timerStartError'))
        console.error('Error starting time tracking:', error)
      }
    }

    const playTimerPreview = () => {
      playTimerExpirySound()
    }

    const getStatusText = (status) => {
      const key = `taskStatus.${status}`
      const translated = t(key)
      return translated !== key ? translated : status
    }

    const getStatusBadgeClass = (status) => {
      const statusMap = {
        'todo': 'soft-blue',
        'in_progress': 'soft-purple',
        'done': 'soft-green',
        'archived': 'soft-gray'
      }
      return statusMap[status] || 'soft-blue'
    }

    const getStatusChipClass = (status) => {
      const statusMap = {
        todo: 'chip-status-todo',
        in_progress: 'chip-status-progress',
        done: 'chip-status-done',
        archived: 'chip-status-archived'
      }
      return statusMap[status] || 'chip-status-todo'
    }

    const getPriorityChipClass = (priority) => {
      if (!priority || typeof priority.level !== 'number') return 'chip-priority-default'
      if (priority.level >= 4) return 'chip-priority-critical'
      if (priority.level === 3) return 'chip-priority-high'
      if (priority.level === 2) return 'chip-priority-medium'
      return 'chip-priority-low'
    }

    const getProjectChipClass = (projectId) => {
      const palette = ['chip-project-a', 'chip-project-b', 'chip-project-c', 'chip-project-d']
      if (!projectId) return palette[0]
      return palette[Math.abs(Number(projectId)) % palette.length]
    }

    const getCategoryChipClass = (categoryId) => {
      const palette = ['chip-category-a', 'chip-category-b', 'chip-category-c', 'chip-category-d']
      if (!categoryId) return palette[0]
      return palette[Math.abs(Number(categoryId)) % palette.length]
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return format(new Date(dateString), 'dd MMM yyyy, HH:mm', { locale: dateLocale.value })
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const getTimeTrackingIcon = (task) => {
      return getActiveEntry(task.id) ? 'fa-stop' : 'fa-play'
    }

    const hasSubtasks = (taskId) => {
      return (tasksByParent.value[taskId] || []).length > 0
    }

    const isExpanded = (taskId) => {
      return !!expandedParents.value[taskId]
    }

    const toggleSubtasks = (taskId) => {
      expandedParents.value = {
        ...expandedParents.value,
        [taskId]: !expandedParents.value[taskId]
      }
    }

    const getRowClass = (task) => {
      const map = {
        todo: 'row-todo',
        in_progress: 'row-progress',
        done: 'row-done',
        archived: 'row-archived'
      }
      return map[task.status] || 'row-todo'
    }

    const toggleTimeTracking = (task) => {
      const activeEntry = getActiveEntry(task.id)
      if (activeEntry) {
        stopTimeTracking(activeEntry.id)
        return
      }
      if (!task.can_edit) {
        toast.error(t('tasksList.viewOnlyTimer'))
        return
      }
      timerModalTask.value = task
      timerModalMinutes.value = 25
      timerModalSound.value = true
      timerModalAutoStop.value = false
      timerModalOpen.value = true
    }

    const setTaskScope = (scope) => {
      taskScope.value = scope
      fetchTasks()
    }

    const toggleFavorite = async (task) => {
      try {
        const { data } = await api.toggleTaskFavorite(task.id)
        if (taskScope.value === 'favorites' && !data.is_favorited) {
          await fetchTasks()
          return
        }
        task.is_favorited = data.is_favorited
      } catch (error) {
        toast.error(t('tasksList.favoriteError'))
        console.error('toggleFavorite', error)
      }
    }

    const quickStatusOptions = [
      { value: 'todo', label: t('taskStatus.todo'), icon: 'fas fa-clock' },
      { value: 'in_progress', label: t('taskStatus.in_progress'), icon: 'fas fa-spinner' },
      { value: 'done', label: t('taskStatus.done'), icon: 'fas fa-check-circle' },
    ]

    const getQuickChipClass = (status) => {
      const map = {
        todo: 'quick-chip-todo',
        in_progress: 'quick-chip-progress',
        done: 'quick-chip-done',
      }
      return map[status] || ''
    }

    const getStatusCount = (status) => {
      return tasks.value.filter(t => t.status === status).length || null
    }

    const toggleStatusFilter = (status) => {
      statusFilter.value = statusFilter.value === status ? 'all' : status
    }

    const hasActiveFilters = computed(() =>
      statusFilter.value !== 'all' || projectFilter.value !== 'all'
    )

    const clearAllFilters = () => {
      statusFilter.value = 'all'
      projectFilter.value = 'all'
      query.value = ''
    }

    const getProjectName = (projectId) => {
      const proj = projects.value.find(p => p.id === projectId)
      return proj ? proj.name : ''
    }

    const isCurrentMonth = (day) => isSameMonth(day, currentDate.value)
    const isToday = (day) => isSameDay(day, new Date())

    onMounted(() => {
      fetchTasks()
      fetchCategories()
      fetchPriorities()
      fetchProjects()
      fetchTimeEntries()
    })

    provide('taskListUi', {
      hasSubtasks,
      isExpanded,
      toggleSubtasks,
      getRowClass,
      goToTaskDetail,
      getStatusText,
      getStatusChipClass,
      getProjectChipClass,
      getCategoryChipClass,
      getPriorityChipClass,
      formatDate,
      truncateText,
      countdownLabelForTask,
      toggleFavorite,
      toggleTimeTracking,
      editTask,
      deleteTask,
      getTimeTrackingIcon,
      filteredSubtasksFor
    })

    return {
      tasks,
      categories,
      priorities,
      projects,
      timeEntries,
      loading,
      filteredTasks,
      visibleTasks,
      visibleTasksFiltered,
      groupedFilteredRows,
      groupMode,
      filteredSubtasksFor,
      blockKey,
      monthLabel,
      weekDays,
      calendarDays,
      activeTasksCount,
      todayTasksCount,
      overdueTasksCount,
      query,
      statusFilter,
      projectFilter,
      projectFilterValue: projectFilter,
      taskScope,
      setTaskScope,
      toggleFavorite,
      goToTaskDetail,
      editTask,
      deleteTask,
      timerModalOpen,
      timerModalTask,
      timerModalMinutes,
      timerModalSound,
      timerModalAutoStop,
      confirmStartTimer,
      playTimerPreview,
      countdownLabelForTask,
      getStatusText,
      getStatusChipClass,
      getPriorityChipClass,
      getProjectChipClass,
      getCategoryChipClass,
      getStatusBadgeClass,
      formatDate,
      truncateText,
      getTimeTrackingIcon,
      toggleTimeTracking,
      getRowClass,
      hasSubtasks,
      isExpanded,
      toggleSubtasks,
      isCurrentMonth,
      isToday,
      format,
      showAdvancedFilters,
      quickStatusOptions,
      getQuickChipClass,
      getStatusCount,
      toggleStatusFilter,
      hasActiveFilters,
      clearAllFilters,
      getProjectName,
      groupedByProjectRows,
      isProjectExpanded,
      toggleProject
    }
  }
}
</script>

<style scoped>
.tasks-page {
  max-width: 1260px;
  margin: 0 auto;
}

.tasks-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.tasks-actions {
  display: inline-flex;
  gap: 8px;
}

.tasks-toolbar .card-body {
  padding: 14px;
}

/* Primary toolbar row */
.toolbar-primary {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

/* Search box */
.search-box {
  flex: 1;
  min-width: 220px;
  position: relative;
}

.search-box i.fa-search {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #8b7697;
}

.search-box .form-control {
  padding-left: 36px;
  padding-right: 36px;
  outline: none;
}

.search-box .form-control:focus {
  border-color: rgba(176, 131, 200, 0.7);
  box-shadow: 0 0 0 3px rgba(176, 131, 200, 0.18);
}

.search-clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8b7697;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 0.85rem;
  line-height: 1;
}

.search-clear-btn:hover { color: #65567d; }

/* Scope pills */
.scope-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.scope-pill {
  border: 1px solid rgba(216, 196, 226, 0.8);
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  color: #65567d;
  padding: 7px 14px;
  font-size: 0.82rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.18s ease;
  outline: none;
}

.scope-pill:focus-visible {
  box-shadow: 0 0 0 2px rgba(176, 131, 200, 0.5);
}

.scope-pill:hover {
  background: rgba(246, 232, 245, 0.6);
  border-color: rgba(194, 170, 211, 0.9);
}

.scope-pill.active {
  background: linear-gradient(135deg, rgba(246, 232, 245, 0.96), rgba(241, 226, 247, 0.96));
  color: #3a4c78;
  border-color: rgba(194, 170, 211, 0.9);
  box-shadow: 0 2px 8px rgba(176, 131, 200, 0.2);
}

/* New task button */
.btn-new-task {
  flex-shrink: 0;
  border-radius: 999px;
  padding: 7px 18px;
  font-size: 0.85rem;
  box-shadow: 0 3px 10px rgba(102, 126, 234, 0.25);
}

/* Filter row */
.toolbar-filters-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed rgba(224, 206, 232, 0.55);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 0.78rem;
  color: #7a6991;
  font-weight: 600;
  white-space: nowrap;
}

/* Quick status chips */
.status-quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.quick-chip {
  border: 1px solid rgba(216, 196, 226, 0.8);
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  color: #65567d;
  padding: 5px 12px;
  font-size: 0.78rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.18s ease;
  line-height: 1.4;
  outline: none;
}

.quick-chip:focus-visible {
  box-shadow: 0 0 0 2px rgba(176, 131, 200, 0.5);
}

.quick-chip i { font-size: 0.75rem; }

.quick-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(136, 110, 149, 0.15);
}

.quick-chip.active {
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.quick-chip-todo.active { background: #ffe8f6; color: #9f3f7d; border-color: #ffc4e6; }
.quick-chip-progress.active { background: #efe7ff; color: #6846a8; border-color: #d4c1ff; }
.quick-chip-done.active { background: #e9f9ef; color: #2c8059; border-color: #bcebcf; }

.chip-count {
  background: rgba(0,0,0,0.08);
  border-radius: 999px;
  padding: 0 5px;
  font-size: 0.7rem;
  font-weight: 600;
}

.quick-chip.active .chip-count { background: rgba(0,0,0,0.1); }

/* Clear filters button */
.clear-filters-btn {
  font-size: 0.78rem;
  color: #a33745;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 184, 192, 0.7);
  background: #fff0f0;
  display: flex;
  align-items: center;
  transition: all 0.18s ease;
}

.clear-filters-btn:hover {
  background: #ffe0e4;
  border-color: rgba(255, 184, 192, 0.9);
}

.clear-filters-btn:focus-visible {
  outline: 2px solid rgba(255, 184, 192, 0.8);
  outline-offset: 2px;
}

/* Active filters bar */
.active-filters-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.active-filters-label {
  font-size: 0.78rem;
  color: #7a6991;
  font-weight: 600;
}

.active-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  background: linear-gradient(135deg, rgba(246, 232, 245, 0.96), rgba(241, 226, 247, 0.96));
  border: 1px solid rgba(194, 170, 211, 0.7);
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 0.78rem;
  color: #3a4c78;
}

.status-dot {
  font-size: 0.5rem;
}
.dot-todo { color: #ff6db8; }
.dot-in_progress { color: #9b7bff; }
.dot-done { color: #63c799; }

.active-chip-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: #7a6991;
  font-size: 0.7rem;
  padding: 0 1px;
  line-height: 1;
}

.active-chip-remove:hover { color: #a33745; }

.active-chip-remove:focus-visible {
  outline: 2px solid rgba(176, 131, 200, 0.5);
  outline-offset: 2px;
  border-radius: 3px;
}

/* Advanced toggle */
.advanced-toggle-row {
  margin-top: 8px;
}

.advanced-toggle-btn {
  background: none;
  border: none;
  color: #7a6991;
  font-size: 0.82rem;
  cursor: pointer;
  padding: 4px 0;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.18s ease;
}

.advanced-toggle-btn:hover,
.advanced-toggle-btn.active { color: #65567d; }

.advanced-toggle-btn:focus-visible {
  outline: 2px solid rgba(176, 131, 200, 0.5);
  outline-offset: 3px;
  border-radius: 4px;
}

.advanced-toggle-btn i.fa-chevron-down {
  transition: transform 0.25s ease;
}

.advanced-toggle-btn i.fa-chevron-down.rotate-180 {
  transform: rotate(180deg);
}

/* Advanced filters panel */
.advanced-filters-panel {
  margin-top: 10px;
  padding: 12px;
  background: rgba(248, 244, 252, 0.7);
  border-radius: 12px;
  border: 1px solid rgba(216, 196, 226, 0.55);
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.adv-filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.adv-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #7a6991;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.adv-filter-group .form-select {
  border-radius: 10px;
  font-size: 0.82rem;
  padding: 6px 28px 6px 10px;
  border-color: rgba(216, 196, 226, 0.8);
  background-color: rgba(255, 255, 255, 0.92);
  color: #65567d;
  height: auto;
  min-height: 0;
}

.adv-filter-group .form-select:focus {
  border-color: rgba(194, 170, 211, 0.95);
  box-shadow: 0 0 0 0.2rem rgba(176, 131, 200, 0.2);
  outline: none;
  color: #3a4c78;
}

.kpis {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #7a6991;
  font-size: 0.88rem;
}

.kpi { display: flex; align-items: center; gap: 4px; }
.kpi i { color: #9b7bff; font-size: 0.85rem; }
.kpi strong { color: #2f3f6d; }
.kpi-overdue { color: #b05c5c; }
.kpi-overdue i { color: #ff6b6b; }
.kpi-overdue strong { color: #a33737; }

.task-rows {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-block {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 0;
}

/* Плавное сворачивание блока подзадач (высота), без transition-group / FLIP */
.tasks-page :deep(.subtask-panel) {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.58s cubic-bezier(0.33, 1, 0.28, 1);
}

.tasks-page :deep(.subtask-panel--open) {
  grid-template-rows: 1fr;
}

.tasks-page :deep(.subtask-panel-inner) {
  overflow: hidden;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tasks-page :deep(.subtask-panel--nested) {
  margin-top: 0;
}

.tasks-page :deep(.task-row) {
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid rgba(227, 211, 236, 0.88);
  display: flex;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  transition: box-shadow 0.22s ease, transform 0.22s ease, background 0.22s ease;
  background: var(--card-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
}

.tasks-page :deep(.task-row:hover) {
  box-shadow: 0 14px 28px rgba(136, 110, 149, 0.22);
  transform: translateY(-4px);
}

.tasks-page :deep(.task-row:hover .task-actions) {
  opacity: 1;
}

.tasks-page :deep(.row-todo) { background: #fff9fd; border-left: 4px solid #ff6db8; }
.tasks-page :deep(.row-progress) { background: #f9f4ff; border-left: 4px solid #9b7bff; }
.tasks-page :deep(.row-done) { background: #f1fbf6; border-left: 4px solid #63c799; }
.tasks-page :deep(.row-archived) { background: #f7f4fb; border-left: 4px solid #bca8c9; }

.tasks-page :deep(.task-title) {
  margin: 0 0 2px 0;
  color: #2a2d4f;
}

.tasks-page :deep(.title-row) {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tasks-page :deep(.collapse-btn) {
  width: 24px;
  height: 24px;
  border: 1px solid rgba(193, 209, 238, 0.82);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  color: #35527c;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tasks-page :deep(.collapse-placeholder) {
  width: 24px;
  height: 24px;
  display: inline-block;
}

.tasks-page :deep(.task-sub) {
  margin: 0 0 7px 0;
  color: #7d7696;
  font-size: 0.9rem;
}

.tasks-page :deep(.chips) {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tasks-page :deep(.chip) {
  font-size: 0.74rem;
  border-radius: 999px;
  background: var(--surface-2);
  border: 1px solid var(--glass-border);
  padding: 2px 8px;
  color: #5b4e7f;
}

.tasks-page :deep(.chip.danger) {
  background: #ffe8ea;
  border-color: #ffb8c0;
  color: #a33745;
}

.tasks-page :deep(.chip-status-todo) {
  background: #ffe8f6;
  border-color: #ffc4e6;
  color: #9f3f7d;
}

.tasks-page :deep(.chip-status-progress) {
  background: #efe7ff;
  border-color: #d4c1ff;
  color: #6846a8;
}

.tasks-page :deep(.chip-status-done) {
  background: #e9f9ef;
  border-color: #bcebcf;
  color: #2c8059;
}

.tasks-page :deep(.chip-status-archived) {
  background: #f3eef8;
  border-color: #dbcee6;
  color: #705d86;
}

.tasks-page :deep(.chip-project-a) { background: #e8f1ff; border-color: #bbd4ff; color: #315f9d; }
.tasks-page :deep(.chip-project-b) { background: #eafbf4; border-color: #bcecd4; color: #2f7a5d; }
.tasks-page :deep(.chip-project-c) { background: #fff2e8; border-color: #f4cfb4; color: #9b6438; }
.tasks-page :deep(.chip-project-d) { background: #f2ecff; border-color: #d7c6ff; color: #6146a8; }

.tasks-page :deep(.chip-category-a) { background: #fff6de; border-color: #f3e1a8; color: #8d6a13; }
.tasks-page :deep(.chip-category-b) { background: #ffecec; border-color: #ffc8c8; color: #a14444; }
.tasks-page :deep(.chip-category-c) { background: #e8f7ff; border-color: #b8e5fa; color: #2f6f93; }
.tasks-page :deep(.chip-category-d) { background: #eef7ea; border-color: #cfe7c1; color: #4e7a3f; }

.tasks-page :deep(.chip-priority-low) {
  background: #e8f7ff;
  border-color: #bfe7ff;
  color: #256e99;
}

.tasks-page :deep(.chip-priority-medium) {
  background: #fff5e1;
  border-color: #ffe0a9;
  color: #9a6b12;
}

.tasks-page :deep(.chip-priority-high) {
  background: #ffe9d9;
  border-color: #ffc7a3;
  color: #b05b17;
}

.tasks-page :deep(.chip-priority-critical) {
  background: #ffe5ea;
  border-color: #ffb8c8;
  color: #ab2748;
}

.tasks-page :deep(.chip-priority-default) {
  background: #f3f0ff;
  border-color: #ddd4ff;
  color: #5f4da5;
}

.tasks-page :deep(.chip.muted) {
  color: #5f7398;
}

.tasks-page :deep(.chip.child) {
  background: rgba(220, 238, 255, 0.72);
  border-color: rgba(172, 206, 239, 0.82);
  color: #2f648f;
}

.tasks-page :deep(.chip-personal) {
  background: rgba(243, 240, 255, 0.95);
  border-color: rgba(190, 180, 230, 0.75);
  color: #5a4a8a;
}

.tasks-page :deep(.chip-collaborative) {
  background: linear-gradient(135deg, #e8f4ff, #f0f8ff);
  border-color: rgba(120, 170, 220, 0.55);
  color: #1d5a8a;
}

/* View toggle */
.view-toggle {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.view-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(216, 196, 226, 0.8);
  background: rgba(255, 255, 255, 0.92);
  color: #8b7697;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  transition: all 0.18s ease;
  outline: none;
}

.view-btn:focus-visible {
  box-shadow: 0 0 0 2px rgba(176, 131, 200, 0.5);
}

.view-btn:hover {
  background: rgba(246, 232, 245, 0.6);
  border-color: rgba(194, 170, 211, 0.9);
}

.view-btn.active {
  background: linear-gradient(135deg, rgba(246, 232, 245, 0.96), rgba(241, 226, 247, 0.96));
  color: #3a4c78;
  border-color: rgba(194, 170, 211, 0.9);
  box-shadow: 0 2px 8px rgba(176, 131, 200, 0.2);
}

/* Project groups */
.project-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.project-group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(246, 232, 245, 0.88), rgba(241, 226, 247, 0.88));
  border: 1px solid rgba(194, 170, 211, 0.7);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s ease;
  font-size: 0.9rem;
  color: #3a4c78;
  font-weight: 600;
  width: 100%;
  text-align: left;
  outline: none;
}

.project-group-header:focus-visible {
  box-shadow: 0 0 0 2px rgba(176, 131, 200, 0.5);
}

.project-group-header:hover {
  background: linear-gradient(135deg, rgba(246, 232, 245, 0.98), rgba(241, 226, 247, 0.98));
  box-shadow: 0 2px 8px rgba(176, 131, 200, 0.18);
}

.group-chevron {
  font-size: 0.7rem;
  color: #9b7bff;
  transition: transform 0.25s cubic-bezier(0.33, 1, 0.28, 1);
  width: 14px;
  text-align: center;
}

.group-chevron.is-open {
  transform: rotate(90deg);
}

.group-icon {
  color: #9b7bff;
  font-size: 0.85rem;
}

.group-name {
  flex: 1;
}

.group-count {
  background: rgba(155, 123, 255, 0.15);
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 0.72rem;
  color: #6846a8;
}

/* Project tasks panel (collapsible) */
.tasks-page :deep(.project-tasks-panel) {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.35s cubic-bezier(0.33, 1, 0.28, 1);
}

.tasks-page :deep(.project-tasks-panel.is-open) {
  grid-template-rows: 1fr;
}

.tasks-page :deep(.project-tasks-inner) {
  overflow: hidden;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 8px;
}

/* Make project tasks slightly different from flat rows */
.tasks-page :deep(.project-group .task-row) {
  border-left-width: 3px;
  margin-left: 8px;
}

.tasks-page :deep(.chip-coworkers) {
  background: rgba(232, 245, 255, 0.92);
  border-color: rgba(140, 190, 230, 0.65);
  color: #2d5f87;
  max-width: 100%;
}

.tasks-page :deep(.chip-timer-countdown) {
  background: rgba(255, 248, 230, 0.95);
  border-color: rgba(220, 180, 90, 0.55);
  color: #8a5f12;
}

.timer-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(40, 28, 52, 0.38);
  backdrop-filter: blur(4px);
}

.timer-modal {
  width: 100%;
  max-width: 420px;
  border-radius: 18px;
  border: 1px solid rgba(219, 199, 230, 0.85);
}

.tasks-page :deep(.icon-btn.star-btn.active) {
  color: #c9a227;
  border-color: rgba(212, 175, 55, 0.75);
  background: rgba(255, 248, 220, 0.95);
}

.tasks-page :deep(.task-actions) {
  margin-left: 28px;
  border: none;
  background: transparent;
}

.tasks-page :deep(.subtask-tree-node .task-row.is-child) {
  margin-left: calc(12px + var(--sub-depth, 1) * 16px);
  border-left: 3px dashed rgba(176, 131, 200, 0.55);
}

.tasks-page :deep(.icon-btn) {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  border: 1px solid var(--glass-border);
  background: var(--surface-1);
  color: #5f4b84;
  outline: none;
}

/* Dark theme overrides (эта страница задавала много "белого" вручную) */
:global([data-theme="dark"]) .tasks-page :deep(.task-row) {
  border-color: rgba(255, 255, 255, 0.09);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
}

:global([data-theme="dark"]) .tasks-page :deep(.task-title) {
  color: var(--text-primary);
}

:global([data-theme="dark"]) .tasks-page :deep(.task-sub) {
  color: var(--text-muted);
}

:global([data-theme="dark"]) .tasks-page :deep(.row-todo) {
  background:
    radial-gradient(circle at 18% 16%, rgba(102, 126, 234, 0.18), transparent 46%),
    linear-gradient(135deg, rgba(48, 48, 56, 0.92), rgba(30, 30, 36, 0.88));
}

:global([data-theme="dark"]) .tasks-page :deep(.row-progress) {
  background:
    radial-gradient(circle at 88% 10%, rgba(118, 75, 162, 0.18), transparent 52%),
    linear-gradient(135deg, rgba(48, 48, 56, 0.92), rgba(30, 30, 36, 0.88));
}

:global([data-theme="dark"]) .tasks-page :deep(.row-done) {
  background:
    radial-gradient(circle at 26% 92%, rgba(99, 179, 237, 0.14), transparent 48%),
    linear-gradient(135deg, rgba(48, 48, 56, 0.92), rgba(30, 30, 36, 0.88));
}

:global([data-theme="dark"]) .tasks-page :deep(.row-archived) {
  background:
    radial-gradient(circle at 60% 40%, rgba(120, 122, 130, 0.18), transparent 52%),
    linear-gradient(135deg, rgba(48, 48, 56, 0.92), rgba(30, 30, 36, 0.88));
}

:global([data-theme="dark"]) .tasks-page :deep(.collapse-btn) {
  border-color: rgba(255, 255, 255, 0.14);
  background: rgba(70, 70, 74, 0.5);
  color: var(--text-secondary);
}

:global([data-theme="dark"]) .tasks-page :deep(.chip) {
  color: var(--text-secondary);
}

:global([data-theme="dark"]) .tasks-page :deep(.icon-btn) {
  color: var(--text-secondary);
}

.tasks-page :deep(.icon-btn:focus-visible) {
  box-shadow: 0 0 0 2px rgba(176, 131, 200, 0.5);
}

.tasks-page :deep(.icon-btn.danger) {
  color: #b4364a;
}

.empty-state {
  text-align: center;
  color: #7f6a8e;
}

.soft-blue { background: #dce8ff; color: #244981; }
.soft-purple { background: #e9ddff; color: #4f3b82; }
.soft-green { background: #dff4df; color: #2f6d3a; }
.soft-gray { background: #eceff4; color: #4f5e77; }

@media (max-width: 992px) {
  .tasks-head {
    flex-direction: column;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tasks-page :deep(.subtask-panel) {
    transition: none;
  }
}

.tasks-page :deep(.collapse-chevron) {
  display: block;
  transform: rotate(0deg);
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.tasks-page :deep(.collapse-chevron.is-open) {
  transform: rotate(90deg);
}

</style>