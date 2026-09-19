from rest_framework.routers import DefaultRouter

from .views import ServiceRequestViewSet

router=DefaultRouter()
router.register('service_requests',ServiceRequestViewSet)

urlpatterns=router.urls