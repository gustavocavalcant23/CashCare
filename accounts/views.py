from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

from .forms import UserForm


class OnBoardingView(FormView):
    template_name = 'accounts/onboarding.html'
    form_class = UserForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user=user)
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('dashboard')
