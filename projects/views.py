from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import role_required
from .forms import ProjectForm, TaskForm
from .models import Project, Task


# ---------- Projects ----------

@login_required
def project_list(request):
    if request.user.role == "LEADER":
        projects = Project.objects.filter(owner=request.user)
    else:
        projects = request.user.projects.all()
    return render(request, "projects/project_list.html", {"projects": projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Only the owner or a member can open the project
    if project.owner != request.user and request.user not in project.members.all():
        messages.error(request, "You are not part of that project.")
        return redirect("projects:project_list")
    return render(request, "projects/project_detail.html", {"project": project})


@role_required("LEADER")
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        form.save_m2m()
        messages.success(request, "Project created.")
        return redirect("projects:project_detail", pk=project.pk)
    return render(request, "projects/form.html", {"form": form, "title": "New Project"})


@role_required("LEADER")
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "Project updated.")
        return redirect("projects:project_detail", pk=project.pk)
    return render(request, "projects/form.html", {"form": form, "title": "Edit Project"})


@role_required("LEADER")
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted.")
        return redirect("projects:project_list")
    return render(request, "projects/confirm_delete.html", {"object": project})


# ---------- Tasks ----------

@role_required("LEADER")
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    form = TaskForm(request.POST or None, project=project)
    if form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        messages.success(request, "Task added.")
        return redirect("projects:project_detail", pk=project.pk)
    return render(request, "projects/form.html", {"form": form, "title": "New Task"})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    is_owner = task.project.owner == request.user
    is_assignee = task.assigned_to == request.user
    if not (is_owner or is_assignee):
        messages.error(request, "You can only update tasks assigned to you.")
        return redirect("projects:project_list")

    form = TaskForm(request.POST or None, instance=task, project=task.project)
    if not is_owner:
        # Members can only change the status of their own task
        for name in ["title", "description", "due_date", "assigned_to"]:
            form.fields[name].disabled = True

    if form.is_valid():
        form.save()
        messages.success(request, "Task updated.")
        return redirect("projects:project_detail", pk=task.project.pk)
    return render(request, "projects/form.html", {"form": form, "title": "Edit Task"})


@role_required("LEADER")
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, project__owner=request.user)
    if request.method == "POST":
        project_pk = task.project.pk
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("projects:project_detail", pk=project_pk)
    return render(request, "projects/confirm_delete.html", {"object": task})