from rest_framework import routers
from .views import (UserProfileViewSet, BookingViewSet, RoomTypeViewSet, HotelViewSet, HotelReviewViewSet, RoomViewSet, RoomImageViewSet)
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'Users', UserProfileViewSet)
router.register(r'Booking', BookingViewSet)
router.register(r'RoomType', RoomTypeViewSet)
router.register(r'Hotel', HotelViewSet)
router.register(r'HotelReview', HotelReviewViewSet)
router.register(r'Room', RoomViewSet)
router.register(r'RoomImage', RoomImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
