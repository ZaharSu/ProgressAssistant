from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

class Habits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class HabitsLog(models.Model):
    habit = models.ForeignKey(Habits, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f'{self.habit.title} - {self.date}'



class WorkoutCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.ForeignKey(WorkoutCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True)
    sets = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True)
    reps_per_set = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('workout', 'date')

    def __str__(self):
        return f'{self.workout.title} - {self.date}'