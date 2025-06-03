from django import forms
from .models import Habits, HabitsLog, HabitsNote


class HabitAddForm(forms.ModelForm):
    class Meta:
        model = Habits
        fields = ['title', 'description', 'purpose']
        labels = {
            'title': 'Название привычки',
            'description': 'Описание привычки',
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