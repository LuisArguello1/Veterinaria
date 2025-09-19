# views.py
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from apps.autenticacion.forms.users_form import RegisterForm


class RegisterView(FormView):
    template_name = 'autenticacion/register.html'
    form_class = RegisterForm
    # Si tu mensaje dice "Por favor inicia sesión", redirige al login:
    success_url = reverse_lazy('auth:login')

    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, no debe ver /register
        if request.user.is_authenticated:
            return redirect('dashboard')  # usa el name real de tu dashboard
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        password = form.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        user.save()

        messages.success(self.request, 'Cuenta creada. Por favor inicia sesión.')
        return super().form_valid(form)
