from django.contrib.auth.forms import AuthenticationForm
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as user_views

urlpatterns = [
    path('', user_views.Demo.as_view(), name='demo'),
    path('register/', user_views.RegisterView.as_view(template_name='registration/register.html'), name='register'),
    path('account/<int:pk>', user_views.UserDetailView.as_view(), name='user-detail'),
    path('login/', user_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', user_views.AdminView.as_view(), name='admin'),
    path('admin/staff/new', user_views.AddStaffView.as_view(), name='add-staff'),
    path('admin/student/new', user_views.AddStudentView.as_view(), name='add-student'),
    path('admin/courses/new', user_views.AddCourseView.as_view(), name='add-course'),
    path('admin/dashboard/', user_views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('staff/dashboard/', user_views.StaffDashboardView.as_view(), name='staff-dashboard'),
    path('student/dashboard/', user_views.StudentDashboardView.as_view(), name='student-dashboard'),
]
