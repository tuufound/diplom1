from rest_framework import serializers
from .models import Task, Category, Priority, TimeEntry
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = ['id', 'name', 'level']

class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    priority = PrioritySerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'due_date', 'is_completed', 'user', 'category', 'priority']

class TimeEntrySerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TimeEntry
        fields = ['id', 'task', 'start_time', 'end_time', 'duration', 'description']