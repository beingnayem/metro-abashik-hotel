from django.db import models


class Room(models.Model):
    room_number = models.CharField(max_length=255, null=True, blank=True, unique=True)
    floor_number = models.CharField(max_length=255, null=True, blank=True)
    room_type = models.CharField(max_length=255, null=True, blank=True)
    room_rent_d = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    room_rent_h =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    room_status = models.BooleanField(default=False)
    capacity = models.IntegerField(null=True, blank=True)
    extra_capacity = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.room_number

    @classmethod
    def total_rooms(cls):
        return cls.objects.count()
    
    @classmethod
    def total_rooms_available(cls):
        return cls.objects.filter(room_status=False).count()
    
    @classmethod
    def total_rooms_booked(cls):
        return cls.objects.filter(room_status=True).count()
    
    @classmethod
    def total_available_silver_rooms(cls):
        return cls.objects.filter(room_type='Silver', room_status=False).count()
    
    @classmethod
    def total_available_golden_rooms(cls):
        return cls.objects.filter(room_type='Golden', room_status=False).count()
    