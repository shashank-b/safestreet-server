"""
Model for storing user details
"""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.gis.db import models
from django.core.validators import RegexValidator

from core.utils import CITIES


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given Email, Name, city, phone
        """
        if not email:
            raise ValueError('Users must have an Email address')

        user = self.model(
            email=MyUserManager.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, name, city, phone and password
        """
        # print(("dd", email, name, city, phone, password))
        # print(("dd", email, name, password))
        u = self.create_user(email=email,
                             name=name,
                             password=password,
                             )
        u.is_admin = True
        u.save(using=self._db)
        return u


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model to store all the user related information
    """
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=200, null=True, blank=True)
    home_location = models.PointField(srid=4326, null=True, blank=True)
    city = models.CharField(max_length=3, choices=CITIES, blank=True,null=True)
    phone = models.CharField(null=True,blank=True,
        validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits")],
        max_length=10)
    email = models.EmailField(unique=True)
    FbId = models.CharField(max_length=20, null=True, blank=True)
    rating = models.FloatField(default=50)
    credit = models.FloatField(default=0)
    deactivate = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        """
        Is the user a member of staff?
        """
        return self.is_admin
