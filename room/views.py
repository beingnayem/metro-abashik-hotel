from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room

@login_required
def room_info(request):
    total_rooms = Room.total_rooms()
    total_rooms_available = Room.total_rooms_available()
    total_rooms_booked = Room.total_rooms_booked()
    total_available_silver_rooms = Room.total_available_silver_rooms() 
    total_available_golden_rooms = Room.total_available_golden_rooms() 
    rooms = Room.objects.all()  

    # Pass the gathered data into the context for rendering the template
    context = {
        'total_rooms': total_rooms,
        'total_rooms_available': total_rooms_available,
        'total_rooms_booked': total_rooms_booked,
        'total_available_silver_rooms': total_available_silver_rooms,
        'total_available_golden_rooms': total_available_golden_rooms,
        'rooms': rooms,
        'title': 'Room Information'
    }
    
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room = Room.objects.filter(room_number=room_number).first()

        if room:
            # If the room is found, add it to the context and render the page
            context.update({'room': room})
            return render(request, 'room/room_info.html', context)
        else:
            # If no room is found, display an error message and re-render the page
            messages.error(request, 'Room not found')
            return render(request, 'room/room_info.html', context)

    return render(request, 'room/room_info.html', context)


@login_required
def create_room(request):
    if not request.user.is_authenticated:
        return redirect('signin')

    if request.method == 'POST':
        room_number = request.POST['room_number']
        floor_number = request.POST['floor_number']
        room_type = request.POST['room_type']
        room_rent_d = request.POST['room_rent_d']
        room_rent_h = request.POST['room_rent_h']
        capacity = request.POST['capacity']
        extra_capacity = request.POST['extra_capacity']

        room_exist = Room.objects.filter(room_number=room_number).exists()

        if room_exist:
            # If room exists, notify the user and redirect to room info page
            messages.error(request, 'Room already exists')
            return redirect('room_info')
        else:
            # Create a new room and notify the user of successful creation
            Room.objects.create(
                room_number=room_number,
                floor_number=floor_number,
                room_type=room_type,
                room_rent_d=room_rent_d,
                room_rent_h=room_rent_h,
                room_status=False,  # Default room status is unoccupied
                capacity=capacity,
                extra_capacity=extra_capacity
            )
            
            messages.success(request, 'Room created successfully')
            return redirect('room_info')

    # Display room statistics for the create room page if the method is not POST
    total_rooms = Room.total_rooms()
    total_rooms_available = Room.total_rooms_available()
    total_rooms_booked = Room.total_rooms_booked()
    total_available_silver_rooms = Room.total_available_silver_rooms()
    total_available_golden_rooms = Room.total_available_golden_rooms()
    
    context = {
        'total_rooms': total_rooms,
        'total_rooms_available': total_rooms_available,
        'total_rooms_booked': total_rooms_booked,
        'total_available_silver_rooms': total_available_silver_rooms,
        'total_available_golden_rooms': total_available_golden_rooms,
        'title': 'Create Room'
    }
    
    return render(request, 'room/create_room.html', context)


@login_required
def delete_room(request, pk):
    room = Room.objects.filter(pk=pk).first()

    if room:
        # If the room exists, delete it and notify the user
        room.delete()
        messages.success(request, 'Room deleted successfully')
        return redirect('room_info')
    else:
        # If the room does not exist, notify the user of the error
        messages.error(request, 'Room not found')
        return redirect('room_info')
