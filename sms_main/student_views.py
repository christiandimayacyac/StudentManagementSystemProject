from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import TemplateView
from .mixins import StudentCheckMixin


class StudentDashboardView(LoginRequiredMixin, StudentCheckMixin, TemplateView):
    template_name = 'student/student_dashboard.html'
    extra_context = {'page_title': 'Student Dashboard'}