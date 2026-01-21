from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from room.models import Room
from booking.models import Booking, Billing, Customer
from datetime import date, time
from django.db.models.functions import TruncDate


@login_required
def dashboard(request):
    total_rooms = Room.total_rooms()  
    available_rooms = Room.total_rooms_available()  
    booked_rooms = Room.total_rooms_booked() 
    available_silver_rooms = Room.total_available_silver_rooms()  
    available_golden_rooms = Room.total_available_golden_rooms()  

    total_bookings = Booking.objects.count()

    t_income = Billing.objects.aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    total_income = round(t_income / 1000, 1)

    today_collection = Billing.objects.annotate(created_at_date=TruncDate('created_at')) \
        .filter(created_at_date=date.today()) \
        .aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    today_collection = round(today_collection / 1000, 1)

    this_month_collection = Billing.objects.filter(created_at__month=date.today().month) \
        .aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    this_month_collection = round(this_month_collection / 1000, 1)

    last_month_collection = Billing.objects.filter(created_at__month=date.today().month - 1) \
        .aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    last_month_collection = round(last_month_collection / 1000, 1)
    
    checkedin = Booking.objects.filter(checkout_date=None).count()  # Guests currently checked in
    today_checkin = Booking.objects.filter(checkin_date=date.today()).count()  # Check-ins today
    today_checkout = Booking.objects.filter(checkout_date=date.today()).count()  # Check-outs today

    recent_bookings = Booking.objects.all().order_by('-id')[:5]  # Last 5 bookings
    recent_bills = Billing.objects.all().order_by('-id')[:5]  # Last 5 billing entries

    # Prepare context dictionary to pass all calculated data to the template
    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms,
        'available_silver_rooms': available_silver_rooms,
        'available_golden_rooms': available_golden_rooms,
        'total_bookings': total_bookings,
        'total_income': total_income,
        'today_collection': today_collection,
        'this_month_collection': this_month_collection,
        'last_month_collection': last_month_collection,
        'checkedin': checkedin,
        'today_checkin': today_checkin,
        'today_checkout': today_checkout,
        'recent_bookings': recent_bookings,
        'recent_bills': recent_bills,
        'title': 'Dashboard'
    }

    # Render the dashboard template with the collected data
    return render(request, 'dashboard/dashboard.html', context)
