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
        

class get_consignmentlist(serializers.ModelSerializer):
    class Meta:
        model=consignment
        fields=['consignment_id','created_date','status','Amount','type']
        
class get_consignment_journey(serializers.Serializer):
    created_at=serializers.CharField()
    created_place_id=serializers.CharField()
    date_time=serializers.DateTimeField()
    process=serializers.CharField()
    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Extract the created_place_id and process fields
        created_place_id = representation.get("created_place_id")
        created_at = representation.get("created_at")

        if created_at == "spo":
            try:
                spo = SPO.objects.get(spo_id=created_place_id)
                representation["created_place_name"] = spo.office_name
            except SPO.DoesNotExist:
                representation["created_place_name"] = "Unknown SPO"
        elif created_at == "hpo":
            try:
                hpo = HPO.objects.get(hpo_id=created_place_id)
                representation["created_place_name"] = hpo.office_name
            except HPO.DoesNotExist:
                representation["created_place_name"] = "Unknown HPO"
        elif created_at == "ich":
            try:
                ich = ICH.objects.get(ich_id=created_place_id)
                representation["created_place_name"] = ich.office_name
            except ICH.DoesNotExist:
                representation["created_place_name"] = "Unknown ICH"
        elif created_at == "nsh":
            try:
                nsh = NSH.objects.get(nsh_id=created_place_id)
                representation["created_place_name"] = nsh.office_name
            except NSH.DoesNotExist:
                representation["created_place_name"] = "Unknown NSH"
        else:
            representation["created_place_name"] = "Invalid Process"

        # Remove created_place_id and add created_place_name for clarity
        del representation["created_place_id"]
        return representation
                
class get_complains_serializer(serializers.ModelSerializer):
    class Meta:
        model=complains
        fields=['complain_id','consignment_id','complain','status','created_on']

class sender_details_serializer(serializers.ModelSerializer):
    class Meta:
        model=senders_details
        fields='__all__'
        
class receiver_details_serializer(serializers.ModelSerializer):
    class Meta:
        model=receiver_details
        fields='__all__'
        
        
        
                
""" class employeetoken(TokenObtainPairSerializer):
    employee_id = serializers.CharField()
    password = serializers.CharField(write_only=True) 
    
    def validate(self, attrs):
        employee_id= attrs.get("employee_id")
        password= attrs.get("password")
        
        try:
            user= employee.objects.get(employee_id=employee_id) """
