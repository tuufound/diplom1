from django.contrib import admin

from .models import (
    Category,
    Priority,
    Project,
    ProjectMembership,
    Task,
    TaskCollaborator,
    TaskFavorite,
    TimeEntry,
)

admin.site.register(Category)
admin.site.register(Priority)
admin.site.register(Project)
admin.site.register(ProjectMembership)
admin.site.register(Task)
admin.site.register(TaskFavorite)
admin.site.register(TaskCollaborator)
admin.site.register(TimeEntry)
