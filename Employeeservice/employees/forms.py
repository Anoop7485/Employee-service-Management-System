from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from departments.models import Department
from services.models import Service
from .models import Employee


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    emp_id = forms.CharField(max_length=20)
    name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=100)
    designation = forms.CharField(max_length=100)
    department = forms.ModelChoiceField(queryset=Department.objects.all())

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "emp_id",
            "name",
            "phone",
            "designation",
            "department",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()

        Employee.objects.create(
            emp_id=self.cleaned_data["emp_id"],
            name=self.cleaned_data["name"],
            email=self.cleaned_data["email"],
            phone=self.cleaned_data["phone"],
            designation=self.cleaned_data["designation"],
            department=self.cleaned_data["department"],
            user=user,
            account_created=True,
        )
        return user


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "description")


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ("name", "description", "department", "is_active")


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ("emp_id", "name", "email", "phone", "designation", "department")
