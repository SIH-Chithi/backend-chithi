from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from accountpannel.models import User, customer
from accountpannel.functions import *
from rest_framework_simplejwt.tokens import RefreshToken

class employeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class employee_token(serializers.Serializer):
    Employee_id = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        Employee_id = attrs.get("Employee_id")
        password = attrs.get("password")

        try:
            # Fetch the employee based on Employee_id
            employee = Employee.objects.get(Employee_id=Employee_id)

            # Check if the password matches
            if not employee.verify_password(password):
                raise serializers.ValidationError("Invalid password")

            # Generate a token
            refresh = RefreshToken()

            # Add custom claims
            refresh["Employee_id"] = employee.Employee_id
            refresh["Employee_type"] = employee.type

            return {
                "access": str(refresh),
                "refresh": str(refresh),
                "Employee_id": employee.Employee_id,
                "type": employee.type,
            }
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee does not exist")
        
class consignment_sender(serializers.ModelSerializer):
    class Meta:
        model = senders_details
        fields='__all__'
            
class consignment_receiver(serializers.ModelSerializer):
    class Meta:
        model = receiver_details
        fields='__all__'
        
class consignment_parcel(serializers.ModelSerializer):
    class Meta:
        model = parcel
        fields='__all__'        
    
class consignment_pickup_details(serializers.ModelSerializer):
    class Meta:
        model = consignment_pickup
        fields='__all__'               
        
class employee_details_serializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['Employee_id', 'first_name', 'last_name',   'type', 'address', 'pincode', 'city_district', 'state','office_id']            


class consignment_serializer(serializers.ModelSerializer):
    class Meta:
        model = consignment
        fields = ['consignment_id', 'type','service']
        
class container_qr_serializer(serializers.ModelSerializer):
    class Meta:
        model=container_qr
        fields=['barcode_url','qr_url']
        
        
class container_serializer(serializers.ModelSerializer):
    consignments = consignment_serializer(many=True, read_only=True)
    qr = container_qr_serializer(source='container_qr', read_only=True)

    class Meta:
        model = container
        fields = ['container_id','created_at','going_to','qr','consignments']
        
class container_journey_serializer(serializers.ModelSerializer):
    container=container_serializer(source='container_id')
    class Meta:
        model = container_journey
        fields = ['container_id','created_at','process','container']
        

class postman_consignment(serializers.ModelSerializer):
    receiver=consignment_receiver(source='receiver_details_set', many=True, read_only=True)
    
    class Meta:
        model = consignment
        fields=['consignment_id','type','service','status','receiver']
    
        
class consignments_serializer_postman(serializers.ModelSerializer):
    consignments = postman_consignment(source='consignment_id', read_only=True)    
    class Meta:
        model = postman_consignments
        fields = ['consignment_id','created_at','consignments']

