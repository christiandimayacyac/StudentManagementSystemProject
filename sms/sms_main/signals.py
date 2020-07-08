from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUserProfile, AdminHOD, Staff, Student


@receiver(post_save, sender=CustomUserProfile)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_level == 1:
            AdminHOD.objects.create(user_profile=instance)
        if instance.user_level == 2:
            Staff.objects.create(user_profile=instance)
        if instance.user_level == 3:
            Student.objects.create(user_profile=instance)


@receiver(post_save, sender=CustomUserProfile)
def save_user_profile(sender, instance, **kwargs):
    print("Saving custom user profile...")
    print(instance.profile_pic.url)
    if instance.user_level == 1:
        instance.adminhod.save()
    if instance.user_level == 2:
        instance.staff.save()
    if instance.user_level == 3:
        instance.student.save()
