from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.db.models import DateTimeField
from django.http import HttpResponseRedirect

from .models import (Student,
                     Staff,
                     AdminHOD,
                     Subject,
                     Course,
                     Attendance,
                     StaffFeedBack,
                     StaffNotification,
                     StudentFeedBack,
                     LeaveReportStaff,
                     AttendanceReport,
                     CustomUserProfile)


def get_course_set():
    queryset = Course.objects.all().order_by('course_name')
    return queryset


def get_staff_set():
    queryset = CustomUserProfile.objects.filter(user_level=2)
    return queryset


class LoginForm(AuthenticationForm):
    user_level = forms.CharField(max_length=1, required=True)

    class Meta:
        fields = '__all__'

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user_level = self.cleaned_data.get('user_level')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                messages.error(self.request, 'Invalid username or password')
                raise forms.ValidationError('Invalid username or password')
            elif not str(user_level) == str(user.user_level):
                print("User level mismatch")
                messages.error(self.request, 'Invalid login')
                raise forms.ValidationError('Invalid Login')

        return super(LoginForm, self).clean(*args, **kwargs)


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUserProfile
        fields = (
            'first_name',
            'middle_initial',
            'last_name',
            'email',
            'password1',
            'password2'
        )


class UserDetailForm(forms.ModelForm):
    class Meta:
        model: CustomUserProfile
        fields = (
            'first_name',
            'middle_initial',
            'last_name',
            'email',
            'user_level',
            'is_staff',
            'is_active'
        )


class RegisterStaffForm(RegistrationForm):
    address = forms.CharField(max_length=255, widget=forms.TextInput())

    # Override the default value of the user_level from 1 to 2
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_level'].initial = 2

    class Meta:
        model = get_user_model()
        fields = (
            'first_name',
            'middle_initial',
            'last_name',
            'email',
            'address',
            'user_level',
            'password1',
            'password2'
        )


class ModifiedCourseChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.course_name


class ModifiedStaffChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.staff_id


class RegisterStudentForm(RegistrationForm):
    gender = forms.CharField(max_length=1)
    address = forms.CharField(max_length=255, widget=forms.TextInput())
    course_id = ModifiedCourseChoiceField(
        queryset=Course.objects.all().order_by('course_name'),
        to_field_name='id',
        empty_label='Select a Course',
    )

    def clean_address(self):
        data = self.cleaned_data['address']
        if data == '':
            data = 'Unspecified'
        return data

    # Override the default value of the user_level from 1 to 2
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_level'].initial = 3
        self.fields['course_id'].widget.attrs['class'] = "form-control"
        self.fields['gender'].choices = (('', 'Select a Gender'), ('M', 'Male'), ('F', 'Female'))
        self.fields['session_start'] = forms.DateTimeField()
        self.fields['session_end'] = forms.DateTimeField()
        self.fields['session_start'].initial = datetime.now
        self.fields['session_end'].initial = datetime.now

    class Meta:
        model = get_user_model()
        fields = (
            'first_name',
            'middle_initial',
            'last_name',
            'email',
            'password1',
            'password2',
            'user_level',
            'gender',
            'address',
            'course_id',
            'profile_pic',
        )


class AddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'course_name',
        )


class AddSubjectForm(forms.ModelForm):
    # course_id = ModifiedCourseChoiceField(
    #     queryset=Course.objects.all().order_by('course_name'),
    #     # queryset=Course.objects.all(),
    #     to_field_name='id',
    #     empty_label='Select a Course',
    # )

    course_id = forms.ModelChoiceField(
        get_course_set()
    )

    staff_id = forms.ModelChoiceField(
        get_staff_set()
    )

    class Meta:
        model = Subject
        fields = (
            'subject_name',
            'course_id',
            'staff_id',
        )
        # fields = '__all__'


# class RegisterStudentForm(forms.ModelForm):
#     class Meta:
#         model = get_user_model()
#         fields = '__all__'

# class AdminHODForm(forms.ModelForm):
#     class Meta:
#         model = AdminHOD
#
#
# class StaffForm(forms.ModelForm):
#     class Meta:
#         model = Staff
#
#
# class CourseForm(forms.ModelForm):
#     class Meta:
#         model = Course
#
#
# class SubjectForm(forms.ModelForm):
#     class Meta:
#         model = Subject


class ManageStaffForm(forms.ModelForm):
    class Meta:
        model = CustomUserProfile

        fields = '__all__'


class ManageStudentsForm(forms.ModelForm):
    class Meta:
        model = CustomUserProfile

        fields = '__all__'


class ManageSubjectsForm(forms.ModelForm):
    class Meta:
        model = Subject

        fields = '__all__'


class ManageCoursesForm(forms.ModelForm):
    class Meta:
        model = Course

        fields = '__all__'


class EditStaffForm(forms.ModelForm):
    address = forms.CharField()

    class Meta:
        model = get_user_model()

        fields = (
            'first_name',
            'middle_initial',
            'middle_initial',
            'last_name',
            'email',
            'address',
            'user_level'
        )


class EditStudentForm(forms.ModelForm):
    gender = forms.CharField(max_length=1)
    address = forms.CharField()
    # course_id = ModifiedCourseChoiceField(
    #     queryset=Course.objects.all().order_by('course_name'),
    #     to_field_name='id',
    #     empty_label='Select a Course',
    # )
    course_id = forms.ModelChoiceField(
        get_course_set()
    )
    session_start = forms.DateTimeField()
    session_end = forms.DateTimeField()
    date_created = forms.DateTimeField()
    date_updated = forms.DateTimeField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = (('', 'Select a Gender'), ('M', 'Male'), ('F', 'Female'))

    def clean_profile_pic(self):
        data = self.cleaned_data['profile_pic']
        if data == '':
            data = '/default.png'
        return data

    class Meta:
        model = get_user_model()

        fields = (
            'first_name',
            'middle_initial',
            'middle_initial',
            'last_name',
            'gender',
            'email',
            'address',
            'user_level',
            'profile_pic',
            'course_id',
            'session_start',
            'session_end',
            'date_created',
        )


class EditSubjectForm(forms.ModelForm):
    course_id = forms.ModelChoiceField(
        get_course_set()
    )
    staff_id = forms.ModelChoiceField(
        get_staff_set()
    )

    class Meta:
        model = Subject

        fields = (
            'subject_name',
            'course_id',
            'staff_id'
        )

