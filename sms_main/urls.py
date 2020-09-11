from django.contrib.auth.forms import AuthenticationForm
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as user_views
from . import admin_views
from . import staff_views
from . import student_views

urlpatterns = [
    path('', user_views.Demo.as_view(), name='demo'),
    path('register/', user_views.RegisterView.as_view(template_name='registration/register.html'), name='register'),
    path('account/<int:pk>/', user_views.UserDetailView.as_view(), name='user-detail'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', user_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin_views.AdminDashboardView.as_view(), name='admin'),
    path('admin/staff/new', admin_views.AddStaffView.as_view(), name='add-staff'),
    path('admin/student/new/', admin_views.AddStudentView.as_view(), name='add-student'),
    path('admin/courses/new/', admin_views.AddCourseView.as_view(), name='add-course'),
    path('admin/subjects/new/', admin_views.AddSubjectView.as_view(), name='add-subject'),
    path('admin/section/new/', admin_views.AddSectionView.as_view(), name='add-section'),
    path('admin/schoolyear/new/', admin_views.AddSchoolYearView.as_view(), name='add-school-year'),
    path('admin/ajax/getsubjects/', admin_views.AjaxGetSubjects.as_view(), name='ajax-get-subjects'),
    path('admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/manage/staff/', admin_views.ManageStaffView.as_view(), name='manage-staff'),
    path('admin/manage/students/', admin_views.ManageStudentsView.as_view(), name='manage-students'),
    path('admin/manage/subjects/', admin_views.ManageSubjectsView.as_view(), name='manage-subjects'),
    path('admin/manage/courses/', admin_views.ManageCoursesView.as_view(), name='manage-courses'),
    path('admin/manage/schoolyear/', admin_views.ManageSchoolYearView.as_view(), name='manage-school-years'),
    path('admin/manage/staff/<int:id>/edit/', admin_views.EditStaffView.as_view(), name='edit-staff'),
    path('admin/manage/student/<int:id>/edit/', admin_views.EditStudentView.as_view(), name='edit-student'),
    path('admin/manage/subject/<int:id>/edit/', admin_views.EditSubjectView.as_view(), name='edit-subject'),
    path('admin/manage/course/<int:id>/edit/', admin_views.EditCourseView.as_view(), name='edit-course'),
    path('admin/manage/schoolyear/<int:id>/edit/', admin_views.EditSchoolYearView.as_view(), name='edit-school-year'),
    path('admin/manage/staff/<int:id>/delete/', admin_views.DeleteStaffView.as_view(), name='delete-staff'),
    path('admin/manage/student/<int:id>/delete/', admin_views.DeleteStudentView.as_view(), name='delete-student'),
    path('admin/manage/subject/<int:id>/delete/', admin_views.DeleteSubjectView.as_view(), name='delete-subject'),
    path('admin/manage/course/<int:id>/delete/', admin_views.DeleteCourseView.as_view(), name='delete-course'),
    path('admin/manage/schoolyear/<int:id>/delete/', admin_views.DeleteSchoolYearView.as_view(), name='delete-school-year'),
    path('admin/', admin_views.DeleteSchoolYearView.as_view(), name='view-staff-feedback'),
    path('admin/', admin_views.DeleteSchoolYearView.as_view(), name='view-student-feedback'),
    path('staff/dashboard/', staff_views.StaffDashboardView.as_view(), name='staff-dashboard'),
    path('staff/dashboard/attendance', staff_views.CreateStudentAttendanceView.as_view(), name='view-student-attendance'),
    path('staff/dashboard/attendance/report/u/<int:id>/', staff_views.StudentAttendanceReport.as_view(), name='view-student-attendance-report'),
    path('staff/dashboard/attendance/report/list/', staff_views.AjaxFetchAttendanceList.as_view(), name='ajax-staff-fetch-attendance-report'),
    path('staff/dashboard/attendance/report/', staff_views.AjaxViewAttendance.as_view(), name='ajax-view-student-attendance'),
    path('staff/dashboard/attendance/report/update', staff_views.AjaxUpdateAttendance.as_view(), name='ajax-update-student-attendance-report'),
    path('staff/students/fetch/', staff_views.AjaxFetchStudents.as_view(), name='ajax-staff-fetch-students'),
    path('admin/section/fetch/', staff_views.AjaxFetchSections.as_view(), name='ajax-admin-fetch-sections'),
    path('staff/section/fetch/', staff_views.AjaxFetchSections.as_view(), name='ajax-staff-fetch-sections'),
    path('staff/leave/', staff_views.LeaveApplicationView.as_view(), name='staff-leave-application'),
    path('staff/leave/report', staff_views.LeaveReportView.as_view(), name='staff-leave-report'),
    path('staff/leave/feedback', staff_views.StaffFeedBackView.as_view(), name='staff-feedback'),
    path('staff/leave/feedback/edit/<int:id>', staff_views.StaffEditFeedBackView.as_view(), name='staff-edit-feedback'),
    path('student/dashboard/', student_views.StudentDashboardView.as_view(), name='student-dashboard'),

]
