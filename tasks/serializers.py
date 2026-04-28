from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Priority, Task, TimeEntry


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


class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    priority = serializers.PrimaryKeyRelatedField(
        queryset=Priority.objects.all(), allow_null=True, required=False
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
            "category",
            "priority",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"] = (
            CategorySerializer(instance.category).data if instance.category else None
        )
        data["priority"] = (
            PrioritySerializer(instance.priority).data if instance.priority else None
        )
        return data


class TimeEntrySerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())
    user = UserSerializer(read_only=True)
    duration = serializers.SerializerMethodField()

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
        if request and value.user_id != request.user.id:
            raise serializers.ValidationError("Можно работать только со своими задачами.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["task"] = TaskSerializer(instance.task).data
        return data
