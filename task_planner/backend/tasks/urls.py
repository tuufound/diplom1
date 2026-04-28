from django.urls import path
from .views import (
    UserCreate,
    CategoryListCreate,
    PriorityListCreate,
    TaskListCreate,
    TaskRetrieveUpdateDestroy,
    TimeEntryListCreate,
    TimeEntryRetrieveUpdateDestroy,
    StartTimeEntry,
    StopTimeEntry
)

urlpatterns = [
    path('auth/register/', UserCreate.as_view(), name='user-create'),
    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('priorities/', PriorityListCreate.as_view(), name='priority-list-create'),
    path('tasks/', TaskListCreate.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroy.as_view(), name='task-retrieve-update-destroy'),
    path('time-entries/', TimeEntryListCreate.as_view(), name='time-entry-list-create'),
    path('time-entries/<int:pk>/', TimeEntryRetrieveUpdateDestroy.as_view(), name='time-entry-retrieve-update-destroy'),
    path('tasks/<int:task_id>/start/', StartTimeEntry.as_view(), name='start-time-entry'),
    path('time-entries/<int:time_entry_id>/stop/', StopTimeEntry.as_view(), name='stop-time-entry'),
]