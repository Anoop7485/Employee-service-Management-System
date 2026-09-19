from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import viewsets
from departments.models import Department
from services.models import Service
from service_requests.models import ServiceRequest
from .forms import DepartmentForm, EmployeeForm, RegisterForm, ServiceForm
from .serializers import EmployeeSerializer
from .models import Employee


class EmployeeAuthForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            employee = Employee.objects.select_related("user").filter(emp_id=username).first()
            if employee and employee.user:
                return employee.user.username
        return username

    def get_user(self):
        username = self.cleaned_data.get("username")
        if username:
            try:
                employee = Employee.objects.select_related("user").get(emp_id=username)
                return employee.user
            except Employee.DoesNotExist:
                pass
        return super().get_user()


@login_required(login_url="login")
def dashboard_view(request):
    employee = getattr(request.user, "employee_profile", None)
    service_requests = ServiceRequest.objects.select_related("employee", "employee__department", "service", "service__department").order_by("-created_at")

    if employee and not request.user.is_staff:
        service_requests = service_requests.filter(employee=employee)

    open_count = service_requests.filter(status="OPEN").count() if employee else 0
    resolved_count = service_requests.filter(status="RESOLVED").count() if employee else 0

    context = {
        "service_requests": service_requests[:5],
        "employee": employee,
        "open_count": open_count,
        "resolved_count": resolved_count,
    }

    if request.user.is_staff:
        context["staff_overview"] = True
        context["staff_total"] = service_requests.count()
        context["staff_open_count"] = service_requests.filter(status="OPEN").count()
        context["staff_in_progress_count"] = service_requests.filter(status="INPROGRESS").count()
        context["staff_resolved_count"] = service_requests.filter(status="RESOLVED").count()

    return render(request, "dashboard.html", context)


@login_required(login_url="login")
def departments_view(request):
    departments = Department.objects.all().order_by("name")

    if request.user.is_staff and request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            Department.objects.create(name=name, description=description)
            messages.success(request, "Department added successfully.")
            return redirect("departments")
        messages.error(request, "Department name is required.")

    return render(request, "departments.html", {
        "departments": departments,
        "can_manage": request.user.is_staff,
    })


@login_required(login_url="login")
def services_view(request):
    services = Service.objects.select_related("department").order_by("name")

    if request.user.is_staff and request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        department_id = request.POST.get("department")
        if name and department_id:
            department = Department.objects.get(pk=department_id)
            Service.objects.create(name=name, description=description, department=department)
            messages.success(request, "Service added successfully.")
            return redirect("services")
        messages.error(request, "Service name and department are required.")

    return render(request, "services.html", {
        "services": services,
        "departments": Department.objects.all().order_by("name"),
        "can_manage": request.user.is_staff,
    })


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def delete_department_view(request, department_id):
    if request.method == "POST":
        department = Department.objects.filter(pk=department_id).first()
        if department:
            department.delete()
            messages.success(request, "Department deleted successfully.")
    return redirect("departments")


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def delete_service_view(request, service_id):
    if request.method == "POST":
        service = Service.objects.filter(pk=service_id).first()
        if service:
            service.delete()
            messages.success(request, "Service deleted successfully.")
    return redirect("services")


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def edit_department_view(request, department_id):
    department = get_object_or_404(Department, pk=department_id)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department updated successfully.")
        return redirect("departments")
    return render(request, "edit_resource.html", {
        "form": form,
        "resource_label": "Department",
        "back_url": "departments",
    })


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Service updated successfully.")
        return redirect("services")
    return render(request, "edit_resource.html", {
        "form": form,
        "resource_label": "Service",
        "back_url": "services",
    })


