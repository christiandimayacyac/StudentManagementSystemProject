from django.contrib import messages
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import CustomUserProfile, AdminHOD, Staff, Student, Course, Attendance, AttendanceReport


@receiver(post_save, sender=CustomUserProfile)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_level == 1:
            AdminHOD.objects.create(user_profile=instance)
        if instance.user_level == 2:
            Staff.objects.create(user_profile=instance)
        if instance.user_level == 3:
            # Get instance attributes from the admin_views.py
            gender = getattr(instance, '_gender', None)
            address = getattr(instance, '_address', None)
            course_id = getattr(instance, '_course_id', None)
            school_year = getattr(instance, '_school_year', None)
            year_level = getattr(instance, '_year_level', None)
            section = getattr(instance, '_section', None)

            Student.objects.create(user_profile=instance,
                                   gender=gender, address=address,
                                   school_year=school_year,
                                   course_id=course_id,
                                   year_level=year_level,
                                   section=section
                                   )


@receiver(post_save, sender=CustomUserProfile)
def save_user_profile(sender, instance, created, **kwargs):
    print("Saving custom user profile...")
    if instance.user_level == 1:
        instance.adminhod.save()
    if instance.user_level == 2:
        instance.staff.save()
    if instance.user_level == 3:
        instance.student.save()


@receiver(post_save, sender=Attendance)
def save_student_attendance(sender, instance, **kwargs):
    print("save_student_attendance saving")
    student_id = getattr(instance, '_student_id', None)
    # If at least one student is present add an attendance entry on each student
    if student_id:
        AttendanceReport.objects.create(student_id=student_id, attendance_id=instance)
