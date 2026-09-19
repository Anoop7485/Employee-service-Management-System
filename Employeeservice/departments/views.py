from django.shortcuts import render
from rest_framework import viewsets
from .serializers import DepartmentSerializer
from .models import Department
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset=Department.objects.all()
    serializer_class=DepartmentSerializer
    permission_classes=[AllowAny]
    