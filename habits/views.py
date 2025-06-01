from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Habits
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import HabitAddForm

@method_decorator(login_required, name='dispatch')
class HabitsView(LoginRequiredMixin, ListView):
    model = Habits
    template_name = 'habits/habits_list.html'
    context_object_name = 'habits'

    def get_queryset(self):
        return Habits.objects.filter(user=self.request.user)


class HabitAdd(LoginRequiredMixin, CreateView):
    model = Habits
    form_class = HabitAddForm
    template_name = 'habits/habits_add.html'
    extra_context = {'title': 'Добавление привычки'}
    success_url = reverse_lazy('habits:habits_view')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)