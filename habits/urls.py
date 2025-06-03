from django.urls import path
from . import views

app_name = 'habits'


urlpatterns = [
    path('', views.HabitsView.as_view(), name='habits_view'),
    path('add/', views.HabitAdd.as_view(), name='habit_add'),
    path('<int:pk>/', views.HabitDetailView.as_view(), name='habit_detail'),
    path('<int:pk>/log/', views.HabitLogCreateView.as_view(), name='habit_log_create')
]