import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import get_messages
from django.core import serializers
from django.db import models
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DeleteView

from .forms import RegisterStaffForm, RegisterStudentForm, AddCourseForm, AddSubjectForm, ManageStaffForm, \
    ManageStudentsForm, ManageSubjectsForm, ManageCoursesForm, EditStaffForm, EditStudentForm, EditSubjectForm, \
    AddSchoolYearForm, EditCourseForm, EditSchoolYearForm, AddSectionForm
from .mixins import AdminCheckMixin
from .models import Course, Subject, CustomUserProfile, Staff, Student, SchoolYearModel, OfferedSubject, CourseSection
from collections import OrderedDict


def custom_message(request, msg, msg_tag):
    """
    Just add the message once
    :param request:
    :param msg:
    :return:
    """
    if msg not in [m.message for m in get_messages(request)]:
        if msg_tag == "success":
            messages.success(request, msg)
        if msg_tag == "error":
            messages.error(request, msg)
        if msg_tag == "warning":
            messages.warning(request, msg)
        if msg_tag == "info":
            messages.info(request, msg)
        if msg_tag == "debug":
            messages.debug(request, msg)

class AdminDashboardView(LoginRequiredMixin, AdminCheckMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'
    links = {'Home': ''}

    extra_context = {
        'page_title': 'Admin Dashboard',
        'page_header_title': 'Admin Dashboard',
        'breadcrumbs': OrderedDict(links.items())
    }


class AddStaffView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    template_name = 'admin/add_staff.html'
    model = get_user_model()
    form_class = RegisterStaffForm
    success_url = reverse_lazy('admin-dashboard')
    links = {
        'page_title': 'Add Staff',
        'Home': 'admin-dashboard',
        'Add Staff': ''
    }

    extra_context = {
        'page_header_title': 'Add Staff',
        'breadcrumbs': OrderedDict(links.items())
    }

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.staff.address = form.cleaned_data.get('address')
        user.save()
        custom_message(self.request, "Staff Registration Successful", "success")
        return super(AddStaffView, self).form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, "Student Registration Failed", "error")
        return super(AddStaffView, self).form_invalid(form)


class AddStudentView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    template_name = 'admin/add_student.html'
    extra_context = {'page_title': 'Add Student'}
    model = get_user_model()
    form_class = RegisterStudentForm
    success_url = reverse_lazy('admin-dashboard')

    school_year = SchoolYearModel.objects.all()
    links = {
        'Home': 'admin-dashboard',
        'Add Student': ''
    }
    extra_context = {
        'page_header_title': 'Add Student',
        'school_year': school_year,
        'default_pic': '/media/default.png',
        'breadcrumbs': OrderedDict(links.items())
    }

    def form_valid(self, form):
        print("Student info valid")
        user = form.save(commit=False)
        # Set instance attributes to be used by the signal for saving extra details in the Student Model
        user._gender = form.cleaned_data.get('gender')
        user._address = form.cleaned_data.get('address')
        user._school_year = form.cleaned_data.get('school_year')
        user._course_id = form.cleaned_data.get('course_id')
        user._year_level = form.cleaned_data.get('year_level')
        user._section = form.cleaned_data.get('section')



        user.save()

        print('user')
        print(user)
        print(user.id)
        print(user.student.id)

        # Make an entry for subjects enrolled by the student
        for subject in form.cleaned_data.get('subject_list'):
            # Get the subject and student instance
            stud = user.student
            subj = OfferedSubject(subject_id=subject, student_id=stud, school_year=user._school_year)
            subj.save()
        custom_message(self.request, "Student Registration Successful", "success")
        return super(AddStudentView, self).form_valid(form)

    def form_invalid(self, form):
        print("Student info invalid")
        print(form.cleaned_data)
        custom_message(self.request, "Student Registration Failed", "error")
        return super(AddStudentView, self).form_invalid(form)


