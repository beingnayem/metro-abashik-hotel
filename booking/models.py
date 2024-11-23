from django.db import models
from datetime import datetime, timedelta, date
from room.models import Room

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name



class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer)
    checkin_date = models.DateField()
    checkout_date = models.DateField(null=True, blank=True)
    checkin_time = models.TimeField(default="13:00") 
    checkout_time = models.TimeField(default="13:00", null=True, blank=True)
    extra_guest_count = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.calculate_total_cost()
        super().save(*args, **kwargs)

    def calculate_total_cost(self):
        effective_checkout_date = self.checkout_date or date.today()
        days_stayed = (effective_checkout_date - self.checkin_date).days or 1
        room_rent = self.room.room_rent_d * days_stayed
        extra_guest_charge_per_day = self.room.room_rent_h
        extra_guest_cost = self.extra_guest_count * extra_guest_charge_per_day * days_stayed
        self.total_cost = room_rent + extra_guest_cost

    def __str__(self):
        return f"Booking for Room {self.room.room_number} from {self.checkin_date} to {self.checkout_date}"  
    


class Billing(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    bookings = models.ManyToManyField(Booking, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)
    created_time = models.TimeField(auto_now_add=True, null=True, blank=True)
    updated_time = models.TimeField(auto_now=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_total_cost()   
        super().save(update_fields=['total_cost'])

    def calculate_total_cost(self):
        self.total_cost = self.bookings.aggregate(total=models.Sum('total_cost'))['total'] or 0
    
    def __str__(self):
        return f"Billing for {self.customer.name} with total cost {self.total_cost}"

