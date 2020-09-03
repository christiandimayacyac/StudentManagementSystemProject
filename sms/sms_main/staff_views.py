from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .mixins import StaffCheckMixin


class StaffDashboardView(LoginRequiredMixin, StaffCheckMixin, TemplateView):
    template_name = 'staff/staff_dashboard.html'
    extra_context = {'page_title': 'Staff Dashboard'}