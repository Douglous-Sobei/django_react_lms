from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.validators import EmailValidator
import re

# =============================================================================
# Custom User Manager
# =============================================================================


class UserManager(BaseUserManager):
    """
    Custom user manager where username is auto-generated from email prefix
    if not provided. Email is the primary identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)

        username = extra_fields.get('username')
        if not username:
            username = self.model.generate_unique_username_from_email_prefix(
                email)
            extra_fields['username'] = username

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)

# =============================================================================
# Custom User Model
# =============================================================================


class User(AbstractUser):
    """
    Custom User model:
    - Uses email as the primary login field
    - Auto-generates username from email if not provided
    - full_name is derived from first_name and last_name
    """

    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()],
        error_messages={'unique': _("A user with that email already exists.")}
    )

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[AbstractUser._meta.get_field('username').validators[0]],
        error_messages={'unique': _(
            "A user with that username already exists.")}
    )

    otp = models.CharField(max_length=6, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)

    objects = UserManager()

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.full_name or self.email or self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @classmethod
    def generate_unique_username_from_email_prefix(cls, email):
        prefix = email.split('@')[0]
        prefix = re.sub(r'[^\w.@+-]', '', prefix)[:150]
        base_username = prefix
        username = base_username
        counter = 1

        while cls.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            if len(username) > 150:
                username = username[:150]
        return username

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

# =============================================================================
# Profile Model
# =============================================================================


class Profile(models.Model):
    """
    Profile model linked one-to-one with User.
    Stores a cached full_name and additional user metadata.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    full_name = models.CharField(max_length=301, blank=True)

    def __str__(self):
        return f"Profile: {self.full_name or self.user.email}"

# =============================================================================
# Signals
# =============================================================================


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Creates or updates Profile when User is saved.
    Keeps Profile.full_name in sync with User.full_name.
    """
    if created:
        Profile.objects.create(user=instance, full_name=instance.full_name)
    else:
        try:
            profile = instance.profile
            new_full_name = instance.full_name
            if profile.full_name != new_full_name:
                profile.full_name = new_full_name
                profile.save(update_fields=['full_name'])
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance, full_name=instance.full_name)


@receiver(pre_save, sender=User)
def ensure_username_and_sync(sender, instance, **kwargs):
    """
    Ensures username is auto-generated from email if not provided.
    """
    if not instance.username:
        instance.username = User.generate_unique_username_from_email_prefix(
            instance.email)
