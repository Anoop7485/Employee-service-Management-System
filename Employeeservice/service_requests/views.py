from django.shortcuts import render
from rest_framework import viewsets,status
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsStaffMember,IsManager,IsEmployee
# Create your views here.
class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset=ServiceRequest.objects.all()
    serializer_class=ServiceRequestSerializer
    permission_classes=[IsAuthenticated]

    @action(
            detail=True,
            methods=['post'],permission_classes=[IsStaffMember])
    def assign(self, request, pk=None):

        service_request = self.get_object()

        service_request.status = 'ASSIGNED'

        service_request.save()

        return Response({
            'message': 'Request assigned successfully',
            'status': service_request.status
        })
    @action(detail=True,methods=['post'])
    def start(self,request,pk=None):
        service_request=self.get_object()
        service_request.status='INPROGRESS'
        service_request.save()
        return Response({
            'message':'Request started',
            'status': service_request.status
        })
    @action(detail=True,methods=['post'],permission_classes=[IsStaffMember])##RESOLVE DONE BY STAFF MEMBER BELONGS TO DEPARTMENT
    def resolve(self,request,pk=None):
        service_request=self.get_object()
        service_request.status='RESOLVED'
        service_request.save()
        return Response({
            'message':'Request Resolved',
            'status':service_request.status
        })
    @action(detail=True,methods=['post'],permission_classes=[IsManager])##HERE WE USE PERMISSION CLS BEACAUSE THE STAFF ONLY CLOSE REQUEST
    def close(self,request,pk=None):
        service_request=self.get_object()
        service_request.status='CLOSED'
        service_request.closed_at=timezone.now()
        service_request.save()
        return Response({
            'message':'Request closed',
            'status':service_request.status
        })