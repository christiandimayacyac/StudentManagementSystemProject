import json
from datetime import datetime, date

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.http import request, HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, CreateView, UpdateView

from .admin_views import custom_message
from .forms import CreateAttendanceForm, LeaveApplicationForm, StaffFeedbackForm, StaffEditFeedbackForm
from .mixins import StaffCheckMixin
from .models import Attendance, Subject, SchoolYearModel, OfferedSubject, CustomUserProfile, Student, AttendanceReport, \
    CourseSection, LeaveReportStaff, StaffFeedBack


class StaffDashboardView(LoginRequiredMixin, StaffCheckMixin, TemplateView):
    template_name = 'staff/staff_dashboard.html'
    extra_context = {
        'page_title': 'Staff Dashboard',
        'page_header_title': 'Staff Dashboard'
    }


class CreateStudentAttendanceView(LoginRequiredMixin, StaffCheckMixin, CreateView):
    model = Attendance
    template_name = 'staff/student_attendance.html'
    form_class = CreateAttendanceForm
    login_url = 'login'
    success_url = reverse_lazy('staff-dashboard')
    school_years = SchoolYearModel.objects.all().order_by('-school_year_end')
    links = {
        'Home': 'staff-dashboard',
        'Student Attendance': ''
    }
    extra_context = {
        'page_title': 'Create Attendance',
        'page_header_title': 'Create Attendance',
    }

    def get_initial(self, *args, **kwargs):
        initial = super(CreateStudentAttendanceView, self).get_initial(**kwargs)
        initial['current_date'] = datetime.now
        initial['page_title'] = 'Staff Attendance'
        initial['school_years_obj'] = SchoolYearModel.objects.all().order_by('-school_year_end')
        initial['subjects_obj'] = Subject.objects.filter(staff_id=self.request.user.id).order_by('subject_name').only('id', 'subject_name', 'course_id')
        return initial

    def form_valid(self, form):
        subject = form.cleaned_data['subject_id']
        school_year = form.cleaned_data['school_year']
        student_id_list = form.cleaned_data['students']
        section = form.cleaned_data['section_id']

        # Check if attendance entry already exists
        existing_attendance = Attendance.objects.filter(
            subject_id=subject,
            school_year_id=school_year,
            date_created__startswith=date.today(),
            subject_id__staff_id=self.request.user.id
        ).only('id')

        is_error = False
        if not existing_attendance:
            # Create a new Attendance Entry
            subject = get_object_or_404(Subject, pk=subject.id)
            school_year = get_object_or_404(SchoolYearModel, pk=school_year.id)
            section = get_object_or_404(CourseSection, id=section.id)
            new_attendance = Attendance(subject_id=subject, school_year=school_year, section_id=section)
            # Check if at least 1 student is present then make an attendance entry then make an  attendance report for every student
            # otherwise, only make an attendance entry
            if student_id_list:
                for student_id in student_id_list:
                    # Save an attendance for each selected students
                    try:
                        student = get_object_or_404(Student, user_profile=student_id)
                        # Create an instance property for signal reference to create AttendanceReport Entry
                        new_attendance._student_id = student
                        new_attendance.save()
                        # custom_message(self.request, 'Attendance has been created.', "success")
                    except:
                        # custom_message(self.request, "There's an error in saving the attendance.", "error")
                        is_error = True
                        break
            else:
                new_attendance._student_id = False
                new_attendance.save()
        else:
            custom_message(self.request, "An attendance for this subject today already exists.", "error")
            return redirect(self.success_url)

        if not is_error:
            custom_message(self.request, 'Attendance has been created.', "success")
        else:
            custom_message(self.request, "There's an error in saving the attendance.", "error")
        return redirect(self.success_url)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to create the new attendance.', "error")
        return super().form_invalid(form)


class StudentAttendanceReport(LoginRequiredMixin, StaffCheckMixin, ListView):
    model = Subject
    context_object_name = 'subjects_obj'
    template_name = 'staff/student_attendance_report.html'
    school_years = SchoolYearModel.objects.all().order_by('-school_year_end')
    extra_context = {
        'page_title': 'Student Attendance Report',
        'page_header_title': 'Student Attendance Report',
        'school_years_obj': school_years,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter query by the variable 'id' set from the url
        return qs.filter(staff_id=self.kwargs['id']).order_by('subject_name')


class AjaxFetchStudents(View):
    model = OfferedSubject

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AjaxFetchStudents, self).dispatch(*args, **kwargs)

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
            section_id = body['section_id']
            school_year_id = body['school_year_id']

            # students = OfferedSubject.objects.filter(subject_id=subject_id, school_year=school_year_id, subject_id__staff_id=staff_id)
            students = get_user_model().objects.filter(student__subjects__staff_id=staff_id,
                                                       student__subjects__id=subject_id,
                                                       student__section=section_id,
                                                       student__school_year__id=school_year_id)

        if not students:
            data = json.dumps({})
        else:
            data = serializers.serialize('json', students, fields=('id', 'first_name', 'middle_initial', 'last_name'))
        return HttpResponse(data, content_type="application/json")


class AjaxFetchAttendanceList(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AjaxFetchAttendanceList, self).dispatch(*args, **kwargs)

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


