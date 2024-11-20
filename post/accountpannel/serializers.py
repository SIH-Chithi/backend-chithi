from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User, customer
from .functions import *


class customertoken(TokenObtainPairSerializer):
    phone_number = serializers.CharField()
    otp= serializers.CharField()
    
    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        try:
            user= User.objects.get(phone_number=phone_number)
            if not verify_otp(attrs.get("otp"), phone_number):
                raise serializers.ValidationError("Invalid OTP")
            
            #Generate token
            refresh = self.get_token(user)
            refresh.payload['user_id'] = user.user_id
            refresh.payload['phone_number'] = user.phone_number
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token), 
                'phone_number': user.phone_number   
            }
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist with this phone number")
        
class customerSerializer(serializers.ModelSerializer):
    class Meta:
        model = customer
        fields = ['first_name', 'last_name', 'address_details', 'country', 'city_district', 'pincode', 'Email','state']      
        
          


""" class employeetoken(TokenObtainPairSerializer):
    employee_id = serializers.CharField()
    password = serializers.CharField(write_only=True) 
    
    def validate(self, attrs):
        employee_id= attrs.get("employee_id")
        password= attrs.get("password")
        
        try:
            user= employee.objects.get(employee_id=employee_id) """