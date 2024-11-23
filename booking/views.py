from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Customer, Booking, Billing
from room.models import Room
from datetime import datetime, date
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from django.template.loader import render_to_string
import threading
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.mail import BadHeaderError, send_mail
from django.core import mail
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse, FileResponse
import pdfkit



def booking(request):
    bookings = Booking.objects.all()
    total_bookings = bookings.count()
    today_checkin = bookings.filter(checkin_date=date.today()).count() # Today's check-ins
    today_checkout = bookings.filter(checkout_date=date.today()).count()  # Today's check-outs
    booked = bookings.filter(checkout_date=None).count()  # Count of currently booked rooms
    bookings = bookings.order_by('-id')[0:15]  # Retrieve the latest 15 bookings

    context = {
        'bookings': bookings, 
        'total_bookings': total_bookings,
        'today_checkin': today_checkin, 
        'today_checkout': today_checkout,
        'booked': booked
    }
    return render(request, 'booking/booking.html', context)


def checkout_page(request):
    if request.method == 'POST':
        rooms_no = int(request.POST.get('rooms_no', 1))  # Default to 1 room if not provided
        return redirect(f"{reverse('checkout_page')}?rooms_no={rooms_no}")
    else:
        rooms_no = int(request.GET.get('rooms_no', 1))
        bookings = Booking.objects.all()
        
        # Aggregate booking statistics
        total_bookings = bookings.count()
        today_checkin = bookings.filter(checkin_date=date.today()).count()
        today_checkout = bookings.filter(checkout_date=date.today()).count()
        booked = bookings.filter(checkout_date=None).count()

        context = {
            'total_bookings': total_bookings,
            'today_checkin': today_checkin,
            'today_checkout': today_checkout,
            'booked': booked,  # Total booked rooms
            'rooms_no': range(rooms_no)  # Range for room input generation
        }
        return render(request, 'booking/checkout_page.html', context)


def checkin_page(request):
    if request.method == 'POST':
        guests = int(request.POST.get('guests', 1))  # Get number of guests from POST data
        return redirect(f"{reverse('checkin_page')}?guests={guests}")
    else:
        rooms = Room.objects.filter(room_status=False)  # Query available rooms
        guests = int(request.GET.get('guests', 1))
        bookings = Booking.objects.all()

        # Fetch booking statistics
        total_bookings = bookings.count()
        today_checkin = bookings.filter(checkin_date=date.today()).count()
        today_checkout = bookings.filter(checkout_date=date.today()).count()
        available_rooms = Room.objects.filter(room_status=False).count()  # Count of free rooms

        context = {
            'bookings': bookings, 
            'total_bookings': total_bookings,
            'today_checkin': today_checkin, 
            'today_checkout': today_checkout,
            'available_rooms': available_rooms, 
            'rooms': rooms,
            'guest_range': range(guests)  # Generate range for guest input fields
        }
        return render(request, 'booking/checkin_page.html', context)


def checkin(request):
    if request.method == 'POST':
        try:
            room_number = request.POST.get('room_number')
            room = get_object_or_404(Room, room_number=room_number)
            
            checkin_date = date.today()
            checkin_time = datetime.now().strftime("%H:%M")  # Capture current time as check-in time

            # Gather customer information from form data
            customers_info = []
            for i in range(room.capacity + room.extra_capacity):
                name = request.POST.get(f'customers[{i}][name]')
                email = request.POST.get(f'customers[{i}][email]')
                phone_number = request.POST.get(f'customers[{i}][phone_number]')
                address = request.POST.get(f'customers[{i}][address]', "")
                
                # Break if any required field is missing
                if not name or not email:
                    break
                
                customers_info.append({
                    'name': name,
                    'email': email,
                    'phone_number': phone_number,
                    'address': address,
                })

            total_guests = len(customers_info)
            main_guest_count = min(total_guests, room.capacity)  # Guests within room capacity
            extra_guest_count = max(total_guests - room.capacity, 0)  # Count of extra guests

            # Validate if extra guests exceed the room's allowed extra capacity
            if extra_guest_count > room.extra_capacity:
                messages.error(request, 'Extra guest exceeds room capacity')
                return redirect('booking_page')

            # Create a booking record
            booking = Booking.objects.create(
                room=room,
                checkin_date=checkin_date,
                checkout_date=None,
                checkin_time=checkin_time,
                checkout_time=None,
                extra_guest_count=extra_guest_count
            )

            # Add customers to the booking
            for customer_data in customers_info:
                customer, created = Customer.objects.get_or_create(
                    email=customer_data['email'],
                    defaults={
                        'name': customer_data['name'],
                        'phone_number': customer_data['phone_number'],
                        'address': customer_data.get('address', "")
                    }
                )
                booking.customers.add(customer)
            booking.save()
            
            # Mark the room as booked
            room.room_status = True
            room.save()
            
            # Send email confirmation to each customer
            for customer_data in customers_info:
                email_subject = "Check-In Successful - Metro Abashik Hotel"
                email_body = render_to_string('booking/checkin_email.html', {
                    'customer': customer_data,
                    'room_number': room.room_number,
                    'checkin_date': checkin_date,
                    'checkin_time': checkin_time,
                    'extra_guest_count': extra_guest_count,
                    'roommates': customers_info,
                })
                email = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[customer_data['email']],
                )
                email.content_subtype = "html"  # Send email as HTML
                email.send()

            messages.success(request, 'Check In Successful')
            return redirect('booking_page')

        except Exception as e:
            # Log errors for debugging purposes
            messages.error(request, f'Error during checkin: {str(e)}')
            return redirect('booking_page')
    else:
        return redirect('booking_page')



