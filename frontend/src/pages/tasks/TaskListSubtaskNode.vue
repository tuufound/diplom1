<template>
  <div class="subtask-tree-node" :style="{ '--sub-depth': depth }">
    <article
      class="task-row is-child"
      :class="ui.getRowClass(task)"
      @click="ui.goToTaskDetail(task.id)"
    >
      <div class="task-main">
        <div class="title-row">
          <button
            v-if="ui.hasSubtasks(task.id)"
            class="collapse-btn"
            type="button"
            :aria-expanded="ui.isExpanded(task.id)"
            @click.stop="ui.toggleSubtasks(task.id)"
          >
            <i class="fas fa-chevron-right collapse-chevron" :class="{ 'is-open': ui.isExpanded(task.id) }"></i>
          </button>
          <span v-else class="collapse-placeholder"></span>
          <h6 class="task-title">{{ task.title }}</h6>
        </div>
        <p v-if="task.description" class="task-sub">{{ ui.truncateText(task.description, 110) }}</p>
        <div class="chips">
          <span class="chip" :class="ui.getStatusChipClass(task.status)">{{ ui.getStatusText(task.status) }}</span>
          <span class="chip muted">{{ ui.formatDate(task.created_at) }}</span>
          <span v-if="!task.project" class="chip chip-personal">{{ $t('tasksList.personal') }}</span>
          <span v-if="task.project" class="chip chip-collaborative">{{ $t('tasksList.collaborativeChip') }}</span>
          <span v-if="task.project" class="chip" :class="ui.getProjectChipClass(task.project?.id)">{{ task.project.name }}</span>
          <span v-if="task.category" class="chip" :class="ui.getCategoryChipClass(task.category?.id)">
            <span class="me-1">{{ task.category.icon || '📁' }}</span>{{ task.category.name }}
          </span>
          <span v-if="task.priority" class="chip" :class="ui.getPriorityChipClass(task.priority)">{{ task.priority.name }}</span>
          <span class="chip child">{{ $t('tasksList.subtaskChip') }}</span>
          <span v-if="task.collaborators?.length" class="chip chip-coworkers">
            <i class="fas fa-users me-1"></i>{{ task.collaborators.map((u) => u.username).join(', ') }}
          </span>
          <span v-if="ui.countdownLabelForTask(task.id)" class="chip chip-timer-countdown">
            <i class="fas fa-bell me-1"></i>{{ $t('tasksList.countdownBell') }} {{ ui.countdownLabelForTask(task.id) }}
          </span>
        </div>
      </div>
      <div class="task-actions">
        <button
          class="icon-btn star-btn"
          :class="{ active: task.is_favorited }"
          type="button"
          @click.stop="ui.toggleFavorite(task)"
          :title="$t('tasksList.favorite')"
        >
          <i class="fas fa-star"></i>
        </button>
        <button
          class="icon-btn"
          @click.stop="ui.toggleTimeTracking(task)"
          :disabled="!task.can_edit"
          :title="$t('tasksList.timer')"
        >
          <i class="fas" :class="ui.getTimeTrackingIcon(task)"></i>
        </button>
        <button
          class="icon-btn"
          @click.stop="ui.editTask(task.id)"
          :disabled="!task.can_edit"
          :title="$t('common.edit')"
        >
          <i class="fas fa-pen"></i>
        </button>
        <button
          class="icon-btn danger"
          @click.stop="ui.deleteTask(task.id)"
          :disabled="!task.can_delete"
          :title="$t('common.delete')"
        >
          <i class="fas fa-trash"></i>
        </button>
        <router-link class="icon-btn" :to="`/tasks/create?parent=${task.id}`" :title="$t('tasksList.subtask')">
          <i class="fas fa-folder"></i>
        </router-link>
      </div>
    </article>
    <div
      v-if="ui.hasSubtasks(task.id)"
      class="subtask-panel subtask-panel--nested"
      :class="{ 'subtask-panel--open': ui.isExpanded(task.id) }"
      :aria-hidden="!ui.isExpanded(task.id)"
    >
      <div class="subtask-panel-inner">
        <TaskListSubtaskNode
          v-for="st in ui.filteredSubtasksFor(task.id)"
          :key="st.id"
          :task="st"
          :depth="depth + 1"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskListSubtaskNode',
  inject: ['taskListUi'],
  props: {
    task: { type: Object, required: true },
    depth: { type: Number, default: 1 }
  },
  computed: {
    ui() {
      return this.taskListUi
    }
  }
}
</script>
