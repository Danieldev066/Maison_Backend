from rest_framework import serializers
from .models import (UserProfile, Booking, RoomType, Hotel, HotelReview, Room, RoomImage)

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'avatar', 'country', 'date_register')

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('guest', 'room', 'check_in', 'check_out', 'guests_count', 'status', 'created_date')

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ('name', 'description')

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ('name', 'address', 'city', 'country', 'stars', 'description', 'photo', 'has_parking', 'has_wifi')

class HotelReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelReview
        fields = ('hotel', 'user', 'stars', 'comment', 'created_date')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('room_number', 'price_per_night', 'capacity', 'description', 'is_available', 'room_type', 'hotel')

class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ('image', 'room')



