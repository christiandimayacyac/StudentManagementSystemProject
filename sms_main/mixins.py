from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class UserRedirectMixin:
    def get_next_url(self):
        if self.request.user.is_authenticated:
            user_level = self.request.user.user_level
            if user_level == 1:
                return'admin-dashboard'
            elif user_level == 2:
                return 'staff-dashboard'
            elif user_level == 3:
                return 'student-dashboard'
            else:
                return 'logout'
        else:
            return 'login'


class AdminCheckMixin(UserPassesTestMixin, UserRedirectMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.user_level == 1

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())

        redirect_path = self.get_next_url()
        return redirect(redirect_path)


class StaffCheckMixin(UserPassesTestMixin, UserRedirectMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.user_level == 2

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())

        redirect_path = self.get_next_url()
        return redirect(redirect_path)


class StudentCheckMixin(UserPassesTestMixin, UserRedirectMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.user_level == 3

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())

        redirect_path = self.get_next_url()
        return redirect(redirect_path)


