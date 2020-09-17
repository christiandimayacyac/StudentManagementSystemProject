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
                raise ValidationError(_('Invalid username or password'), code='invalid')
            elif not str(user_level) == str(user.user_level):
                print("User level mismatch")
                messages.error(self.request, 'Invalid login')
                raise ValidationError(_('Invalid Login'), code='invalid')

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
    gender = forms.CharField(max_length=1)
    year_level = forms.CharField(max_length=3)
    stat = forms.CharField(max_length=1, widget=forms.Select(), empty_value="Select Student Status")
    section = ModifiedSectionChoiceField(
        queryset=CourseSection.objects.all().order_by('-section_name'),
        to_field_name='id',
        empty_label='-Select a Section-',
        required=True,
    )
    address = forms.CharField(max_length=255, widget=forms.TextInput())
    course_id = ModifiedCourseChoiceField(
        queryset=Course.objects.all().order_by('course_name'),
        to_field_name='id',
        empty_label='-Select a Course-',
        required=True
    )
    subject_choices = Subject.objects.all()
    subject_list = forms.ModelMultipleChoiceField(queryset=subject_choices, widget=forms.CheckboxSelectMultiple)
    school_year = ModifiedSchoolYearChoiceField(
        queryset=SchoolYearModel.objects.all().order_by('id'),
        to_field_name='id',
        empty_label='-Select a School Year-',
        required=True
    )

    # Override the default value of the user_level from 1 to 3
    def __init__(self, *args, **kwargs):
        super(RegisterStudentForm, self).__init__(*args, **kwargs)
        gender_options = (('', '-Select a Gender-'), ('M', 'Male'), ('F', 'Female'))

        self.fields['user_level'].initial = 3
        self.fields['course_id'].widget.attrs['class'] = "form-control"
        self.fields['course_id'].widget.attrs['id'] = "course_id"
        self.fields['school_year'].widget.attrs['class'] = "form-control"
        self.fields['year_level'] = forms.ChoiceField(
            choices=Student.Levels.choices,
            initial='',
            widget=forms.Select(attrs={'class': 'form-control'}),
            required=True
        )
        self.fields['gender'] = forms.ChoiceField(
            choices=gender_options,
            initial='',
            widget=forms.Select(attrs={'class': 'form-control'}),
            required=True
        )

        self.fields['stat'].choices = Student.Status.choices

    def clean_address(self):
        data = self.cleaned_data['address']
        if data == '':
            data = 'Unspecified'
        return data

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
        if Subject.objects.filter(subject_name=new_subject_name, staff_id=staff,
                                  course_id=course).exists() or Subject.objects.filter(subject_name=new_subject_name,
                                                                                       course_id=course).exists():
            raise forms.ValidationError(_('Subject already exists'))

        return cleaned_data


class AddSectionForm(forms.ModelForm):
    class Meta:
        model = CourseSection
        fields = (
            'section_name',
            'course_id'
        )

    def clean_section_name(self, *args, **kwargs):
        section_name = self.cleaned_data['section_name']
        section_exists = CourseSection.objects.filter(section_name=section_name).exists()
        if section_exists:
            raise ValidationError(_('The section name already exists in the database.'), code='invalid')
        return section_name


class AddSchoolYearForm(forms.ModelForm):
    class Meta:
        model = SchoolYearModel
        fields = '__all__'


class CreateAttendanceForm(forms.ModelForm):
    students = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        student_choices = [(entry.user_profile.id, entry.user_profile.first_name) for entry in
                           Student.objects.all().only('id', 'user_profile')]
        print('student_choices')
        print(student_choices)
        self.fields['students'].choices = student_choices

    class Meta:
        model = Attendance
        fields = (
            'subject_id',
            'section_id',
            'school_year',
            'students'
        )


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
            'staff_id',
            'is_offered'
        )

    def clean_is_offered(self):
        if self.cleaned_data['is_offered']:
            print("checked")
        else:
            print("unchecked")
        return self.cleaned_data['is_offered']


class EditCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'


class EditSchoolYearForm(forms.ModelForm):
    class Meta:
        model = SchoolYearModel
        fields = '__all__'


# class DynamicMultipleChoiceField(forms.MultipleChoiceField):
#     def validate(self, value):
#         if self.required and not value:
#             raise ValidationError(self.error_messages['required'])


# class StudForm(forms.Form):
#     students = DynamicMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=[])
#
#     def filter_students(self, data):
#         students_obj = get_user_model().objects.filter(student__subjects__staff_id=data['staff_id'],
#                                                        student__subjects__id=data['subject_id'],
#                                                        student__school_year__id=data['school_year_id'])
#         self.fields['students'].choices = [(student.pk, student.first_name) for student in students_obj]
#         print("printing choices")
#         print(self.fields['students'].choices)


class LeaveApplicationForm(forms.ModelForm):
    staff_id = forms.IntegerField(widget=forms.TextInput())

    class Meta:
        model = LeaveReportStaff
        fields = (
            'staff_id',
            'leave_date',
            'leave_message'
        )
        exclude = ['leave_status']

    def clean(self, *args, **kwargs):
        print("cleaning all")
        cleaned_data = super(LeaveApplicationForm, self).clean()
        leave_date = self.cleaned_data['leave_date']
        staff_id = self.cleaned_data['staff_id']
        if LeaveReportStaff.objects.filter(staff_id=staff_id, leave_date=leave_date):
            raise ValidationError(_('There is already an existing application on the selected date.'), code='invalid')
        return cleaned_data

    def clean_staff_id(self, *args, **kwargs):
        print("cleaning staff id")
        staff_id = self.cleaned_data['staff_id']
        s_id = Staff.objects.get(user_profile=staff_id)
        if not s_id:
            return ValidationError(_('Invalid staff.'), code='invalid')
        return s_id


class StaffFeedbackForm(forms.ModelForm):
    staff_id = forms.IntegerField(widget=forms.TextInput())

    class Meta:
        model = StaffFeedBack
        fields = (
            'staff_id',
            'feedback'
        )

    def clean_staff_id(self, *args, **kwargs):
        print("cleaning staff id")
        staff_id = self.cleaned_data['staff_id']
        s_id = Staff.objects.get(user_profile=staff_id)
        if not s_id:
            return ValidationError(_('Invalid staff.'), code='invalid')
        return s_id


class StaffEditFeedbackForm(forms.ModelForm):
    staff_id = forms.IntegerField(widget=forms.TextInput())

    class Meta:
        model = StaffFeedBack
        fields = (
            'staff_id',
            'feedback'
        )

    def clean_staff_id(self, *args, **kwargs):
        print("cleaning staff id")
        staff_id = self.cleaned_data['staff_id']
        s_id = Staff.objects.get(user_profile=staff_id)
        if not s_id:
            return ValidationError(_('Invalid staff.'), code='invalid')
        return s_id

    def clean_feedback(self, *args, **kwargs):
        print("cleaning feedback message")
        return self.cleaned_data['feedback']
