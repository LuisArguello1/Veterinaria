from django.shortcuts import render
from django.contrib import messages

def Dashboard(request):
    messages.debug(request, 'Mensaje de depuración (debug).')
    messages.info(request, 'Mensaje informativo (info).')
    messages.success(request, 'Mensaje de éxito (success).')
    messages.warning(request, 'Mensaje de advertencia (warning).')
    messages.error(request, 'Mensaje de error (error).')
    return render(request, 'layouts/dashboard.html')