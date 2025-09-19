from userauths.models import Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

# -------------------------
# RegisterSerializer
# -------------------------


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration:
    - Validates password strength.
    - Confirms password match.
    - Auto-generates username from email prefix.
    - Returns computed full_name.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password must satisfy site security rules",
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm your password",
    )
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = ['email', 'password', 'password2',
                  'first_name', 'last_name', 'full_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        # Check password match
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})

        # Validate password strength
        temp_user = User(
            email=data.get('email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            username=data.get('email', '').split('@')[0]
        )
        try:
            validate_password(data['password'], temp_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove confirm password
        email = validated_data['email']
        username = email.split('@')[0]

        user = User(
            email=email,
            username=username,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

# -------------------------
# UserSerializer
# -------------------------


class UserSerializer(serializers.ModelSerializer):
    """
    Serializes public user fields.
    Includes computed full_name.
    """
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = ['id', 'email', 'username',
                  'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'full_name']

# -------------------------
# ProfileSerializer
# -------------------------


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializes Profile with nested user info.
    full_name is read-only and synced via signals.
    """
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name']
        read_only_fields = ['id', 'user', 'full_name']

# -------------------------
# MyTokenObtainPairSerializer
# -------------------------


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes JWT response to include user info.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data.update({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            }
        })
        return data
