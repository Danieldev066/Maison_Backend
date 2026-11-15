from rest_framework import viewsets
from .serializers import (UserProfile, RegisterUserSerializer, Booking, BookingSerializer, RoomType, RoomTypeSerializer, Hotel, HotelSerializer, HotelReview,
                          HotelReviewSerializer, Room, RoomSerializer, RoomImage, RoomImageSerializer)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = RegisterUserSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class RoomTypeViewSet(viewsets.ModelViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class HotelReviewViewSet(viewsets.ModelViewSet):
    queryset = HotelReview.objects.all()
    serializer_class = HotelReviewSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomImageViewSet(viewsets.ModelViewSet):
    queryset = RoomImage.objects.all()
    serializer_class = RoomImageSerializer

