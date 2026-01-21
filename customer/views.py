from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from booking.models import Customer, Booking
from django.db.models import Q
from room.models import Room
from datetime import datetime, date
from django.contrib import messages
from django.urls import reverse


def customers(request):
    customers = Customer.objects.all()
    total_guest = customers.count()

    today = date.today()

    curent_guest = Booking.objects.filter(checkout_date__isnull=True).count()
    today_checkin_guest = Booking.objects.filter(checkin_date=today).count()
    today_checkout_guest = Booking.objects.filter(checkout_date=today).count()
    customers = customers.order_by('-id')[0:15]

    # Prepare the context with all calculated data and retrieved customers
    context = {
        'total_guest': total_guest,
        'curent_guest': curent_guest,
        'today_checkin_guest': today_checkin_guest,
        'today_checkout_guest': today_checkout_guest,
        'customers': customers,
        'title': 'Customers'
    }

    # Render the 'customers' page with the context
    return render(request, 'customer/customers.html', context)


def customer_history(request):
    customer = None
    bookings = None

    if request.method == 'POST':
        email = request.POST.get('email') 
        try:
            customer = get_object_or_404(Customer, email=email)

            # Fetch all bookings associated with the customer, including room details
            bookings = Booking.objects.filter(customers=customer).select_related('room')
        except Customer.DoesNotExist:
            # Handle case where no customer is found for the given email
            messages.error(request, f"No guest found with email: {email}")
            redirect('customers')
        except Exception as e:
            # Handle any other unexpected exceptions
            messages.error(request, f"An error occurred: {e}")
            redirect('customers')
            
    customers = Customer.objects.all()
    total_guest = customers.count()
    
    today = date.today()
    curent_guest = Booking.objects.filter(checkout_date__isnull=True).count()
    today_checkin_guest = Booking.objects.filter(checkin_date=today).count()
    today_checkout_guest = Booking.objects.filter(checkout_date=today).count()

    # Prepare the context with customer details, booking history, and summary statistics
    context = {
        'total_guest': total_guest,
        'curent_guest': curent_guest,
        'today_checkin_guest': today_checkin_guest,
        'today_checkout_guest': today_checkout_guest,
        'customer': customer,
        'bookings': bookings,
        'title': 'Customer History'
    }

    # Render the 'customer_details' page with the context
    return render(request, 'customer/customer_details.html', context)
