from django.urls import path
from . import views

urlpatterns = [     
    path('booking_room/', views.booking, name='booking_page'),
    path('checkin_page/', views.checkin_page, name='checkin_page'),
    path('checkin/', views.checkin, name='checkin'),
    path('booking_details/', views.booking_details, name='booking_details'),
    path('checkout_page/', views.checkout_page, name='checkout_page'),   
    path('checkout/', views.checkout, name='checkout'),  
]