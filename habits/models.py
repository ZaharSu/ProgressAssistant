from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()

class Habits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    purpose = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def streak(self):
        return self.logs.count()

class HabitsLog(models.Model):
    habit = models.ForeignKey(Habits, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        return f'{self.habit.title} - {self.date}'


class HabitsNote(models.Model):
    log = models.ForeignKey(HabitsLog, on_delete=models.CASCADE, related_name='notes')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class WorkoutCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)

    class Meta:
        unique_together = ('title', 'user')

    def __str__(self):
        return self.title


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.ForeignKey(WorkoutCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class WorkoutLog(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    sets = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    reps_per_set = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.workout.title} - {self.date}'