def checkout(request):
    bookings = Booking.objects.all()
    total_bookings = bookings.count()
    today_checkin = bookings.filter(checkin_date=date.today()).count()
    today_checkout = bookings.filter(checkout_date=date.today()).count()
    booked = bookings.filter(checkout_date=None).count()
    booking_info = []  # List to hold booking details for rooms being checked out
    customer = None
    total_cost = 0

    if request.method == 'POST':
        email = request.POST.get('email')
        room_numbers = request.POST.getlist('rooms[]')

        if not room_numbers:
            # Ensure that at least one room number is provided
            messages.error(request, "No room numbers were provided.")
            return redirect('booking_page')

        for room_number in room_numbers:
            try:
                # Check if the room exists and is currently booked
                room = Room.objects.get(room_number=room_number, room_status=True)
            except Room.DoesNotExist:
                messages.error(request, f"No active room found with room number {room_number}.")
                return redirect('booking_page')

            try:
                # Get the active booking for the room
                booking = Booking.objects.filter(room=room, checkout_date=None).first()
            except Booking.DoesNotExist:
                messages.error(request, "This room is not booked yet.")
                return redirect('booking_page')

            # Accumulate total cost and add booking details
            total_cost += booking.total_cost
            booking_info.append(booking)

        try:
            # Retrieve the customer by email
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, f"No customer found with email {email}.")
            return redirect('booking_page')

    context = {
        'total_bookings': total_bookings,
        'today_checkin': today_checkin,
        'today_checkout': today_checkout,
        'booked': booked,
        'bookings_info': booking_info,  
        'customer': customer,           
        'total_cost': total_cost         
    }

    return render(request, 'booking/checkout_bill.html', context)


def generate_pdf(template_src, context_dict):
    template = render_to_string(template_src, context_dict)  # Render the template as a string
    pdf = pdfkit.from_string(template, False)  # Convert the HTML string to a PDF
    return pdf


def checkout_confirm(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        room_numbers = request.POST.getlist('room_numbers[]')

        booking_info = []  # List to store bookings being checked out

        for i in room_numbers:
            try:
                # Retrieve the room based on room number and ensure it is currently booked
                room = Room.objects.get(room_number=i, room_status=True)
            except Room.DoesNotExist:
                messages.error(request, f"No active room found with room number {i}.")
                return redirect('booking_page')

            booking = Booking.objects.filter(room=room, checkout_date=None).first()
            if not booking:
                messages.error(request, f"No active booking found for room {i}.")
                return redirect('booking_page')

            booking_info.append(booking)  # Add booking details to the list

        try:
            # Retrieve customer details based on email
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, f"No customer found with email {email}.")
            return redirect('booking_page')

        # Create a new billing record for the customer
        bill = Billing(customer=customer)
        bill.save()

        total_cost = 0  # Initialize total cost for the bill
        for booking in booking_info:
            # Update booking details to mark checkout
            booking.checkout_date = date.today()
            booking.checkout_time = datetime.now().strftime("%H:%M")
            booking.save()

            # Update room status to available
            booking.room.room_status = False
            booking.room.save()

            # Associate the booking with the bill
            bill.bookings.add(booking)
            total_cost += booking.total_cost

        bill.save()  # Save the billing record

        # Generate the invoice PDF
        pdf_context = {
            'customer': customer,
            'bill': bill,
            'booking_info': booking_info,
            'total_cost': total_cost,
        }
        pdf_data = generate_pdf('booking/invoice_template.html', pdf_context)
        if not pdf_data:
            messages.error(request, "Failed to generate invoice PDF.")
            return redirect('booking_page')

        # Prepare and send the invoice email
        email_subject = "Your Invoice from Metro Abashik Hotel"
        email_body = render_to_string('booking/invoice_email.html', {'customer': customer})
        email_message = EmailMessage(subject=email_subject, body=email_body, to=[email])
        email_message.attach('invoice.pdf', pdf_data, 'application/pdf')  # Attach the invoice PDF
        email_message.content_subtype = 'html'
        email_message.send()  # Send the email

        messages.success(request, "Checkout Successful. Invoice sent to customer's email.")
        return redirect('booking_page')

    return redirect('booking_page')


