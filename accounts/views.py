from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from projects.models import Project, Task
from .decorators import role_required
from .forms import RegisterForm, ProfileForm
from django.db.models import Count, Q


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
    if request.user.role == "LEADER":
        return redirect("accounts:leader_dashboard")
    return redirect("accounts:member_dashboard")


@role_required("LEADER")
def leader_dashboard(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, "accounts/leader_dashboard.html", {"projects": projects})


@role_required("MEMBER")
def member_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user).exclude(status="DONE")
    return render(request, "accounts/member_dashboard.html", {"tasks": tasks})


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"profile_user": request.user})


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
        messages.error(request, "Please correct the errors below.")
    return render(request, "accounts/profile_edit.html", {"form": form})