class AjaxFetchSections(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AjaxFetchSections, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        custom_message(self.request, "Invalid AJAX Request", "error")
        return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

    def post(self, *args, **kwargs):
        sections = []
        if self.request.method == "POST":
            body_unicode = self.request.body
            body = json.loads(body_unicode)
            course_id = body['courseId']
            sections = CourseSection.objects.filter(course_id=course_id)
        else:
            custom_message(self.request, "Invalid AJAX Request", "error")
            return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

        if not sections:
            data = json.dumps({})
        else:
            data = serializers.serialize('json', sections, fields=('id', 'section_name'))
        return HttpResponse(data, content_type="application/json")


class AjaxSaveStudentAttendance(View):
    pass


class AjaxViewAttendance(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        custom_message(self.request, "Invalid AJAX Request", "error")
        return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

    def post(self, *args, **kwargs):

        if self.request.method == "POST":
            body_unicode = self.request.body
            body = json.loads(body_unicode)
            attendance_id = body['attendance']
            subject_id = body['subject_id']
            school_year = body['school_year_id']
            qs = AttendanceReport.objects.select_related('student_id').filter(attendance_id=attendance_id).only('student_id')
            class_list = OfferedSubject.objects.filter(subject_id=subject_id, school_year=school_year)
            present_students = []
            attendance_list = []
            for ids in qs:
                present_students.append(ids.student_id.id)
            for student in class_list:
                if student.student_id.id in present_students:
                    is_present = 1
                else:
                    is_present = 0
                student_name = [student.student_id.user_profile.last_name + ", ",
                                student.student_id.user_profile.first_name,
                                student.student_id.user_profile.middle_initial + "."]
                full_name = " ".join(student_name)
                attendance_list.append([{'id': student.student_id.id}, {'full_name': full_name}, {'is_present':is_present}])
            return JsonResponse(attendance_list, safe=False)
        else:
            custom_message(self.request, "Invalid AJAX Request", "error")
            return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})


class AjaxUpdateAttendance(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        custom_message(self.request, "Invalid AJAX Request", "error")
        return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            body_unicode = self.request.body
            body = json.loads(body_unicode)
            attendance_id = body['attendance_id']
            id_list = body['id_list']
            qs = AttendanceReport.objects.select_related('student_id').filter(attendance_id=attendance_id).values('student_id')
            current_attendance = []
            for attendance in qs:
                cur_id = attendance['student_id']
                current_attendance.append(cur_id)
            for stud in id_list:
                stud_id = int(stud['id'])
                if stud['status']:
                    if stud_id not in current_attendance:
                        # Add student attendance record
                        student = Student.objects.get(pk=stud['id'])
                        att_id = Attendance.objects.get(pk=attendance_id)
                        new_attendance = AttendanceReport(student_id=student, attendance_id=att_id)
                        new_attendance.save()
                elif stud_id in current_attendance:
                    # Delete student attendance record
                    AttendanceReport.objects.filter(student_id=stud['id'], attendance_id=attendance_id).delete()
        else:
            custom_message(self.request, "Invalid AJAX Request", "error")
            return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()})

        custom_message(self.request, "Attendance Report has been updated successfully","success")
        return JsonResponse({"success": True, "method": self.request.method, "is_ajax": self.request.is_ajax()})


class LeaveApplicationView(LoginRequiredMixin, StaffCheckMixin, CreateView):
    model = LeaveReportStaff
    template_name = "staff/leave_application.html"
    form_class = LeaveApplicationForm
    success_url = reverse_lazy('staff-leave-report')
    extra_context = {
        'page_title': 'Leave Application',
        'page_header_title': 'Leave Application'
    }

    def form_valid(self, form):
        custom_message(self.request, 'Application for leave is sent successfully.', "success")
        return super().form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to apply for leave.', "error")
        return super().form_invalid(form)


class LeaveReportView(LoginRequiredMixin, StaffCheckMixin, ListView):
    model = LeaveReportStaff
    context_object_name = 'leave_report_obj'
    template_name = "staff/leave_report.html"
    extra_context = {
        'page_title': 'Leave Report',
        'page_header_title': 'Leave Report'
    }

    def get_queryset(self):
        qs = super().get_queryset()
        #Filter only leave applications of the current staff
        return qs.filter(staff_id=self.request.user.staff.id).order_by('id')


class StaffFeedBackView(LoginRequiredMixin, StaffCheckMixin, CreateView):
    model = StaffFeedBack
    template_name = 'staff/staff_feedback.html'
    form_class = StaffFeedbackForm
    success_url = reverse_lazy('staff-feedback')
    extra_context = {
        'page_title': 'Feedback',
        'page_header_title': 'Feedback Form'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_id = self.request.user.staff.id
        context["feedback_obj"] = StaffFeedBack.objects.filter(staff_id=staff_id)
        return context

    def form_valid(self, form):
        custom_message(self.request, 'Feedback is sent successfully.', "success")
        return super().form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to send feedback.', "error")
        return super().form_invalid(form)


class StaffEditFeedBackView(LoginRequiredMixin, StaffCheckMixin, UpdateView):
    model = StaffFeedBack
    form_class = StaffEditFeedbackForm
    context_object_name = 'feedback_obj'
    template_name = 'staff/edit_staff_feedback.html'
    extra_context = {
        'page_title': 'Edit Feedback',
        'page_header_title': 'Edit Feedback'
    }

    def get_object(self):
        feedback_id = self.kwargs.get('id')
        return get_object_or_404(StaffFeedBack, id=feedback_id)

    def form_valid(self, form):
        custom_message(self.request, 'Feedback has been updated.', "success")
        return super().form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to edit feedback.', "error")
        return super().form_invalid(form)
