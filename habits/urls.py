from django.urls import path
from . import views

app_name = 'habits'


urlpatterns = [
    path('', views.HabitsView.as_view(), name='habits_view'),
    path('habit_add/', views.HabitAdd.as_view(), name='habit_add'),
    path('habit/<int:pk>/', views.HabitDetailView.as_view(), name='habit_detail'),
    path('<int:pk>/edit/', views.HabitUpdateView.as_view(), name='habit_edit'),
    path('<int:pk>/delete/', views.HabitDeleteView.as_view(), name='habit_delete'),
    path('<int:pk>/log/', views.HabitLogCreateView.as_view(), name='habit_log_create'),
    path('workouts/', views.WorkoutView.as_view(), name='workouts_view'),
    path('workout_add/', views.WorkoutAdd.as_view(), name='workout_add'),
    path('workout/<int:pk>/', views.WorkoutDetailView.as_view(), name='workout_detail')
]