from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DeleteView

from .forms import RegisterStaffForm, RegisterStudentForm, AddCourseForm, AddSubjectForm, ManageStaffForm, \
    ManageStudentsForm, ManageSubjectsForm, ManageCoursesForm, EditStaffForm, EditStudentForm, EditSubjectForm
from .mixins import AdminCheckMixin
from .models import Course, Subject, CustomUserProfile, Staff, Student


class AdminDashboardView(LoginRequiredMixin, AdminCheckMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'
    extra_context = {
        'page_title': 'Admin Dashboard',
        'page_header_title': 'Admin Dashboard'
    }


class AddStaffView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    template_name = 'admin/add_staff.html'
    extra_context = {'page_title': 'Add Staff'}
    model = get_user_model()
    form_class = RegisterStaffForm
    success_url = reverse_lazy('admin-dashboard')
    extra_context = {'page_header_title': 'Add Staff'}

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.staff.address = form.cleaned_data.get('address')
        user.save()
        messages.success(self.request, "Staff Registration Successful")
        return super(AddStaffView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Student Registration Failed")
        return super(AddStaffView, self).form_invalid(form)


class AddStudentView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    template_name = 'admin/add_student.html'
    extra_context = {'page_title': 'Add Student'}
    model = get_user_model()
    form_class = RegisterStudentForm
    context_object_name = 'reg_form'
    success_url = reverse_lazy('admin-dashboard')
    extra_context = {
        'page_header_title': 'Add Student',
        'default_pic':  '/media/default.png'
    }

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


class AddCourseView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    model = Course
    form_class = AddCourseForm
    template_name = 'admin/add_course.html'
    success_url = reverse_lazy('admin')
    extra_context = {'page_header_title': 'Add Course'}

    def form_valid(self, form):
        messages.success(self.request, 'Course has been created.')
        return super(AddCourseView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Unable to create the new course.')
        return super(AddCourseView, self).form_invalid(form)


class AddSubjectView(LoginRequiredMixin, AdminCheckMixin, CreateView):
    model = Subject
    form_class = AddSubjectForm
    template_name = 'admin/add_subject.html'
    success_url = reverse_lazy('admin')
    extra_context = {'page_header_title': 'Add Subject'}

    def form_valid(self, form):
        messages.success(self.request, 'Subject has been created.')
        return super(AddSubjectView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Unable to create the new subject.')
        return super(AddSubjectView, self).form_invalid(form)


class ManageStaff(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Staff
    template_name = 'admin/manage_staff.html'
    context_object_name = 'staff_obj'
    form_class = ManageStaffForm
    extra_context = {'page_header_title': 'Manage Staff'}


class ManageStudents(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Student
    template_name = 'admin/manage_students.html'
    context_object_name = 'students_obj'
    form_class = ManageStudentsForm
    extra_context = {'page_header_title': 'Manage Students'}


class ManageSubjects(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Subject
    template_name = 'admin/manage_subjects.html'
    context_object_name = 'subjects_obj'
    form_class = ManageSubjectsForm
    extra_context = {'page_header_title': 'Manage Subjects'}


class ManageCourses(LoginRequiredMixin, AdminCheckMixin, ListView):
    model = Course
    template_name = 'admin/manage_courses.html'
    context_object_name = 'courses_obj'
    form_class = ManageCoursesForm
    extra_context = {'page_header_title': 'Manage Courses'}


class EditStaff(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = get_user_model()
    template_name = 'admin/edit_staff.html'
    context_object_name = 'user_obj'
    form_class = EditStaffForm
    extra_context = {'page_header_title': 'Edit Staff'}

    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=user_id)

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.staff.address = form.cleaned_data.get('address')
        user.save()
        messages.success(self.request, "Staff Update Successful")
        return super(EditStaff, self).form_valid(form)


class EditStudent(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = get_user_model()
    template_name = 'admin/edit_student.html'
    context_object_name = 'user_obj'
    form_class = EditStudentForm
    extra_context = {
        'page_header_title': 'Edit Student',
        'course_obj': Course.objects.all()
    }

    def get_object(self):
        user_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=user_id)

    def form_valid(self, form):
        user = form.save()
        user.refresh_from_db()
        user.student.address = form.cleaned_data.get('address')
        user.student.profile_pic = form.cleaned_data.get('profile_pic')
        user.save()
        messages.success(self.request, "Student Update Successful")
        return super(EditStudent, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Student Update Failed")
        return super(EditStudent, self).form_valid(form)


class EditSubject(LoginRequiredMixin, AdminCheckMixin, UpdateView):
    model = Subject
    form_class = EditSubjectForm
    template_name = 'admin/edit_subject.html'
    context_object_name = 'subject_obj'
    extra_context = {
        'course_obj': Course.objects.all(),
        'staff_obj': CustomUserProfile.objects.filter(user_level=2),
    }

    def get_object(self, queryset=None):
        subject_id = self.kwargs.get('id')
        return get_object_or_404(Subject, id=subject_id)

    def form_valid(self, form):
        subject = form.save()
        subject.save()
        messages.success(self.request, "Subject Update Successful")
        return super(EditSubject, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Subject Update Failed")
        return super(EditSubject, self).form_valid(form)


class DeleteStudent(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = get_user_model()
    template_name = 'admin/delete_student.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('manage-students')
    login_url = 'login'

    def get_object(self, queryset=None):
        student_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=student_id)


class DeleteSubject(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = Subject
    template_name = 'admin/delete_subject.html'
    context_object_name = 'subject_obj'
    success_url = reverse_lazy('manage-subjects')
    login_url = 'login'

    def get_object(self, queryset=None):
        subject_id = self.kwargs.get('id')
        return get_object_or_404(Subject, id=subject_id)


class DeleteStaff(LoginRequiredMixin, AdminCheckMixin, DeleteView):
    model = get_user_model()
    template_name = 'admin/delete_staff.html'
    context_object_name = 'staff_obj'
    success_url = reverse_lazy('manage-staff')
    login_url = 'login'

    def get_object(self, queryset=None):
        staff_id = self.kwargs.get('id')
        return get_object_or_404(get_user_model(), id=staff_id)


