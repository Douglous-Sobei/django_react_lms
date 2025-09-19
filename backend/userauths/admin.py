from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile

# -------------------------
# Inline Profile Admin
# -------------------------


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ['full_name']

# -------------------------
# Custom User Admin
# -------------------------


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model.
    Displays full_name, email, username, and profile inline.
    """
    inlines = [ProfileInline]
    model = User

    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'last_name', 'username')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Security'), {'fields': ('otp', 'refresh_token')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

# -------------------------
# Optional: Profile Admin
# -------------------------


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin for Profile model.
    """
    list_display = ('user', 'full_name')
    search_fields = ('full_name', 'user__email', 'user__username')
    readonly_fields = ('full_name',)
