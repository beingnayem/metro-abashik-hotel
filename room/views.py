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
    context = {
            'total_rooms': total_rooms,
            'total_rooms_available': total_rooms_available,
            'total_rooms_booked': total_rooms_booked,
            'total_available_silver_rooms': total_available_silver_rooms,
            'total_available_golden_rooms': total_available_golden_rooms,
            'rooms' : rooms
        }
    
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room = Room.objects.filter(room_number=room_number).first()
        if room:
            context.update({'room': room})
            return render(request, 'room/room_info.html', context)
        else:
            messages.error(request, 'Room not found')
            return render(request, 'room/room_info.html', context)

    return render(request, 'room/room_info.html', context)



@login_required
def create_room(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    else:
        if request.method=='POST':
            room_number = request.POST['room_number']
            floor_number = request.POST['floor_number']
            room_type = request.POST['room_type']
            room_rent_d = request.POST['room_rent_d']
            room_rent_h = request.POST['room_rent_h']
            capacity = request.POST['capacity']
            extra_capacity = request.POST['extra_capacity']
            room_exist = Room.objects.filter(room_number=room_number).exists()
            if room_exist:
                messages.error(request, 'Room already exist')
                return redirect('room_info')
            else:
                messages.success(request, 'Room created successfully')
                Room.objects.create(room_number=room_number, floor_number=floor_number, room_type=room_type, room_rent_d=room_rent_d, room_rent_h=room_rent_h, room_status=False, capacity=capacity, extra_capacity=extra_capacity)
                return redirect('room_info')
        total_rooms = Room.total_rooms()
        total_rooms_available = Room.total_rooms_available()
        total_rooms_booked = Room.total_rooms_booked()
        total_available_silver_rooms = Room.total_available_silver_rooms()
        total_available_golden_rooms = Room.total_available_golden_rooms()
        return render(request, 'room/create_room.html', {
            'total_rooms': total_rooms,
            'total_rooms_available': total_rooms_available,
            'total_rooms_booked': total_rooms_booked,
            'total_available_silver_rooms': total_available_silver_rooms,
            'total_available_golden_rooms': total_available_golden_rooms,
        })


@login_required
def delete_room(request, pk):
    room = Room.objects.filter(pk=pk).first()
    if room:
        room.delete()
        messages.success(request, 'Room deleted successfully')
        return redirect('room_info')
    else:
        messages.error(request, 'Room not found')
        return redirect('room_info')