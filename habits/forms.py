from django import forms
from .models import Habits, HabitsLog, HabitsNote, Workout, WorkoutLog


class HabitAddForm(forms.ModelForm):
    class Meta:
        model = Habits
        fields = ['title', 'description', 'purpose']
        labels = {
            'title': 'Название привычки',
            'description': 'Описание привычки(необязательно)',
            'purpose': 'Цель(дней)'
        }
        widget = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose': forms.IntegerField()
        }


class HabitLogForm(forms.Form):
    pass


class HabitNoteForm(forms.ModelForm):
    class Meta:
        model = HabitsNote
        fields = ['text']
        labels = {
            'text': 'Заметка'
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Добавить заметку...', 'class': 'form-control'})
        }


class WorkoutAddForm(forms.ModelForm):
    category_or_new = forms.CharField(label='Категория', widget=forms.TextInput(attrs={
        'list': 'category-list',
        'placeholder': 'Выбери или введи свою категорию'
    }))

    class Meta:
        model = Workout
        fields = ['title', 'description', 'category_or_new']
        labels = {
            'title': 'Название',
            'description': 'Описание тренировки(необязательно)'
        }


class WorkoutLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = ['date', 'duration_minutes', 'sets', 'reps_per_set','note']
        labels = {
            'date': 'Дата тренировки',
            'duration_minutes': 'Длительность тренировки',
            'sets': 'Количество подходов',
            'reps_per_set': 'Количество повторений в подходе',
            'note': 'Заметка'
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Добавить заметку...', 'class': 'form-control'})
        }