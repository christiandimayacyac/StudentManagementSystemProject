from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth import get_user_model


# from .forms import LoginForm, RegistrationForm
from .forms import RegistrationForm, LoginForm, UserDetailForm, RegisterStaffForm, RegisterStudentForm, AddCourseForm
from .models import Course


class AdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class StaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_level == 2


class StudentMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_level == 3


class Demo(TemplateView):
    template_name = 'sms_main/demo.html'


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    extra_context = {'page_title': 'User Login'}


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    context_object_name = 'form'
    success_url = reverse_lazy('login')
    extra_context = {'page_title': 'User Registration'}


class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    context_object_name = 'user_obj'
    template_name = 'sms_main/user_detail.html'
    # template_name = 'admin/admin_home.html'
    extra_context = {'page_title': 'User Detail'}

    # def get_queryset(self):
    #     queryset = get_user_model().objects.filter(pk=self.kwargs['pk'])
    #     return queryset

    # def get_object(self):
    #     user_id = self.kwargs.get('pk')
    #     return get_object_or_404(get_user_model(), id=user_id)


class AdminView(LoginRequiredMixin, AdminMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'
    extra_context = {'page_title': 'Admin Dashboard'}


class AdminDashboardView(LoginRequiredMixin, AdminMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'
    extra_context = {'page_title': 'Admin Dashboard'}


class StaffDashboardView(LoginRequiredMixin, StaffMixin, TemplateView):
    template_name = 'staff/staff_dashboard.html'
    extra_context = {'page_title': 'Staff Dashboard'}


class StudentDashboardView(LoginRequiredMixin, StudentMixin, TemplateView):
    template_name = 'student/student_dashboard.html'
    extra_context = {'page_title': 'Student Dashboard'}


class AddStaffView(LoginRequiredMixin, CreateView):
    template_name = 'admin/add_staff.html'
    extra_context = {'page_title': 'Add Staff'}
    model = get_user_model()
    form_class = RegisterStaffForm
    success_url = reverse_lazy('admin-dashboard')

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.staff.address = form.cleaned_data.get('address')
        user.save()
        return super(AddStaffView, self).form_valid(form)

    def form_invalid(self, form):
        print("Invalid")
        print(form)
        return super(AddStaffView, self).form_invalid(form)


class AddStudentView(LoginRequiredMixin, CreateView):
    template_name = 'admin/add_student.html'
    extra_context = {'page_title': 'Add Student'}
    model = get_user_model()
    form_class = RegisterStudentForm
    context_object_name = 'reg_form'
    success_url = reverse_lazy('admin-dashboard')

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.student.gender = form.cleaned_data.get('gender')
        user.student.address = form.cleaned_data.get('address')
        user.student.session_start = form.cleaned_data.get('session_start')
        user.student.session_end = form.cleaned_data.get('session_end')
        user.student.course_id = form.cleaned_data.get('course_id')
        user.save()
        messages.success(self.request, "Student Registration Successful")
        return super(AddStudentView, self).form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Student Registration Failed")
        return response


class AddCourseView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = AddCourseForm
    template_name = 'admin/add_course.html'
    success_url = reverse_lazy('admin')

    def form_valid(self, form):
        messages.success(self.request, 'Course has been created.')

        return super(AddCourseView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Unable to create the new course.')

        return super(AddCourseView, self).form_invalid(form)





