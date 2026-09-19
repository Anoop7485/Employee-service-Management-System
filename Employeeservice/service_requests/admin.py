from django.contrib import admin
from .models import ServiceRequest
# Register your models here.
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display=('ticket_number','service','created_at','resolved_at')
admin.site.register(ServiceRequest,ServiceRequestAdmin)