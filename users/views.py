from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from .models import TelegramUser
from config import settings
from .forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:register_done')

def register_done(request):
    return render(request, 'users/register_done.html')

class ProfileUser(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль пользователя'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['default_image'] = settings.DEFAULT_USER_IMAGE

        return context


class ProfileEdit(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile_edit.html'
    extra_context = {'title': 'Редактировать профиль',
                     'default_image':settings.DEFAULT_USER_IMAGE, }

    def get_success_url(self):
        return reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user



class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"


@login_required
def connect_telegram(request):
    token = request.GET.get('token')
    tg_user = TelegramUser.objects.get(token=token)
    tg_user.linked_user = request.user
    tg_user.save()
    messages.success(request, 'Аккаунт связан с Telegram!')
    return redirect('users:profile')