class AddCourseView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    model = Course
    form_class = AddCourseForm
    template_name = 'admin/add_course.html'
    success_url = reverse_lazy('add-course')
    links = {
        'Home': 'admin-dashboard',
        'Add Course': ''
    }
    extra_context = {
        'page_header_title': 'Addsubject Course',
        'breadcrumbs': OrderedDict(links.items())
    }

    def form_valid(self, form):
        custom_message(self.request, 'Course has been created.', "success")
        return super(AddCourseView, self).form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to create the new course.', "error")
        return super(AddCourseView, self).form_invalid(form)


class AddSubjectView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    model = Subject
    form_class = AddSubjectForm
    template_name = 'admin/add_subject.html'
    success_url = reverse_lazy('add-subject')
    links = {
        'Home': 'admin-dashboard',
        'Add Subject': ''
    }
    extra_context = {
        'page_header_title': 'Add Subject',
        'breadcrumbs': OrderedDict(links.items())
    }

    def form_valid(self, form):
        custom_message(self.request, 'Subject has been created.', "success")
        return super(AddSubjectView, self).form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to create the new subject.', "error")
        return super(AddSubjectView, self).form_invalid(form)


class AddSectionView(CreateView):
    model = CourseSection
    template_name = 'admin/add_section.html'
    form_class = AddSectionForm
    courses = Course.objects.all().order_by("course_name").only('id', 'course_name')
    success_url = reverse_lazy('add-section')
    links = {
        'Home': 'admin-dashboard',
        'Add Section': ''
    }
    extra_context = {
        'page_header_title': 'Add Section',
        'courses_obj': courses,
        'breadcrumbs': OrderedDict(links.items())
    }

    def form_valid(self, form):
        custom_message(self.request, 'Section has been created.', "success")
        return super(AddSectionView, self).form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to create the new section.', "error")
        return super(AddSectionView, self).form_invalid(form)


class AddSchoolYearView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    model = SchoolYearModel
    form_class = AddSchoolYearForm
    template_name = 'admin/add_school_year.html'
    success_url = reverse_lazy('manage-school-years')
    links = {
        'Home': 'admin-dashboard',
        'Add School Year': ''
    }
    extra_context = {
        'page_header_title': 'Add School Year',
        'breadcrumbs': OrderedDict(links.items())
    }

    def form_valid(self, form):
        custom_message(self.request, 'School Year has been created.', "success")
        return super(AddSchoolYearView, self).form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, 'Unable to create the new school year.', "error")
        return super(AddSchoolYearView, self).form_invalid(form)


class ManageSchoolYearView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = SchoolYearModel
    template_name = 'admin/manage_school_year.html'
    context_object_name = 'school_year_obj'
    form_class = ManageStaffForm
    links = {
        'Home': 'admin-dashboard',
        'Manage School Year': ''
    }
    extra_context = {
        'page_header_title': 'Manage School Year',
        'breadcrumbs': OrderedDict(links.items())
    }


class ManageStaffView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Staff
    template_name = 'admin/manage_staff.html'
    context_object_name = 'staff_obj'
    form_class = ManageStaffForm
    links = {
        'Home': 'admin-dashboard',
        'Manage Staff': ''
    }
    extra_context = {
        'page_header_title': 'Manage Staff',
        'breadcrumbs': OrderedDict(links.items())
    }


class ManageStudentsView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Student
    template_name = 'admin/manage_students.html'
    context_object_name = 'students_obj'
    form_class = ManageStudentsForm
    links = {
        'Home': 'admin-dashboard',
        'Manage Student': ''
    }
    extra_context = {
        'page_header_title': 'Manage Students',
        'breadcrumbs': OrderedDict(links.items())
    }


class ManageSubjectsView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Subject
    template_name = 'admin/manage_subjects.html'
    context_object_name = 'subjects_obj'
    form_class = ManageSubjectsForm
    links = {
        'Home': 'admin-dashboard',
        'Manage Subject': ''
    }
    extra_context = {
        'page_header_title': 'Manage Subjects',
        'breadcrumbs': OrderedDict(links.items())
    }


