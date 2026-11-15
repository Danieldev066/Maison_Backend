from rest_framework import serializers
from .models import (UserProfile, Specialization, Doctor, Schedule, Appointment, MedicalRecord, DoctorReview)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'first_name', 'last_name', 'birth_date', 'phone_number', 'address', 'cdate_register')

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ('id', 'name', 'description', 'image')

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'first_name', 'last_name', 'patronymic', 'photo', 'experience_years', 'price', 'specialization')

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'doctor', 'day_of_week', 'start_time', 'end_time')

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id', 'patient', 'doctor', 'date_time', 'complaint', 'status', 'created_date')

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ('id', 'appointment', 'diagnosis', 'prescription', 'created_date')

class DoctorReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorReview
        fields = ('id', 'doctor', 'patient', 'stars', 'comment', 'created_date')
