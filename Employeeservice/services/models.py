from django.db import models
from departments.models import Department
# Create your models here.
class Service(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True)
    department=models.ForeignKey(Department,on_delete=models.CASCADE,related_name="services")
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
