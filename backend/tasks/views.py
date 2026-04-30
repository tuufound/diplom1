from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Priority, Project, ProjectMembership, Task, TimeEntry
from .serializers import (
    CategorySerializer,
    PrioritySerializer,
    ProjectMembershipSerializer,
    ProjectSerializer,
    RegisterSerializer,
    TaskSerializer,
    TimeEntrySerializer,
    UserSerializer,
)


def get_task_role(task, user):
    if task.user_id == user.id:
        return "owner"
    if not task.project_id:
        return None
    membership = ProjectMembership.objects.filter(project=task.project, user=user).first()
    return membership.role if membership else None


def can_edit_task(task, user):
    return get_task_role(task, user) in {"owner", "editor"}


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Неверные учетные данные."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip().lower()
        new_password = request.data.get("new_password", "")

        if not username or not email or not new_password:
            return Response(
                {"detail": "Укажите username, email и новый пароль."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username, email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Пользователь с такими данными не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"detail": "Пароль успешно обновлен."})


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PriorityListCreateView(generics.ListCreateAPIView):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(memberships__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ProjectMembership.objects.get_or_create(
            project=project,
            user=self.request.user,
            defaults={"role": ProjectMembership.ROLE_OWNER},
        )


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(
            Q(owner=self.request.user) | Q(memberships__user=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        project = self.get_object()
        membership = ProjectMembership.objects.filter(
            project=project,
            user=self.request.user,
        ).first()
        role = membership.role if membership else None
        if project.owner_id != self.request.user.id and role not in {
            ProjectMembership.ROLE_OWNER,
            ProjectMembership.ROLE_EDITOR,
        }:
            raise PermissionDenied("Недостаточно прав для изменения проекта.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner_id != self.request.user.id:
            raise PermissionDenied("Удалять проект может только владелец.")
        instance.delete()


class ProjectMembershipCreateView(generics.CreateAPIView):
    serializer_class = ProjectMembershipSerializer

    def perform_create(self, serializer):
        project = generics.get_object_or_404(Project, id=self.kwargs["project_id"])
        if project.owner_id != self.request.user.id:
            raise PermissionDenied("Добавлять участников может только владелец.")
        serializer.save(project=project)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(
            Q(user=self.request.user) | Q(project__memberships__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")
        if project:
            membership = ProjectMembership.objects.filter(
                project=project,
                user=self.request.user,
            ).first()
            role = membership.role if membership else None
            if project.owner_id != self.request.user.id and role not in {
                ProjectMembership.ROLE_OWNER,
                ProjectMembership.ROLE_EDITOR,
            }:
                raise PermissionDenied("Нет прав для создания задачи в этом проекте.")
        serializer.save(user=self.request.user)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(
            Q(user=self.request.user) | Q(project__memberships__user=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        task = self.get_object()
        if not can_edit_task(task, self.request.user):
            raise PermissionDenied("Недостаточно прав для редактирования задачи.")
        serializer.save()

    def perform_destroy(self, instance):
        if not can_edit_task(instance, self.request.user):
            raise PermissionDenied("Недостаточно прав для удаления задачи.")
        instance.delete()


class TimeEntryListCreateView(generics.ListCreateAPIView):
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        return TimeEntry.objects.filter(
            Q(user=self.request.user)
            | Q(task__project__memberships__user=self.request.user)
            | Q(task__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        task = serializer.validated_data["task"]
        if not can_edit_task(task, self.request.user):
            raise PermissionDenied("Только owner/editor может добавлять время.")
        end_time = serializer.validated_data.get("end_time")
        serializer.save(user=self.request.user, is_active=end_time is None)


class TimeEntryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeEntrySerializer

    def get_queryset(self):
        return TimeEntry.objects.filter(
            Q(user=self.request.user)
            | Q(task__project__memberships__user=self.request.user)
            | Q(task__user=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        entry = self.get_object()
        if entry.user_id != self.request.user.id:
            raise PermissionDenied("Изменять запись может только автор.")
        if not can_edit_task(entry.task, self.request.user):
            raise PermissionDenied("Недостаточно прав для изменения записи.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied("Удалять запись может только автор.")
        if not can_edit_task(instance.task, self.request.user):
            raise PermissionDenied("Недостаточно прав для удаления записи.")
        instance.delete()


class TimeEntryStartView(APIView):
    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"detail": "Задача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_edit_task(task, request.user):
            raise PermissionDenied("Только owner/editor может запускать таймер.")

        active_entry = TimeEntry.objects.filter(
            user=request.user, task=task, end_time__isnull=True, is_active=True
        ).first()
        if active_entry:
            return Response(
                {"detail": "Для этой задачи уже запущен активный таймер."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry = TimeEntry.objects.create(
            user=request.user,
            task=task,
            start_time=timezone.now(),
            description=request.data.get("description", ""),
            is_active=True,
        )
        return Response(TimeEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


class TimeEntryStopView(APIView):
    def post(self, request, time_entry_id):
        try:
            entry = TimeEntry.objects.get(id=time_entry_id)
        except TimeEntry.DoesNotExist:
            return Response(
                {"detail": "Запись времени не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if entry.user_id != request.user.id:
            raise PermissionDenied("Останавливать таймер может только автор.")
        if not can_edit_task(entry.task, request.user):
            raise PermissionDenied("Недостаточно прав для остановки таймера.")

        if entry.end_time:
            return Response(
                {"detail": "Таймер уже остановлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry.end_time = timezone.now()
        entry.is_active = False
        entry.save(update_fields=["end_time", "is_active", "updated_at"])
        return Response(TimeEntrySerializer(entry).data)


class ReportView(APIView):
    def get(self, request):
        tasks = Task.objects.filter(
            Q(user=request.user) | Q(project__memberships__user=request.user)
        ).distinct()
        entries = TimeEntry.objects.filter(
            Q(user=request.user)
            | Q(task__project__memberships__user=request.user)
            | Q(task__user=request.user)
        ).distinct()

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            entries = entries.filter(start_time__date__gte=start_date)
            tasks = tasks.filter(created_at__date__gte=start_date)
        if end_date:
            entries = entries.filter(start_time__date__lte=end_date)
            tasks = tasks.filter(created_at__date__lte=end_date)

        status_stats = dict(
            tasks.values("status")
            .annotate(total=Count("id"))
            .values_list("status", "total")
        )
        priority_stats = dict(
            tasks.exclude(priority__isnull=True)
            .values("priority__name")
            .annotate(total=Count("id"))
            .values_list("priority__name", "total")
        )
        daily_time = list(
            entries.exclude(end_time__isnull=True)
            .annotate(day=TruncDate("start_time"))
            .values("day")
            .annotate(total_entries=Count("id"))
            .order_by("day")
        )

        completed_entries = entries.exclude(end_time__isnull=True).select_related("task")
        task_time_seconds = {}
        weekday_time_seconds = {i: 0 for i in range(7)}

        for entry in completed_entries:
            duration_seconds = int((entry.end_time - entry.start_time).total_seconds())
            if duration_seconds <= 0:
                continue
            task_id = entry.task_id
            if task_id not in task_time_seconds:
                task_time_seconds[task_id] = {
                    "task_id": task_id,
                    "task_title": entry.task.title,
                    "seconds": 0,
                }
            task_time_seconds[task_id]["seconds"] += duration_seconds

            weekday = timezone.localtime(entry.start_time).weekday()
            weekday_time_seconds[weekday] += duration_seconds

        top_time_tasks = sorted(
            task_time_seconds.values(), key=lambda item: item["seconds"], reverse=True
        )[:10]

        weekday_labels = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
        productivity_by_weekday = [
            {
                "weekday": weekday_labels[idx],
                "seconds": weekday_time_seconds[idx],
            }
            for idx in range(7)
        ]

        completed_tasks = tasks.filter(status="done").exclude(completed_at__isnull=True)
        avg_completion_seconds = None
        if completed_tasks.exists():
            total_completion_seconds = 0
            valid_count = 0
            for task in completed_tasks:
                if task.completed_at and task.created_at and task.completed_at > task.created_at:
                    total_completion_seconds += int(
                        (task.completed_at - task.created_at).total_seconds()
                    )
                    valid_count += 1
            if valid_count:
                avg_completion_seconds = total_completion_seconds // valid_count

        total_tracked_seconds = sum(item["seconds"] for item in task_time_seconds.values())

        return Response(
            {
                "total_tasks": tasks.count(),
                "completed_tasks": tasks.filter(status="done").count(),
                "active_timers": entries.filter(end_time__isnull=True).count(),
                "status_stats": status_stats,
                "priority_stats": priority_stats,
                "daily_time_entries": daily_time,
                "total_tracked_seconds": total_tracked_seconds,
                "top_time_tasks": top_time_tasks,
                "productivity_by_weekday": productivity_by_weekday,
                "avg_completion_seconds": avg_completion_seconds,
            }
        )
