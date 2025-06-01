from django import forms
from .models import Habits

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