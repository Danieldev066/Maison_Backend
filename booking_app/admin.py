from django.contrib import admin
from .models import (UserProfile, Booking, RoomType, Hotel, HotelReview, Room, RoomImage)

admin.site.register(UserProfile)
admin.site.register(Booking)
admin.site.register(RoomType)
admin.site.register(Hotel)
admin.site.register(HotelReview)
admin.site.register(Room)
admin.site.register(RoomImage)
