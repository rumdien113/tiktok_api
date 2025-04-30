from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        if not password:
            raise ValueError('Password is required')

        email = self.normalize_email(email)
        user = self.model(email = email, username = username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=70, blank=False, null=False)
    lastname = models.CharField(max_length=70, blank=False, null=False)
    birthdate = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=False, null=False)
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    last_login = None

    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    def __str__(self):
        return self.email

    def generate_otp(self):
        import random
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp_code = otp
        self.otp_expires_at = timezone.now() + timedelta(minutes=5)
        self.save()
        return otp

    def is_otp_valid(self, otp_code):
        if self.otp_code and self.otp_expires_at and timezone.now() <= self.otp_expires_at and self.otp_code == otp_code:
            return True
        return False
    
    def clear_otp(self):
        self.otp_code = None
        self.otp_expires_at = None
        self.save()
