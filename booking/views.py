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
    today_checkin = bookings.filter(checkin_date=date.today()).count()
    today_checkout = bookings.filter(checkout_date=date.today()).count()
    booked = bookings.filter(checkout_date=None).count()
    bookings = bookings.order_by('-id')[0:15]
    context = {'bookings': bookings, 'total_bookings': total_bookings, 
               'today_checkin': today_checkin, 'today_checkout': today_checkout, 
               'booked': booked
               }
    return render(request, 'booking/booking.html', context)


def checkout_page(request):
    if request.method == 'POST':
        rooms_no = int(request.POST.get('rooms_no', 1))
        print("Room No - ",rooms_no)
        return redirect(f"{reverse('checkout_page')}?rooms_no={rooms_no}")
    else: 
        rooms_no = int(request.GET.get('rooms_no', 1))
        bookings = Booking.objects.all()
        total_bookings = bookings.count()
        today_checkin = bookings.filter(checkin_date=date.today()).count()
        today_checkout = bookings.filter(checkout_date=date.today()).count()
        booked = bookings.filter(checkout_date=None).count()

        context = {
            'total_bookings': total_bookings,
            'today_checkin': today_checkin,
            'today_checkout': today_checkout,
            'booked': booked,
            'booked': booked, 'rooms_no': range(rooms_no)
        }
        return render(request, 'booking/checkout_page.html', context)


def checkin_page(request):
    if request.method == 'POST':
        guests = int(request.POST.get('guests', 1))
        return redirect(f"{reverse('checkin_page')}?guests={guests}")
    else:
        # Fetch only available rooms
        rooms = Room.objects.filter(room_status=False)  
        guests = int(request.GET.get('guests', 1))  # Default to 1 guest if not specified
        bookings = Booking.objects.all()
        total_bookings = bookings.count()
        today_checkin = bookings.filter(checkin_date=date.today()).count()
        today_checkout = bookings.filter(checkout_date=date.today()).count()
        available_rooms=Room.objects.filter(room_status=False).count()
        context = {'bookings': bookings, 'total_bookings': total_bookings, 
                    'today_checkin': today_checkin, 'today_checkout': today_checkout, 
                    'available_rooms': available_rooms, 'rooms': rooms, 
                    'guest_range': range(guests)
                }
        return render(request, 'booking/checkin_page.html', context)


def checkin(request):
    if request.method == 'POST':
        try:
            # Retrieve room details and booking information
            room_number = request.POST.get('room_number')
            room = get_object_or_404(Room, room_number=room_number)
            
            checkin_date = date.today()
            checkin_time = datetime.now().strftime("%H:%M")

            customers_info = []
            for i in range(room.capacity + room.extra_capacity):  # Adjust according to max guests
                name = request.POST.get(f'customers[{i}][name]')
                email = request.POST.get(f'customers[{i}][email]')
                phone_number = request.POST.get(f'customers[{i}][phone_number]')
                address = request.POST.get(f'customers[{i}][address]', "")
                
                if not name or not email:
                    break
                
                customers_info.append({
                    'name': name,
                    'email': email,
                    'phone_number': phone_number,
                    'address': address,
                })

            total_guests = len(customers_info)
            main_guest_count = min(total_guests, room.capacity)
            extra_guest_count = max(total_guests - room.capacity, 0)

            if extra_guest_count > room.extra_capacity:
                messages.error(request, 'Extra guest exceeds room capacity')
                return redirect('booking_page')

            booking = Booking.objects.create(
                room=room,
                checkin_date=checkin_date,
                checkout_date=None,
                checkin_time=checkin_time,
                checkout_time=None,
                extra_guest_count=extra_guest_count
            )

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
            
            room.room_status = True
            room.save()
            
            for customer_data in customers_info:
                email_subject = "Check-In Successful - Metro Abashik Hotel"
                email_body = render_to_string('booking/checkin_email.html', {
                    'customer': customer_data,
                    'room_number': room.room_number,
                    'checkin_date': checkin_date,
                    'checkin_time': checkin_time,
                    'extra_guest_count': extra_guest_count,
                    'roommates': customers_info,  # Pass all customer details to the template
                })
                email = EmailMessage(
                    subject=email_subject,
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[customer_data['email']],
                )
                email.content_subtype = "html"  # This is crucial for HTML emails
                email.send()

            messages.success(request, 'Check In Successful')
            return redirect('booking_page')

        except Exception as e:
            messages.error(request, f'Error get_object_or_404during checkin: {str(e)}')
            return redirect('booking_page')
    else:
        return redirect('booking_page')


