from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView
from .models import Habits, HabitsLog, HabitsNote
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import HabitAddForm, HabitLogForm, HabitNoteForm

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


class HabitDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        habit = get_object_or_404(Habits, pk=pk, user=request.user)
        today = timezone.now().date()
        log = HabitsLog.objects.filter(habit=habit, date=today, user=request.user).first()
        note_form = HabitNoteForm()
        notes = HabitsNote.objects.filter(log__habit=habit).order_by('-created_at')
        log_count = HabitsLog.objects.filter(habit=habit, user=request.user).count()
        context = {
            'habit': habit,
            'log': log,
            'note_form': note_form,
            'log_count': log_count,
            'notes': notes
        }
        return render(request, 'habits/habit_detail.html', context)

    def post(self, request, pk):
        habit = get_object_or_404(Habits, pk=pk, user=request.user)
        today = timezone.now().date()
        log = HabitsLog.objects.filter(habit=habit, date=today, user=request.user).first()
        if not log:
            messages.warning(request, 'Сначала отметьте выполнение привычки!')
            return redirect('habits:habit_detail', pk=habit.pk)

        form = HabitNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.log = log
            note.save()
            messages.success(request, 'Заметка добавлена!')
        else:
            messages.error(request, 'Не удалось сохранить заметку!')

        return redirect('habits:habit_detail', pk=habit.pk)


class HabitLogCreateView(View):

    def post(self, request, pk):
        habit=get_object_or_404(Habits, pk=pk, user=request.user)
        today = timezone.now().date()
        if HabitsLog.objects.filter(habit=habit, date=today).exists():
            messages.warning(request, 'Вы уже отметили эту привычку сегодня!')
        else:
            form = HabitLogForm(request.POST)
            if form.is_valid():
                HabitsLog.objects.create(user=request.user,
                                         habit=habit,
                                         date=timezone.now().date()
                                         )
            messages.success(request, 'Выполнение привычки отмечено!')


        return redirect('habits:habit_detail', pk=habit.pk)