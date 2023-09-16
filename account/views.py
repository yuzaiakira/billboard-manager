from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy


# Create your views here.


class Login(LoginView):
    template_name = 'template/account/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))


class Logout(LogoutView):
    def get_success_url(self):
        return reverse_lazy('home')
