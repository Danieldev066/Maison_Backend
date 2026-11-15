from django.contrib import admin
from .models import (UserProfile, Specialization, Doctor, Schedule, Appointment, MedicalRecord, DoctorReview)

admin.site.register(UserProfile)
admin.site.register(Specialization)
admin.site.register(Doctor)
admin.site.register(Schedule)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(DoctorReview)

