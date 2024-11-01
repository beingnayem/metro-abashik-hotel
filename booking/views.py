from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Customer, Booking, Billing
from room.models import Room
from datetime import datetime, date
from django.contrib import messages
from django.urls import reverse


def booking(request):
    bookings = Booking.objects.all()
    total_bookings = bookings.count()
    today_checkin = bookings.filter(checkin_date=date.today()).count()
    today_checkout = bookings.filter(checkout_date=date.today()).count()
    available_rooms=Room.objects.filter(room_status=False).count()
    context = {'bookings': bookings, 'total_bookings': total_bookings, 
               'today_checkin': today_checkin, 'today_checkout': today_checkout, 
               'available_rooms': available_rooms
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
        available_rooms = Room.objects.filter(room_status=False).count()

        context = {
            'total_bookings': total_bookings,
            'today_checkin': today_checkin,
            'today_checkout': today_checkout,
            'available_rooms': available_rooms,
            'booking': booking, 'rooms_no': range(rooms_no)
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
        # Extract data from request.POST directly, as it's form data
        try:
            # Retrieve room details and booking information
            room_number = request.POST.get('room_number')
            room = get_object_or_404(Room, room_number=room_number)
            checkin_date = datetime.strptime(request.POST.get('checkin_date'), "%Y-%m-%d").date()
            checkin_time = request.POST.get('checkin_time', "13:00")

            # Extract customer information (assumes customer fields are indexed in form)
            customers_info = []
            for i in range(room.capacity + room.extra_capacity):  # Adjust according to max guests
                name = request.POST.get(f'customers[{i}][name]')
                email = request.POST.get(f'customers[{i}][email]')
                phone_number = request.POST.get(f'customers[{i}][phone_number]')
                address = request.POST.get(f'customers[{i}][address]', "")
                
                # Break if no more customers are found
                if not name or not email:
                    break
                
                # Append customer info to list
                customers_info.append({
                    'name': name,
                    'email': email,
                    'phone_number': phone_number,
                    'address': address,
                })

            # Calculate total guests for the room in this booking
            total_guests = len(customers_info)
            main_guest_count = min(total_guests, room.capacity)
            extra_guest_count = max(total_guests - room.capacity, 0)

            # Check if extra guest count exceeds room's extra capacity
            if extra_guest_count > room.extra_capacity:
                messages.error(request, 'Extra guest exceeds room capacity')
                return redirect('booking_page')

            # Create Booking instance for the room
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
            
            room.room_status = True
            room.save()

            messages.success(request, 'Checkin successful')
            return redirect('booking_page')

        except Exception as e:
            messages.error(request, f'Error get_object_or_404during checkin: {str(e)}')
            return redirect('booking_page')
    else:
        return redirect('booking_page')



def checkout(request):
    if request.method == 'POST':
        rooms_no = int(request.GET.get('rooms_no', 1))
        
        email = request.POST.get('email')
        booking_info = []
        for i in range(rooms_no):
            try:
                room_number = request.POST.get(f'rooms[{i}][room_number]')
                room = Room.objects.get(room_number=room_number, room_status=True)
            except Room.DoesNotExist:
                messages.error(request, f"No active room found with room number {room_number}.")
                return redirect('booking_page')
            try:
                booking = Booking.objects.get(room=room)
            except Booking.DoesNotExist:
                messages.error(request, "This room is not booked yet.")
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
        for booking in booking_info:
            booking.checkout_date = date.today()
            booking.checkout_time = datetime.now().strftime("%H:%M")
            booking.save()
            booking.room.room_status = False
            booking.room.save()
            bill.bookings.add(booking)

        bill.save()

        messages.success(request, 'Check out successful')
        return redirect('booking_page')
    
    else:
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
        available_rooms = Room.objects.filter(room_status=False).count()

        context = {
            'total_bookings': total_bookings,
            'today_checkin': today_checkin,
            'today_checkout': today_checkout,
            'available_rooms': available_rooms,
            'booking': booking
        }

        return render(request, 'booking/search_booking.html', context)

    return render(request, 'booking/search_booking.html')
