from django.urls import path
from . import views

urlpatterns = [     
      path('', views.signin, name='signin'),
      path('signout/', views.signout, name='signout'),
      path('profile/', views.profile_view, name='profile'),
      path('update_profile/', views.update_profile, name='update_profile'),
      path('change_pass/', views.change_pass, name='change_pass'),
]