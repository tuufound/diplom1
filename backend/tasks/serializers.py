from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Priority, Project, ProjectMembership, Task, TimeEntry


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description")


class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ("id", "name", "level", "color")


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
    )

    class Meta:
        model = ProjectMembership
        fields = ("id", "user", "user_id", "role", "created_at")
        read_only_fields = ("id", "created_at", "user")


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    memberships = ProjectMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "memberships",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("owner", "memberships", "created_at", "updated_at")


class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    access_role = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        allow_null=True,
        required=False,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    priority = serializers.PrimaryKeyRelatedField(
        queryset=Priority.objects.all(), allow_null=True, required=False
    )
    parent_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "updated_at",
            "due_date",
            "completed_at",
            "is_active",
            "user",
            "access_role",
            "can_edit",
            "project",
            "category",
            "priority",
            "parent_task",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = (
            CategorySerializer(instance.category).data if instance.category else None
        )
        data["project"] = (
            ProjectSerializer(instance.project).data if instance.project else None
        )
        data["priority"] = (
            PrioritySerializer(instance.priority).data if instance.priority else None
        )
        data["parent_task"] = (
            {"id": instance.parent_task.id, "title": instance.parent_task.title}
            if instance.parent_task
            else None
        )
        return data

    def validate_parent_task(self, value):
        request = self.context.get("request")
        if not value or not request:
            return value

        if value.user_id == request.user.id:
            return value

        membership = ProjectMembership.objects.filter(
            project=value.project,
            user=request.user,
        ).first()
        if not membership:
            raise serializers.ValidationError("Нет доступа к родительской задаче.")
        return value

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        parent_task = attrs.get("parent_task")
        if parent_task is None and instance:
            parent_task = instance.parent_task

        if instance and parent_task and parent_task.id == instance.id:
            raise serializers.ValidationError(
                {"parent_task": "Задача не может быть родительской сама себе."}
            )

        if instance and parent_task:
            current_parent = parent_task
            while current_parent:
                if current_parent.id == instance.id:
                    raise serializers.ValidationError(
                        {"parent_task": "Нельзя создавать циклическую иерархию задач."}
                    )
                current_parent = current_parent.parent_task

        project = attrs.get("project")
        if project is None and instance:
            project = instance.project

        if parent_task and parent_task.project_id != (project.id if project else None):
            raise serializers.ValidationError(
                {
                    "parent_task": "Родительская задача должна быть из того же проекта или личного списка."
                }
            )

        return attrs

    def get_access_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if obj.user_id == request.user.id:
            return "owner"
        if not obj.project_id:
            return None
        membership = ProjectMembership.objects.filter(
            project=obj.project,
            user=request.user,
        ).first()
        return membership.role if membership else None

    def get_can_edit(self, obj):
        return self.get_access_role(obj) in {"owner", "editor"}


class TimeEntrySerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    user = UserSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = (
            "id",
            "task",
            "user",
            "start_time",
            "end_time",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "duration",
            "can_edit",
        )
        read_only_fields = ("is_active",)

    def get_duration(self, obj):
        duration = obj.duration()
        if not duration:
            return None
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def validate_task(self, value):
        request = self.context.get("request")
        if not request:
            return value
        if value.user_id == request.user.id:
            return value
        membership = ProjectMembership.objects.filter(
            project=value.project,
            user=request.user,
        ).first()
        if not membership:
            raise serializers.ValidationError("Нет доступа к выбранной задаче.")
        return value

    def get_can_edit(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if obj.user_id != request.user.id:
            return False
        task = obj.task
        if task.user_id == request.user.id:
            return True
        membership = ProjectMembership.objects.filter(
            project=task.project,
            user=request.user,
        ).first()
        return bool(membership and membership.role in {"owner", "editor"})

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["task"] = TaskSerializer(instance.task).data
        return data
