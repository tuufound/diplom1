from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CategoryListCreateView,
    CurrentUserView,
    LoginView,
    PriorityListCreateView,
    RegisterView,
    ReportView,
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    TimeEntryListCreateView,
    TimeEntryRetrieveUpdateDestroyView,
    TimeEntryStartView,
    TimeEntryStopView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/user/", CurrentUserView.as_view(), name="current_user"),
    path("categories/", CategoryListCreateView.as_view(), name="category_list_create"),
    path("priorities/", PriorityListCreateView.as_view(), name="priority_list_create"),
    path("tasks/", TaskListCreateView.as_view(), name="task_list_create"),
    path(
        "tasks/<int:pk>/",
        TaskRetrieveUpdateDestroyView.as_view(),
        name="task_detail",
    ),
    path("time-entries/", TimeEntryListCreateView.as_view(), name="time_entry_list_create"),
    path(
        "time-entries/<int:pk>/",
        TimeEntryRetrieveUpdateDestroyView.as_view(),
        name="time_entry_detail",
    ),
    path("tasks/<int:task_id>/start/", TimeEntryStartView.as_view(), name="time_entry_start"),
    path(
        "time-entries/<int:time_entry_id>/stop/",
        TimeEntryStopView.as_view(),
        name="time_entry_stop",
    ),
    path("reports/", ReportView.as_view(), name="reports"),
]
