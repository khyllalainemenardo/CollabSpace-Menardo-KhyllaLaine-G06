from django import forms
from django.utils import timezone
from accounts.models import User
from .models import Project, Task


class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role="MEMBER"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "members"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "due_date", "assigned_to"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only members of this project can be assigned
        self.fields["assigned_to"].queryset = project.members.all()

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        if due_date and "due_date" in self.changed_data and due_date < timezone.localdate():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date