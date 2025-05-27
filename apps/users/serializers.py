from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    is_host = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)
    is_staff = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'is_host', 'is_active', 'is_staff']

    def create(self, validated_data):
        is_host = validated_data.pop('is_host', False)
        is_active = validated_data.pop('is_active', True)
        is_staff = validated_data.pop('is_staff', False)

        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )

        user.is_host = is_host
        user.is_active = is_active
        user.is_staff = is_staff

        if is_staff:
            user.role = 'admin'
        elif is_host:
            user.role = 'host'
        else:
            user.role = 'user'

        user.save()

        return user


class SingleHostSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            is_host=True
        )


class BulkRegisterHostSerializer(serializers.Serializer):
    users = SingleHostSerializer(many=True)

    def create(self, validated_data):
        users_data = validated_data['users']
        return [SingleHostSerializer().create(user_data) for user_data in users_data]



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_host']
        read_only_fields = ['id', 'email', 'is_host']


