from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserChangeForm, RegistrationForm
from .forms import RegistrationForm
from .models import CustomUserProfile, Course


class CustomUserProfileAdmin(admin.ModelAdmin):
    add_form = RegistrationForm
    # form = CustomUserChangeForm
    model = CustomUserProfile
    list_display = ['email', 'first_name', 'middle_initial', 'last_name', 'profile_pic','is_staff', 'is_active', 'is_superuser']
    list_editable = ['profile_pic']


class CoursesAdmin(admin.ModelAdmin):
    model = Course
    list_display = ['id', 'course_name', 'date_created', 'date_updated']
    list_display_links = ['id']
    list_editable = ['course_name']
    search_fields = ['course_name']
    list_per_page = 10


admin.site.register(CustomUserProfile, CustomUserProfileAdmin,)
admin.site.register(Course, CoursesAdmin,)