def booking_details(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')

        # Check if a room number is provided
        if not room_number:
            messages.error(request, "Room number is missing. Please provide a valid room number.")
            return redirect('booking_page')

        try:
            # Attempt to find an active room with the provided room number
            room = Room.objects.get(room_number=room_number, room_status=True)
        except Room.DoesNotExist:
            # Room does not exist or is not active
            messages.error(request, f"No active room found with room number {room_number}.")
            return redirect('booking_page')

        try:
            # Fetch the booking associated with the room
            booking = get_object_or_404(Booking, room=room)
        except Booking.DoesNotExist:
            # Handle case where the room is not booked
            messages.error(request, "This room is not booked yet.")
            return redirect('booking_page')

        # Gather booking statistics
        bookings = Booking.objects.all()
        total_bookings = bookings.count()
        today_checkin = bookings.filter(checkin_date=date.today()).count()
        today_checkout = bookings.filter(checkout_date=date.today()).count()
        booked = bookings.filter(checkout_date=None).count()

        # Context for rendering the booking details
        context = {
            'total_bookings': total_bookings,
            'today_checkin': today_checkin,
            'today_checkout': today_checkout,
            'booked': booked,
            'booking': booking
        }

        return render(request, 'booking/search_booking.html', context)

    return render(request, 'booking/search_booking.html')


def bills(request):
    # Fetch all billing records and calculate statistics
    bills = Billing.objects.all()
    total_bills = bills.count()
    today = timezone.now().date()
    today_bills = bills.filter(created_at=today).count()
    today_total = bills.filter(created_at=today).aggregate(total=Sum('total_cost'))['total']
    today_total = today_total if today_total is not None else 0
    today_total_in_k = today_total / 1000  # Convert the total to thousands for display
    today_total_in_k = round(today_total_in_k, 1)  # Round to one decimal place
    booked = Booking.objects.filter(checkout_date=None).count()

    # Fetch the latest 15 bills for display
    bills = bills.order_by('-id')[0:15]
    context = {
        'bills': bills,
        'total_bills': total_bills,
        'today_bills': today_bills,
        'today_total_in_k': today_total_in_k,
        'booked': booked
    }

    return render(request, 'booking/bills.html', context)


def search_bill(request):
    if request.method == 'POST':
        # Recalculate billing statistics for display on the search results page
        bills = Billing.objects.all()
        total_bills = bills.count()
        today = timezone.now().date()
        today_bills = bills.filter(created_at=today).count()
        today_total = bills.filter(created_at=today).aggregate(total=Sum('total_cost'))['total']
        today_total = today_total if today_total is not None else 0
        today_total_in_k = today_total / 1000
        today_total_in_k = round(today_total_in_k, 1)
        booked = Booking.objects.filter(checkout_date=None).count()

        email = request.POST.get('email')
        if email:
            try:
                # Fetch the customer associated with the provided email
                customer = Customer.objects.get(email=email)
                try:
                    # Find all bills associated with this customer
                    bill = bills.filter(customer=customer)
                except Billing.DoesNotExist:
                    # Handle case where no bills are found for the customer
                    messages.error(request, "No bill found for this customer.")
                    return redirect('bills')
            except Customer.DoesNotExist:
                # Handle case where the customer does not exist
                messages.error(request, "Customer not found with this email.")
                return redirect('bills')

            # Context for rendering the bill details page
            context = {
                'bill': bill,
                'total_bills': total_bills,
                'today_bills': today_bills,
                'today_total_in_k': today_total_in_k,
                'booked': booked
            }
            return render(request, 'booking/bill_details.html', context)

    return redirect('bills')


def view_invoice(request, bill_id):
    bill = Billing.objects.get(id=bill_id)
    customer = bill.customer
    booking_info = bill.bookings.all()
    total_cost = bill.total_cost

    # Generate PDF invoice using the provided context
    pdf_context = {
        'customer': customer,
        'bill': bill,
        'booking_info': booking_info,
        'total_cost': total_cost,
    }
    pdf = generate_pdf('booking/invoice_template.html', pdf_context)

    # Return the generated PDF as a downloadable response
    return HttpResponse(pdf, content_type='application/pdf')

