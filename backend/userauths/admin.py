from django.contrib import admin
from .models import User, Profile

# Register your models here


class ProfileInline(admin.StackedInline):
    list_display = ('user', 'full_name', 'date')


admin.site.register(User)
admin.site.register(Profile)
