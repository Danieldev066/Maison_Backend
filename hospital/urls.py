from rest_framework import routers
from .views import (UserProfileViewSet, SpecializationViewSet, DoctorViewSet, ScheduleViewSet, AppointmentViewSet, MedicalRecordViewSet, DoctorReviewViewSet)
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'User', UserProfileViewSet)
router.register(r'Specialization', SpecializationViewSet)
router.register(r'Doctor', DoctorViewSet)
router.register(r'Schedule', ScheduleViewSet)
router.register(r'Appointment', AppointmentViewSet)
router.register(r'MedicalRecord', MedicalRecordViewSet)
router.register(r'DoctorReview', DoctorReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]