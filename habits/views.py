from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from .models import Habits, HabitsLog, HabitsNote, Workout, WorkoutCategory, WorkoutLog
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import HabitAddForm, HabitLogForm, HabitNoteForm, WorkoutAddForm, WorkoutLogForm


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
        response = super().form_valid(form)

        if self.request.POST.get('submit_type') == 'add_and_log':
            HabitsLog.objects.create(user=self.request.user,
                                     habit=self.object,
                                     date=timezone.now().date())

            return redirect('habits:habit_detail', pk=self.object.pk)

        return response


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


class HabitUpdateView(LoginRequiredMixin, UpdateView):
    model = Habits
    form_class = HabitAddForm
    template_name = 'habits/habit_edit.html'

    def get_queryset(self):
        return Habits.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['habit'] = self.get_object()
        return context

    def get_success_url(self):
        return reverse_lazy('habits:habit_detail', kwargs={'pk': self.object.pk})



class HabitDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        habit = get_object_or_404(Habits, pk=pk, user=request.user)
        habit.delete()
        messages.success(request, 'Привычка успешно удалена!')
        return redirect('habits:habits_view')


class WorkoutView(LoginRequiredMixin, ListView):
    model = Workout
    template_name = 'workouts/workouts_list.html'
    context_object_name = 'workouts'

    def get_queryset(self):
        user = self.request.user
        queryset = Workout.objects.filter(user=user)
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['categories'] = WorkoutCategory.objects.filter(Q(user=user), workout__user=user).distinct()
        context['selected_category'] = self.request.GET.get('category')
        workouts = context['workouts']
        workout_data = []
        for workout in workouts:
            logs = workout.logs.order_by('-date')
            last_log = logs.first()
            workout_data.append({
                'workout': workout,
                'total_logs': logs.count(),
                'last_date': last_log.date if last_log else None,
                'duration': last_log.duration_minutes if last_log else None,
            })
        context['workout_data'] = workout_data
        return context


class WorkoutAdd(LoginRequiredMixin, CreateView):
    model = Workout
    form_class = WorkoutAddForm
    template_name = 'workouts/workout_add.html'
    success_url = reverse_lazy('habits:workouts_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = WorkoutCategory.objects.filter(Q(user__isnull=True))
        return context

    def form_valid(self, form):
        category_name = form.cleaned_data['category_or_new']

        category, created = WorkoutCategory.objects.get_or_create(title=category_name, user=self.request.user)

        self.objects = form.save(commit=False)
        self.objects.category = category
        self.objects.user = self.request.user
        self.objects.save()
        return redirect(self.success_url)


class WorkoutDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk, user=request.user)
        logs = WorkoutLog.objects.filter(workout=workout).order_by('-date')
        form = WorkoutLogForm()
        context = {
            'workout': workout,
            'logs': logs,
            'form': form
        }
        return render(request, 'workouts/workout_detail.html', context)

    def post(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk, user=request.user)
        form = WorkoutLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.workout = workout
            if not log.date:
                log.date = timezone.now().date()
            log.save()
            messages.success(request, 'Запись добавлена!')
        else:
            logs = WorkoutLog.objects.filter(workout=workout).order_by('-date')
            context = {
            'workout': workout,
            'logs': logs,
            'form': form
            }
            messages.warning(request, 'Ошибка при отметке выполнения. Возможно вы заполнили не все необходимые поля!')
            return render(request, 'workouts/workout_detail.html', context)

        return redirect('habits:workout_detail', pk=workout.pk)


class WorkoutUpdateView(LoginRequiredMixin, UpdateView):
    model = Workout
    form_class = WorkoutAddForm
    template_name = 'workouts/workout_edit.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workout'] = self.get_object()
        return context

    def form_valid(self, form):
        category_title = form.cleaned_data['category_or_new']
        category, created = WorkoutCategory.objects.get_or_create(title=category_title, user=self.request.user)
        form.instance.category = category
        form.instance.user = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('habits:workout_detail', kwargs={'pk': self.object.pk})


class WorkoutDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk, user=request.user)
        workout.delete()
        messages.success(request, 'Тренировка успешно удалена!')
        return redirect('habits:workouts_view')