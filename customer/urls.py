from django.urls import path
from . import views

urlpatterns = [     
    path('', views.customers, name='customers'),
    path('customer_history/', views.customer_history, name='customer_history'),
]