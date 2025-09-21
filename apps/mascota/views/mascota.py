from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def main_register(request):

    return render(request, 'main_register.html')