@login_required(login_url="login")
def service_requests_view(request):
    employee = getattr(request.user, "employee_profile", None)
    requests = ServiceRequest.objects.select_related("employee", "service", "service__department").order_by("-created_at")

    if employee:
        requests = requests.filter(employee=employee)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        service_id = request.POST.get("service")
        priority = request.POST.get("priority", "MEDIUM")

        if title and description and service_id and employee:
            service = Service.objects.get(pk=service_id)
            ServiceRequest.objects.create(
                ticket_number=f"SR-{ServiceRequest.objects.count() + 1010}",
                employee=employee,
                service=service,
                title=title,
                description=description,
                priority=priority,
                status="ASSIGNED",
            )
            messages.success(request, "Your service request was created successfully.")
            return redirect("service_requests")

        messages.error(request, "Please complete all fields and make sure your employee profile exists.")

    return render(request, "service_requests.html", {
        "requests": requests,
        "services": Service.objects.select_related("department").order_by("name"),
    })


@login_required(login_url="login")
def team_view(request):
    employee = getattr(request.user, "employee_profile", None)

    if not request.user.is_staff:
        own_requests = ServiceRequest.objects.select_related("employee", "service", "service__department")
        if employee:
            own_requests = own_requests.filter(employee=employee).order_by("-created_at")
        else:
            own_requests = own_requests.none()

        return render(request, "team.html", {
            "employee": employee,
            "requests": own_requests,
            "is_staff_view": False,
        })

    employees = Employee.objects.select_related("department").order_by("name")
    return render(request, "team.html", {"employees": employees, "is_staff_view": True})


@login_required(login_url="login")
def reports_view(request):
    all_requests = ServiceRequest.objects.select_related("employee", "service", "service__department", "employee__department").order_by("-created_at")
    total = all_requests.count()
    open_count = all_requests.filter(status="OPEN").count()
    assigned_count = all_requests.filter(status="ASSIGNED").count()
    resolved_count = all_requests.filter(status="RESOLVED").count()

    department_status_summary = []
    for department in Department.objects.all().order_by("name"):
        department_requests = all_requests.filter(employee__department=department)
        department_status_summary.append({
            "name": department.name,
            "total": department_requests.count(),
            "open": department_requests.filter(status="OPEN").count(),
            "assigned": department_requests.filter(status="ASSIGNED").count(),
            "resolved": department_requests.filter(status="RESOLVED").count(),
        })

    return render(request, "reports.html", {
        "requests": all_requests[:10],
        "all_requests": all_requests,
        "total": total,
        "open_count": open_count,
        "assigned_count": assigned_count,
        "resolved_count": resolved_count,
        "department_status_summary": department_status_summary,
    })


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def update_service_request_status(request, request_id):
    if request.method == "POST":
        new_status = request.POST.get("status", "").upper()
        service_request = ServiceRequest.objects.filter(pk=request_id).first()
        if service_request and new_status in dict(ServiceRequest.STATUS_CHOICES):
            service_request.status = new_status
            if new_status == "RESOLVED":
                service_request.resolved_at = timezone.now()
            elif new_status == "CLOSED":
                service_request.closed_at = timezone.now()
            service_request.save(update_fields=["status", "resolved_at", "closed_at", "updated_at"])
            messages.success(request, f"Service request {service_request.ticket_number} marked as {new_status}.")
        else:
            messages.error(request, "Please choose a valid status.")
    return redirect("reports")


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def admin_employees_view(request):
    employees = Employee.objects.select_related("department").order_by("name")
    return render(request, "admin_employees.html", {"employees": employees})


@user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")
def edit_employee_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    form = EmployeeForm(request.POST or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Employee updated successfully.")
        return redirect("admin_employees")
    return render(request, "edit_resource.html", {
        "form": form,
        "resource_label": "Employee",
        "back_url": "admin_employees",
    })


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "auth_register.html", {"form": form})


def admin_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None and user.is_staff:
                login(request, user)
                return redirect("dashboard")
            form.add_error(None, "Admin access only.")
    else:
        form = AuthenticationForm()

    return render(request, "auth_admin_login.html", {"form": form})


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

