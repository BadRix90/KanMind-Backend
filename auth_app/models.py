from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model without username field."""
    
    def create_user(self, email, fullname, password=None):
        """
        Create and save a regular user with email and password.
        
        Args:
            email: User's email address
            fullname: User's full name
            password: User's password (optional)
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email is not provided
        """
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
        """
        Create and save a superuser with email and password.
        
        Args:
            email: Superuser's email address
            fullname: Superuser's full name
            password: Superuser's password (optional)
            
        Returns:
            User: Created superuser instance
        """
        user = self.create_user(email, fullname, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Custom User model using email instead of username."""
    
    username = None
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']
    
    def __str__(self):
        """Return string representation of user."""
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'