from rest_framework import generics, permissions
from .models import Task, Category, Priority, TimeEntry
from .serializers import TaskSerializer, CategorySerializer, PrioritySerializer, TimeEntrySerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone

class UserCreate(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class PriorityListCreate(generics.ListCreateAPIView):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = [permissions.IsAuthenticated]

class TaskListCreate(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class TimeEntryListCreate(generics.ListCreateAPIView):
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TimeEntry.objects.filter(task__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

class TimeEntryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TimeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TimeEntry.objects.filter(task__user=self.request.user)

class StartTimeEntry(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id, format=None):
        try:
            task = Task.objects.get(id=task_id, user=request.user)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        time_entry = TimeEntry.objects.create(
            task=task,
            start_time=timezone.now(),
            description=request.data.get('description', '')
        )
        return Response(TimeEntrySerializer(time_entry).data, status=status.HTTP_201_CREATED)

class StopTimeEntry(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, time_entry_id, format=None):
        try:
            time_entry = TimeEntry.objects.get(id=time_entry_id, task__user=request.user)
        except TimeEntry.DoesNotExist:
            return Response({'error': 'Time entry not found'}, status=status.HTTP_404_NOT_FOUND)

        time_entry.end_time = timezone.now()
        time_entry.duration = timezone.now() - time_entry.start_time
        time_entry.save()
        return Response(TimeEntrySerializer(time_entry).data, status=status.HTTP_200_OK)