from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.autenticacion.forms.password_recovery_form import PasswordRecoveryRequestForm, PasswordRecoveryConfirmForm


class PasswordRecoveryRequestView(PasswordResetView):
    """Vista para solicitar recuperación de contraseña"""
    template_name = 'autenticacion/password_recovery/request.html'
    form_class = PasswordRecoveryRequestForm
    email_template_name = 'autenticacion/password_recovery/email.txt'
    html_email_template_name = 'autenticacion/password_recovery/email.html'
    subject_template_name = 'autenticacion/password_recovery/email_subject.txt'
    success_url = reverse_lazy('auth:password_recovery_done')
    
    def form_valid(self, form):
        """Procesa el formulario válido y envía el email"""
        messages.success(
            self.request,
            'Si el correo electrónico existe en nuestro sistema, recibirás instrucciones para restablecer tu contraseña.'
        )
        return super().form_valid(form)


class PasswordRecoveryDoneView(PasswordResetDoneView):
    """Vista que confirma que se envió el email"""
    template_name = 'autenticacion/password_recovery/done.html'


class PasswordRecoveryConfirmView(PasswordResetConfirmView):
    """Vista para establecer nueva contraseña usando el token"""
    template_name = 'autenticacion/password_recovery/confirm.html'
    form_class = PasswordRecoveryConfirmForm
    success_url = reverse_lazy('auth:password_recovery_complete')
    
    def form_valid(self, form):
        """Procesa el formulario válido"""
        messages.success(
            self.request,
            '¡Tu contraseña ha sido restablecida exitosamente! Ahora puedes iniciar sesión con tu nueva contraseña.'
        )
        return super().form_valid(form)


class PasswordRecoveryCompleteView(PasswordResetCompleteView):
    """Vista que confirma que la contraseña fue restablecida"""
    template_name = 'autenticacion/password_recovery/complete.html'
