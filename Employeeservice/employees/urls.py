from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeAuthForm,
    EmployeeViewSet,
    admin_employees_view,
    admin_login_view,
    dashboard_view,
    delete_department_view,
    delete_service_view,
    edit_department_view,
    edit_employee_view,
    edit_service_view,
    departments_view,
    logout_view,
    register_view,
    reports_view,
    service_requests_view,
    services_view,
    team_view,
    update_service_request_status,
)

router = DefaultRouter()
router.register("employees", EmployeeViewSet)

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("departments/", departments_view, name="departments"),
    path("departments/<int:department_id>/delete/", delete_department_view, name="delete_department"),
    path("departments/<int:department_id>/edit/", edit_department_view, name="edit_department"),
    path("services/", services_view, name="services"),
    path("services/<int:service_id>/delete/", delete_service_view, name="delete_service"),
    path("services/<int:service_id>/edit/", edit_service_view, name="edit_service"),
    path("requests/", service_requests_view, name="service_requests"),
    path("team/", team_view, name="team"),
    path("reports/", reports_view, name="reports"),
    path("requests/<int:request_id>/status/", update_service_request_status, name="update_service_request_status"),
    path("staff/employees/", admin_employees_view, name="admin_employees"),
    path("staff/employees/<int:employee_id>/edit/", edit_employee_view, name="edit_employee"),
    path("", dashboard_view, name="home"),
    path("login/", auth_views.LoginView.as_view(template_name="auth_login.html", authentication_form=EmployeeAuthForm), name="login"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html",
        email_template_name="registration/password_reset_email.html",
        success_url="/password-reset/done/",
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="registration/password_reset_done.html"
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="registration/password_reset_confirm.html",
        success_url="/reset/done/",
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),
    path("admin-login/", admin_login_view, name="admin_login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    *router.urls,
]
