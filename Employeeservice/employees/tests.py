from django.test import TestCase


class FrontendPagesTest(TestCase):
    def test_login_page_loads(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_team_page_loads_for_authenticated_user(self):
        self.client.force_login(user=self._create_user())
        response = self.client.get("/team/")
        self.assertEqual(response.status_code, 200)

    def test_reports_page_loads_for_authenticated_user(self):
        self.client.force_login(user=self._create_user())
        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 200)

    def test_admin_employees_page_requires_staff(self):
        normal_user = self._create_user()
        self.client.force_login(user=normal_user)
        response = self.client.get("/staff/employees/")
        self.assertEqual(response.status_code, 302)

        staff_user = self._create_user(username="staffer")
        staff_user.is_staff = True
        staff_user.save()
        self.client.force_login(user=staff_user)
        response = self.client.get("/staff/employees/")
        self.assertEqual(response.status_code, 200)

    def test_employee_can_login_with_emp_id(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from employees.models import Employee

        department = Department.objects.create(name="IT", description="IT department")
        user = User.objects.create_user(username="app-user-1001", password="secret123")
        Employee.objects.create(
            emp_id="EMP-1001",
            name="Jane Employee",
            email="jane@example.com",
            phone="123",
            designation="Developer",
            department=department,
            user=user,
            account_created=True,
        )

        response = self.client.post("/login/", {"username": "EMP-1001", "password": "secret123"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_service_request_defaults_to_assigned_and_employee_sees_status(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from employees.models import Employee
        from service_requests.models import ServiceRequest
        from services.models import Service

        department = Department.objects.create(name="Support Desk", description="Support")
        user = User.objects.create_user(username="app-user-assign", password="secret123")
        employee = Employee.objects.create(
            emp_id="EMP-5001",
            name="Assigned User",
            email="assigned@example.com",
            phone="555",
            designation="Analyst",
            department=department,
            user=user,
            account_created=True,
        )
        service = Service.objects.create(name="VPN Issue", description="VPN support", department=department)

        self.client.force_login(user)
        create_response = self.client.post(
            "/requests/",
            {
                "title": "VPN not working",
                "description": "Cannot connect to VPN",
                "service": service.pk,
                "priority": "HIGH",
            },
            follow=True,
        )
        self.assertEqual(create_response.status_code, 200)

        request_obj = ServiceRequest.objects.get(title="VPN not working")
        self.assertEqual(request_obj.status, "ASSIGNED")

        admin_user = User.objects.create_user(username="admin-status-seen", password="secret123")
        admin_user.is_staff = True
        admin_user.save()

        self.client.force_login(admin_user)
        self.client.post(f"/requests/{request_obj.pk}/status/", {"status": "RESOLVED"}, follow=True)

        self.client.force_login(user)
        employee_response = self.client.get("/requests/", follow=True)
        self.assertContains(employee_response, "RESOLVED")

    def test_logout_redirects_to_login_page(self):
        from django.contrib.auth.models import User

        user = User.objects.create_user(username="logoutuser", password="secret123")
        self.client.force_login(user=user)

        response = self.client.get("/logout/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_admin_login_page_loads_and_accepts_staff_user(self):
        from django.contrib.auth.models import User

        response = self.client.get("/admin-login/")
        self.assertEqual(response.status_code, 200)

        staff_user = User.objects.create_user(username="adminuser", password="secret123")
        staff_user.is_staff = True
        staff_user.save()

        login_response = self.client.post("/admin-login/", {"username": "adminuser", "password": "secret123"}, follow=True)
        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.wsgi_request.user.is_authenticated)
        self.assertTrue(login_response.wsgi_request.user.is_staff)

    def test_admin_can_delete_department_and_service(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from services.models import Service

        admin_user = User.objects.create_user(username="admin-delete", password="secret123")
        admin_user.is_staff = True
        admin_user.save()
        self.client.force_login(admin_user)

        department = Department.objects.create(name="IT Support", description="IT")
        service = Service.objects.create(name="Laptop Repair", description="Fix laptop", department=department)

        response_department = self.client.post(f"/departments/{department.pk}/delete/", follow=True)
        self.assertEqual(response_department.status_code, 200)
        self.assertFalse(Department.objects.filter(pk=department.pk).exists())

        response_service = self.client.post(f"/services/{service.pk}/delete/", follow=True)
        self.assertEqual(response_service.status_code, 200)
        self.assertFalse(Service.objects.filter(pk=service.pk).exists())

    def test_employee_dashboard_shows_only_own_requests(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from employees.models import Employee
        from service_requests.models import ServiceRequest
        from services.models import Service

        department = Department.objects.create(name="HR", description="HR department")
        user_one = User.objects.create_user(username="EMP-2001", password="secret123")
        user_two = User.objects.create_user(username="EMP-2002", password="secret123")
        employee_one = Employee.objects.create(
            emp_id="EMP-2001",
            name="A Person",
            email="a@example.com",
            phone="111",
            designation="Analyst",
            department=department,
            user=user_one,
            account_created=True,
        )
        employee_two = Employee.objects.create(
            emp_id="EMP-2002",
            name="B Person",
            email="b@example.com",
            phone="222",
            designation="Analyst",
            department=department,
            user=user_two,
            account_created=True,
        )
        service = Service.objects.create(name="Laptop Support", description="Laptop service", department=department)
        ServiceRequest.objects.create(
            ticket_number="SR-1001",
            employee=employee_one,
            service=service,
            title="My own request",
            description="Should show on dashboard",
            status="RESOLVED",
            priority="HIGH",
        )
        ServiceRequest.objects.create(
            ticket_number="SR-1002",
            employee=employee_two,
            service=service,
            title="Other employee request",
            description="Should not show on dashboard",
            status="OPEN",
            priority="MEDIUM",
        )

        self.client.force_login(user=user_one)
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My own request")
        self.assertNotContains(response, "Other employee request")

    def test_employee_cannot_add_department_or_service(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from services.models import Service

        user = User.objects.create_user(username="EMP-3001", password="secret123")
        self.client.force_login(user)

        department_response = self.client.post("/departments/", {"name": "Finance", "description": "Finance dept"}, follow=True)
        self.assertEqual(department_response.status_code, 200)
        self.assertFalse(Department.objects.filter(name="Finance").exists())
        self.assertNotContains(department_response, "Add department")

        service_response = self.client.post("/services/", {"name": "Payroll", "description": "Pays employees", "department": "1"}, follow=True)
        self.assertEqual(service_response.status_code, 200)
        self.assertFalse(Service.objects.filter(name="Payroll").exists())
        self.assertNotContains(service_response, "Add service")

    def test_admin_can_update_service_request_status(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from employees.models import Employee
        from service_requests.models import ServiceRequest
        from services.models import Service

        admin_user = User.objects.create_user(username="admin-status", password="secret123")
        admin_user.is_staff = True
        admin_user.save()
        self.client.force_login(admin_user)

        department = Department.objects.create(name="Support", description="Support dept")
        employee = Employee.objects.create(
            emp_id="EMP-9001",
            name="Support User",
            email="support@example.com",
            phone="999",
            designation="Analyst",
            department=department,
            user=User.objects.create_user(username="EMP-9001", password="secret123"),
            account_created=True,
        )
        service = Service.objects.create(name="VPN Access", description="VPN service", department=department)
        request_obj = ServiceRequest.objects.create(
            ticket_number="SR-9001",
            employee=employee,
            service=service,
            title="VPN issue",
            description="Cannot access the VPN",
            status="OPEN",
            priority="HIGH",
        )

        response = self.client.post(f"/requests/{request_obj.pk}/status/", {"status": "RESOLVED"}, follow=True)

        self.assertEqual(response.status_code, 200)
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, "RESOLVED")

    def test_password_reset_request_page_works(self):
        from django.contrib.auth.models import User

        user = User.objects.create_user(username="EMP-4001", email="employee@example.com", password="secret123")
        response = self.client.post("/password-reset/", {"email": user.email}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password reset sent")

    def test_reports_show_department_status_summary(self):
        from django.contrib.auth.models import User
        from departments.models import Department
        from employees.models import Employee
        from service_requests.models import ServiceRequest
        from services.models import Service

        admin_user = User.objects.create_user(username="admin-report-summary", password="secret123")
        admin_user.is_staff = True
        admin_user.save()
        self.client.force_login(admin_user)

        it_department = Department.objects.create(name="IT Dept", description="IT")
        hr_department = Department.objects.create(name="HR Dept", description="HR")
        it_employee = Employee.objects.create(
            emp_id="EMP-6001",
            name="IT Employee",
            email="it@example.com",
            phone="600",
            designation="Engineer",
            department=it_department,
            user=User.objects.create_user(username="EMP-6001", password="secret123"),
            account_created=True,
        )
        hr_employee = Employee.objects.create(
            emp_id="EMP-6002",
            name="HR Employee",
            email="hr@example.com",
            phone="601",
            designation="Manager",
            department=hr_department,
            user=User.objects.create_user(username="EMP-6002", password="secret123"),
            account_created=True,
        )
        it_service = Service.objects.create(name="Laptop Support", description="Laptop", department=it_department)
        hr_service = Service.objects.create(name="Leave Request", description="Leave", department=hr_department)

        ServiceRequest.objects.create(
            ticket_number="SR-6001",
            employee=it_employee,
            service=it_service,
            title="Laptop issue",
            description="Laptop broken",
            status="ASSIGNED",
            priority="HIGH",
        )
        ServiceRequest.objects.create(
            ticket_number="SR-6002",
            employee=it_employee,
            service=it_service,
            title="Laptop resolved",
            description="Resolved",
            status="RESOLVED",
            priority="MEDIUM",
        )
        ServiceRequest.objects.create(
            ticket_number="SR-6003",
            employee=hr_employee,
            service=hr_service,
            title="Leave request",
            description="Need leave",
            status="ASSIGNED",
            priority="LOW",
        )

        response = self.client.get("/reports/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IT Dept")
        self.assertContains(response, "Assigned")
        self.assertContains(response, "Resolved")
        self.assertContains(response, "Open: 0")
        self.assertContains(response, "Assigned: 1")
        self.assertContains(response, "Resolved: 1")
        self.assertContains(response, "HR Dept")

    @staticmethod
    def _create_user(username="tester"):
        from django.contrib.auth.models import User
        return User.objects.create_user(username=username, password="secret123")