def checkout(request):
    bookings = Booking.objects.all()
    total_bookings = bookings.count()
    today_checkin = bookings.filter(checkin_date=date.today()).count()
    today_checkout = bookings.filter(checkout_date=date.today()).count()
    booked = bookings.filter(checkout_date=None).count()
    booking_info = []
    customer = None
    total_cost = 0

    if request.method == 'POST':
        email = request.POST.get('email')
        room_numbers = request.POST.getlist('rooms[]')  # Get all room numbers as a list
        
        # print(room_numbers)

        if not room_numbers:
            messages.error(request, "No room numbers were provided.")
            return redirect('booking_page')

        # print("Room Numbers - ", room_numbers)

        for room_number in room_numbers:
            try:
                room = Room.objects.get(room_number=room_number, room_status=True)
                # print("Room Num - ", room_number)
            except Room.DoesNotExist:
                messages.error(request, f"No active room found with room number {room_number}.")
                return redirect('booking_page')

            try:
                booking = Booking.objects.filter(room=room, checkout_date=None).first()
            except Booking.DoesNotExist:
                messages.error(request, "This room is not booked yet.")
                return redirect('booking_page')

            total_cost += booking.total_cost
            booking_info.append(booking)

        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, f"No customer found with email {email}.")
            return redirect('booking_page')

    # print(booking_info)
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
    """Generate a PDF from an HTML template and context."""
    # Render the HTML content
    template = render_to_string(template_src, context_dict)
    
    # Generate PDF
    pdf = pdfkit.from_string(template, False)  # False will return the PDF as a byte string
    
    return pdf


def checkout_confirm(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        room_numbers = request.POST.getlist('room_numbers[]')

        booking_info = []
        for i in room_numbers:
            try:
                room = Room.objects.get(room_number=i, room_status=True)
            except Room.DoesNotExist:
                messages.error(request, f"No active room found with room number {i}.")
                return redirect('booking_page')
            
            booking = Booking.objects.filter(room=room, checkout_date=None).first()
            if not booking:
                messages.error(request, f"No active booking found for room {i}.")
                return redirect('booking_page')
            
            booking_info.append(booking)
        
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, f"No customer found with email {email}.")
            return redirect('booking_page')
        
        # Create the Billing object
        bill = Billing(customer=customer)
        bill.save()

        # Now add each booking to the bill
        total_cost = 0
        for booking in booking_info:
            booking.checkout_date = date.today()
            booking.checkout_time = datetime.now().strftime("%H:%M")
            booking.save()
            booking.room.room_status = False
            booking.room.save()
            bill.bookings.add(booking)
            total_cost += booking.total_cost

        bill.save()

        # Generate PDF Invoice
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
        
        # Send Email with Invoice
        email_subject = "Your Invoice from Metro Abashik Hotel"
        email_body = render_to_string('booking/invoice_email.html', {'customer': customer})
        email_message = EmailMessage(subject=email_subject, body=email_body, to=[email])
        email_message.attach('invoice.pdf', pdf_data, 'application/pdf')
        email_message.content_subtype = 'html'
        email_message.send()

        messages.success(request, "Checkout Successful. Invoice sent to customer's email.")
        return redirect('booking_page')

    return redirect('booking_page')


def booking_details(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        print(room_number)
        # Check if room_number is None or empty
        if not room_number:
            messages.error(request, "Room number is missing. Please provide a valid room number.")
            return redirect('booking_page')

        try:
            # Fetch the Room with room_status=True
            room = Room.objects.get(room_number=room_number, room_status=True)
        
        except Room.DoesNotExist:
            messages.error(request, f"No active room found with room number {room_number}.")
            return redirect('booking_page')

        try:
            booking = get_object_or_404(Booking, room=room)
        except Booking.DoesNotExist:
            messages.error(request, "This room is not booked yet.")
            return redirect('booking_page')

        # Collect booking stats
        bookings = Booking.objects.all()
        total_bookings = bookings.count()
        today_checkin = bookings.filter(checkin_date=date.today()).count()
        today_checkout = bookings.filter(checkout_date=date.today()).count()
        booked = bookings.filter(checkout_date=None).count()

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
    bills = Billing.objects.all()
    total_bills = bills.count()
    today = timezone.now().date()
    today_bills = bills.filter(created_at=today).count()
    today_total = bills.filter(created_at=today).aggregate(total=Sum('total_cost'))['total']
    today_total = today_total if today_total is not None else 0
    today_total_in_k = today_total / 1000  # Convert to 'K Tk'
    today_total_in_k = round(today_total_in_k, 1)  # Round to one decimal place
    booked = Booking.objects.filter(checkout_date=None).count()
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
                # Find customer by email
                customer = Customer.objects.get(email=email)
                try:
                    bill = bills.filter(customer=customer)
                except Billing.DoesNotExist:
                    messages.error(request, "No bill found for this customer.")
                    return redirect('bills')
            except Customer.DoesNotExist:
                messages.error(request, "Customer not found with this email.")
                return redirect('bills')
            context = {
                'bill': bill,
                'total_bills': total_bills,
                'today_bills': today_bills,
                'today_total_in_k': today_total_in_k,
                'booked': booked
            }
            return render(request, 'booking/bill_details.html', context)
    
    else:
        return redirect('bills')


def view_invoice(request, bill_id):
    
    bill = Billing.objects.get(id=bill_id)
    customer = bill.customer
    booking_info = bill.bookings.all()
    total_cost = bill.total_cost
    
    pdf_context = {
        'customer': customer,
        'bill': bill,
        'booking_info': booking_info,
        'total_cost': total_cost,
    }
    pdf = generate_pdf('booking/invoice_template.html', pdf_context)
    return HttpResponse(pdf, content_type='application/pdf')
