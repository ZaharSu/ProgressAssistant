from django.contrib import admin
from .models import Habits, WorkoutCategory, Workout

@admin.register(Habits)
class HabitsAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category')


@admin.register(WorkoutCategory)
class WorkoutCategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')