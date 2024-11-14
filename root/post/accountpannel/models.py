from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here
class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    phone_number = models.CharField(unique=True, max_length=15)
    is_phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.phone_number
    
class customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type=models.CharField(max_length=50,editable=False)  
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    address_details=models.TextField()
    country=models.CharField(max_length=50)
    city_district=models.CharField(max_length=50)
    pincode=models.CharField(max_length=50)
    Email=models.EmailField(blank=True,null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Ensure that the field can only be set during object creation
            self.account_type = "Customer"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.phone_number} - {self.first_name} {self.last_name}"    