from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from .models import Habits
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class HabitsView(LoginRequiredMixin, ListView):
    model = Habits
    template_name = 'habits/habits_list.html'
    context_object_name = 'habits'

    def get_queryset(self):
        return Habits.objects.filter(user=self.request.user)


