from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta , datetime
from django.contrib.auth.hashers import make_password,check_password

# Create your models here
class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The phone number must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
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
    USER_ID_FIELD = 'phone_number'
    
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
    state=models.CharField(max_length=100,null=True,blank=True)
    pincode=models.CharField(max_length=50)
    Email=models.EmailField(blank=True,null=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Ensure that the field can only be set during object creation
            self.account_type = "Customer"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.user.phone_number} - {self.first_name} {self.last_name}"    
    
    
class pincode(models.Model):
    pincode=models.IntegerField(primary_key=True)
    division_name=models.CharField(max_length=50)
    region_name=models.CharField(max_length=50)
    circle_name=models.CharField(max_length=50)
    district_name=models.CharField(max_length=50)
    state_name=models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.pincode} - {self.district_name}, {self.state_name}"
    
class SPO(models.Model):
    spo_id=models.AutoField(primary_key=True)
    pincode=models.ForeignKey(pincode, on_delete=models.CASCADE)  
    office_name=models.CharField(max_length=100)
    divsion_name=models.CharField(max_length=50)
    circle_name=models.CharField(max_length=50)
    district_name=models.CharField(max_length=50)
    state_name=models.CharField(max_length=50)
    region_name=models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.spo_id} - {self.office_name}"
    
class HPO(models.Model):
    hpo_id = models.AutoField(primary_key=True)
    ho_pincode = models.IntegerField(unique=True)
    office_name = models.CharField(max_length=100)
    region_name = models.CharField(max_length=50)
    division_name = models.CharField(max_length=50)
    circle_name = models.CharField(max_length=50)
    district_name = models.CharField(max_length=50)
    state_name = models.CharField(max_length=50)
    spo = models.ManyToManyField(SPO, related_name='hpos')  # Many SPOs related to one HPO

    def __str__(self):
        return f"{self.hpo_id} - {self.office_name}"
    
    
class ICH(models.Model):
    ich_id=models.AutoField(primary_key=True)
    ich_pincode=models.IntegerField(unique=True)
    division_name=models.CharField(max_length=50)
    region_name=models.CharField(max_length=50)
    circle_name=models.CharField(max_length=50)
    district_name=models.CharField(max_length=50)
    state_name=models.CharField(max_length=50)
    office_name=models.CharField(max_length=100)
    hpo = models.ManyToManyField(HPO, related_name='ichs')  
    
    def __str__(self):
        return f"{self.ich_id} - {self.office_name}"

class NSH(models.Model):
        nsh_id=models.AutoField(primary_key=True)
        nsh_pincode=models.IntegerField(unique=True)
        division_name=models.CharField(max_length=50)
        region_name=models.CharField(max_length=50)
        circle_name=models.CharField(max_length=50)
        district_name=models.CharField(max_length=50)
        state_name=models.CharField(max_length=50)
        office_name=models.CharField(max_length=100)
        ich=models.ManyToManyField(ICH, related_name='nshs')
        
        def __str__(self):
            return f"{self.nsh_id} - {self.office_name}"
        
        
class senders_details(models.Model):
    consignment_id=models.ForeignKey('consignment', on_delete=models.CASCADE)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    pincode=models.IntegerField()
    address=models.TextField()
    city_district=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    phone_number=models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.consignment_id} - {self.first_name} {self.last_name}"


class receiver_details(models.Model):
    consignment_id=models.ForeignKey('consignment', on_delete=models.CASCADE)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    pincode=models.IntegerField()
    address=models.TextField()
    city_district=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    phone_number=models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.consignment_id} - {self.first_name} {self.last_name}"    
    

    
class consignment_pickup(models.Model):
    consignment_id=models.ForeignKey('consignment', on_delete=models.CASCADE)
    pickup_date=models.DateTimeField()
    pickup_time=models.TimeField()
    pickup_amount=models.FloatField()
    pickup_status=models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.consignment_id)    
    
class parcel(models.Model):
    consignment_id=models.OneToOneField('consignment', on_delete=models.CASCADE)
    parcel_id=models.AutoField(primary_key=True)
    weight=models.FloatField()
    length=models.FloatField()
    breadth=models.FloatField()
    height=models.FloatField()
    price=models.FloatField()    
    
    def __str__(self):
        return f"{self.consignment_id} - {self.parcel_id}"

parcel_types=(
    ('Document','Document'),
    ('Parcel','Parcel')
)  
class consignment(models.Model):        
    consignment_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    type=models.CharField(max_length=50,choices=parcel_types)
    created_place=models.CharField(max_length=10)
    created_date=models.DateTimeField(auto_now_add=True)
    created_time=models.TimeField(auto_now_add=True)
    Amount=models.FloatField()
    is_pickup=models.BooleanField(default=False)
    is_payed=models.BooleanField(default=False)
    status=models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.consignment_id} - {self.type}"
    
class consignment_qr(models.Model):
    consignment_id = models.OneToOneField('consignment', on_delete=models.CASCADE)    
    barcode_url=models.URLField()
    qr_url=models.URLField()
    created_date=models.DateTimeField(auto_now_add=True)
    created_by=models.CharField(max_length=50)
    created_by_id=models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.consignment_id} - {self.created_by}"
    
office_types=(
    ('spo','spo'),
    ('hpo','hpo'),
    ('ich','ich'),
    ('nsh','nsh')
)  

process=(
    ('check_in','check_in'),
    ('check_out','check_out')
)
class consignment_journey(models.Model):
    consignment_id=models.ForeignKey('consignment', on_delete=models.CASCADE)
    created_at=models.CharField(max_length=50,choices=office_types)  
    created_place_id=models.IntegerField()
    date_time=models.DateTimeField(auto_now_add=True)
    process=models.CharField(max_length=10,choices=process)
    
    def __str__(self):
        return f"{self.consignment_id} - {self.created_at}"
    
    
class adjacent_nsh_data(models.Model):
    nsh1=models.ForeignKey('NSH',on_delete=models.CASCADE,related_name='nsh1_relations') 
    nsh2=models.ForeignKey('NSH',on_delete=models.CASCADE,related_name='nsh2_relations')
    time=models.IntegerField(blank=True,null=True)  #in minutes
    traffic=models.IntegerField(blank=True,null=True)
    capacity=models.IntegerField(blank=True,null=True)
    
    
    def __str__(self):
        return f"{self.nsh1}-{self.nsh2}"
    
    
class complains(models.Model):
    complain_id=models.AutoField(primary_key=True)
    consignment_id=models.ForeignKey('consignment', on_delete=models.CASCADE)    
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_on=models.DateTimeField(auto_now_add=True)
    complain=models.TextField()
    status=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.complain_id} - {self.consignment_id}"

   
class Employee(models.Model):
    Employee_id=models.CharField(max_length=50,primary_key=True)
    password=models.CharField(max_length=128)
    type=models.CharField(max_length=50,choices=office_types)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    address=models.TextField()
    pincode=models.IntegerField()
    city_district=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    office_id=models.IntegerField()
    
    def make(self,password):
        passwords=make_password(password)
        self.password=passwords
        self.save()
        return passwords
        
    def verify_password(self, password):
        return check_password(password, self.password)    
    
    def __str__(self):
        return f"{self.Employee_id} - {self.first_name} {self.last_name}"
