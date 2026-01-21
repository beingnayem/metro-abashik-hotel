from django.contrib import admin
from .models import *

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'room',
        'checkin_time',
        'checkout_time'
    ]