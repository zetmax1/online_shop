import random
import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import CustomUser, PasswordResetCode

from .tasks import send_reset_code

class AccountsTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class AccountsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'profile_picture')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password should be 8 characters at least")

        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password should include one letter (A–Z or a–z) at least")

        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password should include one number at least")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password should include one specific character(!@#$ etc) at least ")

        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance



class SendResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("There is no active user with this email")
        return value

    def save(self, **kwargs):
        email = self.validated_data['email']
        code = str(random.randint(1000, 9999))
        PasswordResetCode.objects.create(email=email, code=code)
        send_reset_code.delay(email, code)
        return code


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        email = data.get("email")
        code = data.get("code")
        try:
            reset_code = PasswordResetCode.objects.filter(email=email, code=code).latest("created_at")
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid code"})

        if not reset_code.is_valid():
            raise serializers.ValidationError({"code": "The code is expired"})

        data["reset_code"] = reset_code
        return data

    def save(self, **kwargs):
        email = self.validated_data["email"]
        new_password = self.validated_data["new_password"]
        reset_code = self.validated_data["reset_code"]

        user = CustomUser.objects.get(email=email)
        user.password = make_password(new_password)
        user.save()
        reset_code.delete()
        return user
