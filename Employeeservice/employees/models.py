from django.db import models
from django.contrib.auth.models import User
from departments.models import Department
# Create your models here.
class Employee(models.Model):
    emp_id=models.CharField(max_length=20,unique=True)
    name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=100)
    designation=models.CharField(max_length=100)
    department=models.ForeignKey(Department,on_delete=models.CASCADE,related_name='employees')
    user=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='employee_profile')
    created_at=models.DateTimeField(auto_now_add=True)
    account_created=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.emp_id}-{self.name}"
    

