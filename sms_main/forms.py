from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.db.models import DateTimeField
from django.http import HttpResponseRedirect

from django.utils.translation import gettext_lazy as _

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
                     CustomUserProfile, SchoolYearModel, CourseSection)


def get_sy_set():
    queryset = SchoolYearModel.objects.all().order_by('-id')
    return queryset


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


class ModifiedSchoolYearChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.school_year_start}-{obj.school_year_end}"


class ModifiedStaffChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.staff_id


class ModifiedSectionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.section_name


class RegisterStudentForm(RegistrationForm):
    gender = forms.CharField(max_length=1, widget=forms.Select())
    year_level = forms.CharField(max_length=3, widget=forms.Select(), empty_value="Select a Year Level")
    section = ModifiedSectionChoiceField(
        queryset=CourseSection.objects.all().order_by('-section_name'),
        to_field_name='id',
        empty_label='-Select a Section-'
    )
    address = forms.CharField(max_length=255, widget=forms.TextInput())
    course_id = ModifiedCourseChoiceField(
        queryset=Course.objects.all().order_by('course_name'),
        to_field_name='id',
        empty_label='Select a Course',
    )
    subject_choices = Subject.objects.all()
    subject_list = forms.ModelMultipleChoiceField(queryset=subject_choices, widget=forms.CheckboxSelectMultiple)
    stat = forms.CharField(max_length=255)
    school_year = ModifiedSchoolYearChoiceField(
        queryset=SchoolYearModel.objects.all().order_by('id'),
        to_field_name='id',
        empty_label='Select a School Year',
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
        self.fields['gender'].choices = (('', '-Select a Gender-'), ('M', 'Male'), ('F', 'Female'))
        self.fields['year_level'].choices = Student.Levels.choices

    class Meta:
        model = get_user_model()
        fields = (
            'first_name',
            'middle_initial',
            'last_name',
            'email',
            'password1',
            'password2',
            'year_level',
            'section',
            'user_level',
            'gender',
            'address',
            'course_id',
            'subject_list',
            'school_year',
            'stat',
            'profile_pic',
        )


class AddCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'course_name',
        )

    def clean_course_name(self):
        new_course_name = self.cleaned_data['course_name']
        if Course.objects.filter(course_name=new_course_name).exists():
            raise forms.ValidationError('Course already exists')
        return new_course_name


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

    def clean(self, *args, **kwargs):
        cleaned_data = super(AddSubjectForm, self).clean()
        new_subject_name = cleaned_data['subject_name']
        staff = cleaned_data['staff_id']
        course = cleaned_data['course_id']
        if Subject.objects.filter(subject_name=new_subject_name, staff_id=staff).exists() or Subject.objects.filter(subject_name=new_subject_name, course_id=course).exists():
            print(staff)
            raise forms.ValidationError(_('Subject already exists'))

        return cleaned_data


class AddSectionForm(forms.ModelForm):
    class Meta:
        model = CourseSection
        fields = '__all__'


class AddSchoolYearForm(forms.ModelForm):
    class Meta:
        model = SchoolYearModel
        fields = '__all__'



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
    school_year = forms.ModelChoiceField(
        get_sy_set()
    )

    # date_created = forms.DateTimeField()
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
            'last_name',
            'gender',
            'email',
            'address',
            'user_level',
            'profile_pic',
            'course_id',
            'school_year',
            'date_updated'
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


class EditCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'


class EditSchoolYearForm(forms.ModelForm):
    class Meta:
        model = SchoolYearModel
        fields = '__all__'

