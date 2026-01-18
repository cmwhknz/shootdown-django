from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = (['username','stripe_id'])

admin.site.register(User, CustomUserAdmin)