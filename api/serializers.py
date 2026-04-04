from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, FinancialRecord


# ── Auth serializers ──────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ('username', 'email', 'password', 'password2', 'role')
        extra_kwargs = {'role': {'required': False}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ('id', 'username', 'email', 'role', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Admin-only: update role and active status."""
    class Meta:
        model  = User
        fields = ('role', 'is_active')


# ── Financial record serializers ──────────────────────────────────────────────

class FinancialRecordSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True
    )

    class Meta:
        model  = FinancialRecord
        fields = (
            'id', 'amount', 'entry_type', 'category',
            'date', 'description', 'is_deleted',
            'created_by', 'created_by_username',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'is_deleted')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class FinancialRecordCreateSerializer(FinancialRecordSerializer):
    """Write serializer — excludes read-only admin fields."""
    class Meta(FinancialRecordSerializer.Meta):
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at', 'is_deleted')