class ManageCoursesView(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Course
    template_name = 'admin/manage_courses.html'
    context_object_name = 'courses_obj'
    form_class = ManageCoursesForm
    links = {
        'Home': 'admin-dashboard',
        'Manage Course': ''
    }
    extra_context = {
        'page_header_title': 'Manage Courses',
        'breadcrumbs': OrderedDict(links.items())
    }


class EditStaffView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = get_user_model()
    template_name = 'admin/edit_staff.html'
    context_object_name = 'user_obj'
    form_class = EditStaffForm
    links = {
        'Home': 'admin-dashboard',
        'Manage Staff': 'manage-staff',
        'Edit Staff': ''
    }
    extra_context = {
        'page_header_title': 'Edit Staff',
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=user_id)

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.staff.address = form.cleaned_data.get('address')
        user.save()
        custom_message(self.request, "Staff Update Successful", "success")
        return super(EditStaffView, self).form_valid(form)


class EditStudentView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = get_user_model()
    template_name = 'admin/edit_student.html'
    context_object_name = 'user_obj'
    form_class = EditStudentForm
    links = {
        'Home': 'admin-dashboard',
        'Dashboard': 'manage-students',
        'Edit Students': ''
    }
    extra_context = {
        'page_header_title': 'Edit Student',
        'course_obj': Course.objects.all().order_by('course_name'),
        'school_year_obj': SchoolYearModel.objects.all().order_by('-id'),
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=user_id)

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.student.address = form.cleaned_data.get('address')
        user.student.school_year = form.cleaned_data.get('school_year')
        user.student.gender = form.cleaned_data.get('gender')
        user.student.course_id = form.cleaned_data.get('course_id')
        user.student.profile_pic = form.cleaned_data.get('profile_pic')
        user.student.date_updated = form.cleaned_data.get('date_updated')
        user.save()
        custom_message(self.request, "Student Update Successful", "success")
        return super(EditStudentView, self).form_valid(form)

    def form_invalid(self, form):
        custom_message(self.request, "Student Update Failed", "error")
        return super(EditStudentView, self).form_valid(form)


class EditSubjectView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = Subject
    form_class = EditSubjectForm
    template_name = 'admin/edit_subject.html'
    context_object_name = 'subject_obj'
    links = {
        'Home': 'admin-dashboard',
        'Dashboard': 'manage-subjects',
        'Edit Subject': ''
    }
    extra_context = {
        'course_obj': Course.objects.all(),
        'staff_obj': CustomUserProfile.objects.filter(user_level=2),
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        subject_id = self.kwargs.get('id')
        return get_object_or_404(Subject, id=subject_id)

    def form_valid(self, form):
        print("valid")
        print(form.cleaned_data)
        subject = form.save()
        subject.save()
        custom_message(self.request, "Subject Update Successful", "succes")
        return super(EditSubjectView, self).form_valid(form)

    def form_invalid(self, form):
        print("invalid")
        messages.error(self.request, "Subject Update Failed", "error")
        return super(EditSubjectView, self).form_valid(form)


class EditCourseView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = Course
    form_class = EditCourseForm
    template_name = 'admin/edit_course.html'
    context_object_name = 'course_obj'
    links = {
        'Home': 'admin-dashboard',
        'Dashboard': 'manage-courses',
        'Edit Course': ''
    }
    extra_context = {
        'page-header-title': 'Edit Course',
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('id')
        return get_object_or_404(Course, id=course_id)

    def form_valid(self, form):
        course = form.save()
        course.save()
        custom_message(self.request, "Course Update Successful", "succes")
        return super(EditCourseView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Course Update Failed", "error")
        return super(EditCourseView, self).form_valid(form)


class EditSchoolYearView(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = SchoolYearModel
    form_class = EditSchoolYearForm
    template_name = 'admin/edit_school_year.html'
    context_object_name = 'school_year_obj'
    links = {
        'Home': 'admin-dashboard',
        'Manage School Year': 'manage-school-years',
        'Edit School Year': ''
    }
    extra_context = {
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        sy_id = self.kwargs.get('id')
        return get_object_or_404(SchoolYearModel, id=sy_id)

    def form_valid(self, form):
        sy = form.save()
        sy.save()
        custom_message(self.request, "School Year Update Successful", "succes")
        return super(EditSchoolYearView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "School Year Update Failed", "error")
        return super(EditSchoolYearView, self).form_valid(form)


class DeleteStudentView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = get_user_model()
    template_name = 'admin/delete_student.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('manage-students')
    login_url = 'login'
    links = {
        'Home': 'admin-dashboard',
        'Manage Student': 'manage-students',
        'Delete Student': ''
    }
    extra_context = {
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        student_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=student_id)


class DeleteSubjectView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = Subject
    template_name = 'admin/delete_subject.html'
    context_object_name = 'subject_obj'
    success_url = reverse_lazy('manage-subjects')
    login_url = 'login'
    links = {
        'Home': 'admin-dashboard',
        'Manage Subject': 'manage-subjects',
        'Delete Subject': ''
    }
    extra_context = {
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        subject_id = self.kwargs.get('id')
        return get_object_or_404(Subject, id=subject_id)


class DeleteCourseView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = Course
    template_name = 'admin/delete_course.html'
    context_object_name = 'course_obj'
    success_url = reverse_lazy('manage-courses')
    error_url = reverse_lazy('manage-courses')
    login_url = 'login'
    links = {
        'Home': 'admin-dashboard',
        'Manage Course': 'manage-courses',
        'Delete Course': ''
    }
    extra_context = {
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        course_idx = self.kwargs.get('id')
        return get_object_or_404(Course, id=course_idx)

    def get_error_url(self):
        return self.error_url

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        error_url = self.get_error_url()
        try:
            self.object.delete()
            custom_message(self.request, "The course has been deleted successfully.", "succes")
            return redirect(success_url)
        except models.ProtectedError:
            messages.error(self.request, f"Unable to delete the course: {self.object.course_name}. One or more "
                                         f"students are enrolled on this course.", "error")
            return redirect(error_url)


class DeleteStaffView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = get_user_model()
    template_name = 'admin/delete_staff.html'
    context_object_name = 'staff_obj'
    success_url = reverse_lazy('manage-staff')
    login_url = 'login'
    links = {
        'Home': 'admin-dashboard',
        'Manage Staff': 'manage-staff',
        'Delete Staff': ''
    }
    extra_context = {
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        staff_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=staff_id)


class DeleteSchoolYearView(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = SchoolYearModel
    template_name = 'admin/delete_school_year.html'
    context_object_name = 'school_year_obj'
    success_url = reverse_lazy('manage-school-year')
    login_url = 'login'
    links = {
        'Home': 'admin-dashboard',
        'Manage School Year': 'manage-school-years',
        'Delete School Year': ''
    }
    extra_context = {
        'breadcrumbs': OrderedDict(links.items())
    }

    def get_object(self, queryset=None):
        sy_id = self.kwargs.get('id')
        return get_object_or_404(SchoolYearModel, id=sy_id)


class AjaxGetSubjects(View):
    model = OfferedSubject

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxGetSubjects, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            # body_unicode = self.request.body.decode('utf-8') decode is only used in python 3.5below
            body_unicode = self.request.body
            body = json.loads(body_unicode)
            course_id = body['course_id']
            course_subjects = Subject.objects.filter(course_id=course_id, is_offered=True).order_by('subject_name')

            if not course_subjects:
                data = json.dumps({})
            else:
                data = serializers.serialize('json', course_subjects, fields=('id', 'subject_name'))
            return HttpResponse(data, content_type="application/json")
        else:
            return JsonResponse({"success": False, "method": self.request.method, "is_ajax": self.request.is_ajax()}, status=400)


class AjaxAssignSubjects(CreateView):
    pass
