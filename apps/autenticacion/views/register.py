from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages

from apps.autenticacion.forms.users_form import RegisterForm


class RegisterView(FormView):
    template_name = 'autenticacion/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('auth:Dashboard')

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        user.save()
        messages.success(self.request, 'Cuenta creada. Por favor inicia sesión.')
        return super().form_valid(form)