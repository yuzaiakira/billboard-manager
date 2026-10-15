from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from account.forms import UserRegisterForm
from siteoption.constants import SITE_NAME
from siteoption.utils.functions import get_option


# Create your views here.


class Login(LoginView):
    template_name = 'template/account/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Django's LoginView sets context["site_name"] = current_site.name (domain like 127.0.0.1:8001).
        # Override with our site option so header/footer show the real site name.
        context["site_name"] = get_option(SITE_NAME, default="siteName")
        return context

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))


class Register(SuccessMessageMixin, CreateView):
    template_name = 'template/account/register.html'
    success_url = reverse_lazy('login')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"


class Logout(LogoutView):
    def get_success_url(self):
        return reverse_lazy('home')
