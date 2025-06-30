from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Workout, WorkoutCategory

@receiver(post_delete, sender=Workout)
def delete_empty_category(sender, instance, **kwargs):
    category = instance.category
    if category and not Workout.objects.filter(category=category, user=instance.user).exists():
        category.delete()