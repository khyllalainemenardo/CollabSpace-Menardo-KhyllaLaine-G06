from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("accounts:login")
        messages.error(request, "Please correct the errors below.")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")