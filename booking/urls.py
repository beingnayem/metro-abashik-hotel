from django.urls import path
from . import views

urlpatterns = [     
    path('', views.booking, name='booking_page'),
    path('checkin_page/', views.checkin_page, name='checkin_page'),
    path('checkin/', views.checkin, name='checkin'),
    path('booking_details/', views.booking_details, name='booking_details'),
    path('checkout_page/', views.checkout_page, name='checkout_page'),   
    path('checkout/', views.checkout, name='checkout'), 
    path('checkout_confrim/', views.checkout_confirm, name='checkout_confrim'), 
    path('bills/', views.bills, name='bills'),
    path('search_bill/', views.search_bill, name='search_bill'),
    path('view_invoice/<int:bill_id>/', views.view_invoice, name='view_invoice'),
]