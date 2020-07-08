from datetime import datetime

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils import timezone


class UserProfileManager(BaseUserManager):
    """Manager for User Profiles - Provides method to interact with the Customized User Model"""

    def create_user(self, email, first_name, middle_initial, last_name, password=None):
        """Create a new user profile"""

        if not email:
            raise ValueError('User must have an email address')

        if not first_name:
            raise ValueError('User enter your first name')

        if not middle_initial:
            raise ValueError('User enter your middle initial')

        if not last_name:
            raise ValueError('User enter your last name')

        if not password:
            raise ValueError('Password is required')

        email = self.normalize_email(email)
        # Create an object model that will hold the user data
        user = self.model(email=email, first_name=first_name, middle_initial=middle_initial, last_name=last_name)

        # Encrypt the password
        user.set_password(password)
        # Save the user data in the database using the default settings in the settings.py "DATABASE"
        user.save(using=self._db)

        # return the newly created object
        return user

    def create_superuser(self, email, first_name, middle_initial, last_name, password):
        """Create and save a super user"""
        user = self.create_user(email, first_name, middle_initial, last_name,
                                password)  # self parameter is automatically passed when calling another class function

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class CustomUserProfile(AbstractBaseUser, PermissionsMixin):
    user_type = (
        (1, 'Admin'),
        (2, 'Staff'),
        (3, 'Student')
    )
    user_level = models.IntegerField(default=1, choices=user_type, verbose_name='user_level')
    first_name = models.CharField(max_length=255)
    middle_initial = models.CharField(max_length=2)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='photos/%Y/%m/%d', default="/default.png", blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'middle_initial', 'last_name']

    def get_full_name(self):
        """Retrieve the full name of the user"""
        return f"{self.first_name} {self.middle_initial} {self.last_name}"

    def get_short_name(self):
        """Retrieve the short name of the user"""
        return self.first_name

    def get_user_level(self):
        """Retrieve the user level"""
        return self.user_level

    def get_user_avatar(self):
        """Retrieve the user profile picture"""
        return self.profile_pic

    def __str__(self):
        """Return string representation of the user"""
        return self.email

    def get_absolute_url(self):
        if self.user_level == 1:
            return reverse('admin-dashboard')
        elif self.user_level == 2:
            return reverse('staff-dashboard')
        elif self.user_level == 3:
            return reverse('student-dashboard')
        else:
            return reverse('logout')


class AdminHOD(models.Model):
    # name = models.CharField(max_length=100, blank=False)
    # email = models.CharField(max_length=255, blank=False, null=False)
    # password = models.CharField(max_length=255, blank=False, null=False)
    user_profile = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('admin-dashboard')


class Staff(models.Model):
    user_profile = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=datetime.now)

    # def get_name(self):
    #     """Return string representation of the course"""
    #     return f"{self.first_name} {self.middle_initial} {self.last_name}"

    def get_absolute_url(self):
        return reverse('admin-dashboard')


class Course(models.Model):
    course_name = models.CharField(max_length=255, blank=False, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        """Return string representation of the course"""
        return self.course_name

    def get_absolute_url(self):
        return reverse('admin-dashboard')


class Student(models.Model):
    user_profile = models.OneToOneField(CustomUserProfile, on_delete=models.CASCADE)
    gender = models.CharField(default="M", max_length=255, blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    course_id = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, to_field='id')
    session_start = models.DateTimeField(default=None, null=True)
    session_end = models.DateTimeField(default=None, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)

    class Meta:
        permissions = (
            ('can_view_page', 'Can view page'),
        )

    def get_gender(self):
        """Return string representation of the course"""
        return self.gender

    def get_absolute_url(self):
        return reverse('admin-dashboard')


class Subject(models.Model):
    subject_name = models.CharField(max_length=255, blank=False, null=False)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    staff_id = models.ForeignKey(CustomUserProfile, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)

    def get_course_id(self):
        return self.course_id

    def get_staff_id(self):
        return self.staff_id

    def get_absolute_url(self):
        return reverse('admin-dashboard')


class Attendance(models.Model):
    subject_id = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    attendance_date = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)


class AttendanceReport(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)


class LeaveReportStaff(models.Model):
    staff_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)


class StudentFeedBack(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)


class StaffFeedBack(models.Model):
    student_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)


class StaffNotification(models.Model):
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)


class StudentNotification(models.Model):
    staff_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=timezone.now)
