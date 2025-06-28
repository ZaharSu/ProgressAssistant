from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    photo = models.ImageField(upload_to='users/photos/%Y/%m/%d/', blank=True, null=True, verbose_name='Фотография')
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name='Дата рождения')


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    linked_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    token = models.CharField(max_length=100, blank=True, null=True)

    def str(self):
        return f"{self.telegram_id} ({self.username})"