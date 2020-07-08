from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth import get_user_model


# from .forms import LoginForm, RegistrationForm
from .forms import RegistrationForm, LoginForm


class Demo(TemplateView):
    template_name = 'sms_main/demo.html'


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    extra_context = {'page_title': 'User Login'}


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    context_object_name = 'form'
    success_url = reverse_lazy('login')
    extra_context = {'page_title': 'User Registration'}


class UserDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    context_object_name = 'user_obj'
    template_name = 'sms_main/user_detail.html'
    extra_context = {'page_title': 'User Detail'}

    # def get_queryset(self):
    #     queryset = get_user_model().objects.filter(pk=self.kwargs['pk'])
    #     return queryset

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(get_user_model(), id=user_id)




















