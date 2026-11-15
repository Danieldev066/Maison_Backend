from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models

TYPE_CHOICES = (
            ('standard', 'Standard'),
            ('deluxe', 'Deluxe'),
            ('suite', 'Suite'),
            ('family', 'Family'),
        )


class UserProfile(AbstractUser):
    phone_number = PhoneNumberField(default='+996')
    avatar = models.ImageField(default='profile_images/')
    country = models.CharField(max_length=50)
    date_register = models.DateTimeField(auto_now_add=True)

class RoomType(models.Model):
    name = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES
    )
    description = models.TextField()

class Hotel(models.Model):
    name = models.CharField(max_length=50)
    address= models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    stars = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    has_parking = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)

    def get_avg_rating(self):
        return self.reviews.aggregate(
            models.Avg('rating'),
        )['rating_avg']


class Room(models.Model):
    room_number = models.IntegerField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

class RoomImage(models.Model):
    image = models.ImageField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

class Booking(models.Model):
    guest = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(auto_now_add=True)
    guests_count = models.IntegerField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Ожидает'),
            ('confirmed', 'Подтверждено'),
            ('cancelled', 'Отменено'),
        ]
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return (self.check_out - self.check_in).days

    def get_nights(self):
        return self.room.price_per_night * self.get_nights()

class HotelReview(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)




