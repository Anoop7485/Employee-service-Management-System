from django.db import models
from employees.models import Employee
from services.models import Service
# Create your models here.
class ServiceRequest(models.Model):
    PRIORITY_CHOICES=[
        ('LOW','low'),
        ('MEDIUM','medium'),
        ('HIGH','high'),
        ('URGENT','urgent'),
    ]

    STATUS_CHOICES=[
        ('OPEN','open'),
        ('ASSIGNED','assigned'),
        ('INPROGRESS','In progress'),
        ('RESOLVED','Resolved'),
        ('CLOSED','Closed'),
        ('REJECTED','Rejected'),
    ]

    ticket_number=models.CharField(max_length=20,unique=True)

    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='requests')

    service=models.ForeignKey(Service,on_delete=models.CASCADE,related_name='requests')

    title=models.CharField(max_length=200)

    description=models.TextField()

    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='OPEN')

    priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default='MEDIUM')

    created_at=models.DateTimeField(auto_now_add=True)

    updated_at=models.DateTimeField(auto_now=True)

    resolved_at=models.DateTimeField(null=True,blank=True)

    closed_at=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.ticket_number}-{self.title}"