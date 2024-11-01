from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name',
        'email',
        'gender',
        'is_active',
        'is_admin'
    ]