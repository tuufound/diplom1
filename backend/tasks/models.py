from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_project_name_per_owner",
            )
        ]

    def __str__(self):
        return self.name


class ProjectMembership(models.Model):
    ROLE_OWNER = "owner"
    ROLE_EDITOR = "editor"
    ROLE_VIEWER = "viewer"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_EDITOR, "Editor"),
        (ROLE_VIEWER, "Viewer"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_user_membership_per_project",
            )
        ]

    def __str__(self):
        return f"{self.user.username} in {self.project.name} ({self.role})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=8, default="📁")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Priority(models.Model):
    name = models.CharField(max_length=50, unique=True)
    level = models.IntegerField(unique=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Priorities"
        ordering = ['level']

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='tasks')
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, blank=True, null=True, related_name='tasks')
    parent_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="subtasks",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TaskFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_favorites",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="user_favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "task"],
                name="unique_task_favorite_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user.username} ★ {self.task.title}"


class TaskCollaborator(models.Model):
    """Пользователь, приглашённый автором задачи для совместной работы."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="collaboratorships",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_collaborations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "user"],
                name="unique_task_collaborator",
            )
        ]

    def __str__(self):
        return f"{self.user.username} ↔ {self.task.title}"


class TimeEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Time Entry"
        verbose_name_plural = "Time Entries"
        ordering = ['-start_time']

    def duration(self):
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"Time entry for {self.task.title} by {self.user.username}"
