from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom Manager für User ohne Username"""
    
    def create_user(self, email, fullname, password=None):
        if not email:
            raise ValueError('Email is required')
        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, fullname, password=None):
        user = self.create_user(email, fullname, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Custom User Model mit fullname statt first/last name"""
    username = None
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'