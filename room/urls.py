from django.urls import path
from . import views

urlpatterns = [     
    path('room_info/', views.room_info, name='room_info'),
    path('create_room/', views.create_room, name='create_room'),
    path('delete_room/<int:pk>/', views.delete_room, name='delete_room'),
]