from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'room_number',
        'room_type',
        'room_status',
    ]