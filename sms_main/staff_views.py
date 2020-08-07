import json
from datetime import datetime, date

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import request, HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView

from .admin_views import custom_message
from .mixins import StaffCheckMixin
from .models import Attendance, Subject, SchoolYearModel, OfferedSubject, CustomUserProfile, Student, AttendanceReport


class StaffDashboardView(LoginRequiredMixin, StaffCheckMixin, TemplateView):
    template_name = 'staff/staff_dashboard.html'
    extra_context = {'page_title': 'Staff Dashboard'}


class StudentAttendanceView(LoginRequiredMixin, StaffCheckMixin, ListView):
    model = Subject
    template_name = 'staff/student_attendance.html'
    login_url = 'login'
    school_years = SchoolYearModel.objects.all().order_by('-school_year_end')
    context_object_name = 'subjects_obj'
    links = {
        'Home': 'staff-dashboard',
        'Student Attendance': ''
    }
    extra_context = {
        'page_title': 'Staff Attendance',
        'school_years_obj': school_years,
        'current_date': datetime.now
    }

    def get_queryset(self):
        return Subject.objects.filter(staff_id=self.request.user.id).values('id', 'subject_name').order_by('subject_name')


class StudentAttendanceReport(LoginRequiredMixin, StaffCheckMixin, ListView):
    model = Subject
    context_object_name = 'subjects_obj'
    template_name = 'staff/student_attendance_report.html'
    school_years = SchoolYearModel.objects.all().order_by('-school_year_end')
    extra_context = {
        'page_title': 'Staff Dashboard',
        'school_years_obj': school_years,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter query by the variable 'id' set from the url
        return qs.filter(staff_id=self.kwargs['id']).order_by('subject_name')


class AjaxFetchStudents(View):
    model = OfferedSubject

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxFetchStudents, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        custom_message(self.request, "Invalid AJAX Request", "error")
        return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

    def post(self, *args, **kwargs):
        students = []
        if self.request.method == "POST":
            body_unicode = self.request.body
            body = json.loads(body_unicode)
            subject_id = body['subject_id']
            staff_id = body['staff_id']
            school_year_id = body['school_year_id']

            # students = OfferedSubject.objects.filter(subject_id=subject_id, school_year=school_year_id, subject_id__staff_id=staff_id)
            students = get_user_model().objects.filter(student__subjects__staff_id=staff_id,
                                                       student__subjects__id=subject_id,
                                                       student__school_year__id=school_year_id)

        if not students:
            data = json.dumps({})
        else:
            data = serializers.serialize('json', students, fields=('id', 'first_name', 'middle_initial', 'last_name'))
        return HttpResponse(data, content_type="application/json")


class AjaxSaveAttendance(View):
    model = Attendance

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxSaveAttendance, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

    def post(self, *args, **kwargs):
        # Get POST data from Ajax call
        body_unicode = self.request.body
        body = json.loads(body_unicode)
        student_id_list = body['id_list']
        subject_id = int(body['subject_id'])
        school_year_id = body['school_year_id']

        status = ''

        # Check if attendance entry already exists
        existing_attendance = Attendance.objects.filter(
            subject_id=subject_id,
            school_year_id=school_year_id,
            date_created__startswith=date.today(),
            subject_id__staff_id=self.request.user.id
        ).only('id')

        if not existing_attendance:
            # Create a new Attendance Entry
            subject = get_object_or_404(Subject, pk=subject_id)
            school_year = get_object_or_404(SchoolYearModel, pk=school_year_id)
            new_attendance = Attendance(subject_id=subject, school_year=school_year)

            for student_id in student_id_list:
                # Save an attendance for each selected students
                try:
                    student = get_object_or_404(Student, user_profile=student_id)
                    new_attendance._student_id = student
                    new_attendance.save()
                    status = True
                    custom_message(self.request, "Attendance for today has been saved.", "success")
                except:
                    status = False
                    custom_message(self.request, "There's an error in saving the attendance.", "error")
                    break
        else:
            custom_message(self.request, "An attendance for this subject today already exists.", "error")
            status = False

        data = {"status": status}
        return JsonResponse(data)


class AjaxFetchAttendance(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxFetchAttendance, self).dispatch(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        custom_message(self.request, "Invalid AJAX Request", "error")
        return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

    def post(self, *args, **kwargs):
        students = []
        if self.request.method == "POST":
            body_unicode = self.request.body
            body = json.loads(body_unicode)
            subject_id = body['subject_id']
            staff_id = body['staff_id']
            school_year_id = body['school_year_id']
            attendance = Attendance.objects.filter(subject_id__staff_id=staff_id,
                                                       subject_id=subject_id,
                                                       school_year_id=school_year_id)

        if not attendance:
            data = json.dumps({})
        else:
            data = serializers.serialize('json', attendance, fields=('id', 'attendance_date'))
        return HttpResponse(data, content_type="application/json")

