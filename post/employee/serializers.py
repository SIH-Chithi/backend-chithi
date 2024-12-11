from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from accountpannel.models import User, customer
from accountpannel.functions import *
from rest_framework_simplejwt.tokens import RefreshToken
from accountpannel.serializers import *

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
        

class consignment_details_serializer(serializers.ModelSerializer):        
    sender=consignment_sender(source='sender_details_set', many=True, read_only=True)
    receiver=consignment_receiver(source='receiver_details_set', many=True, read_only=True)
    parcel=consignment_parcel(source='parcel_details_set', many=True, read_only=True)
    pickup=consignment_pickup_details(source='consignment_pickup_set', many=True, read_only=True)
    journey = get_consignment_journey(source='consignment_journey_set', many=True, read_only=True)
    
    class Meta:
        model = consignment
        fields = ['consignment_id','type','service','status','sender','receiver','parcel','pickup','journey']

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
        

        
class complain_journey_serializer(serializers.ModelSerializer):
    transferred_office_name = serializers.SerializerMethodField()
    class Meta:
        model = complain_journey
        fields = ['transferred_office_type','transferred_office_id','transferred_office_name','transferred_at','comments']        
        
    
    def get_transferred_office_name(self, obj):
        type=obj.transferred_office_type
        id=obj.transferred_office_id
        
        if type == "nsh":
            return NSH.objects.get(nsh_id=id).office_name
        elif type == "ich":
            return ICH.objects.get(ich_id=id).office_name
        elif type == "hpo":
            return HPO.objects.get(hpo_id=id).office_name
        elif type == "spo":
            return SPO.objects.get(spo_id=id).office_name
        
        else:
            return None
        
class complain_serializer(serializers.ModelSerializer):
    consignment_details=consignment_details_serializer(source='consignment_id')
    nsh_office_name = serializers.SerializerMethodField()
    current_office_name = serializers.SerializerMethodField()
    journey = complain_journey_serializer(source='complain_journey_set', many=True, read_only=True)
    class Meta:
        model = complains
        fields = ['complain_id','consignment_id','consignment_details','created_on','complain','status','nsh_office','nsh_office_name','current_office_type','current_office_id','current_office_name','journey'] 
        
    def get_nsh_office_name(self, obj):
        id=obj.nsh_office    
        
        return NSH.objects.get(nsh_id=id).office_name
    
    def get_current_office_name(self, obj):
        type=obj.current_office_type
        id=obj.current_office_id
        
        if type == "nsh":
            return NSH.objects.get(nsh_id=id).office_name
        elif type == "ich":
            return ICH.objects.get(ich_id=id).office_name
        elif type == "hpo":
            return HPO.objects.get(hpo_id=id).office_name
        elif type == "spo":
            return SPO.objects.get(spo_id=id).office_name
        
        else:
            return None
        
class list_complains_serializer(serializers.ModelSerializer):
    class Meta:
        model = complains
        fields = ['complain_id','consignment_id','created_on','complain','status']
        
class get_system_serializer(serializers.ModelSerializer):
    
    class Meta:
        model = system_complain
        fields = ['complain_id','consignment_id','created_time','message','delayed_time'] 

class get_system_complain_details_serializer(serializers.ModelSerializer):
    consignment_details=consignment_details_serializer(source='consignment_id')
    class Meta:
        model = system_complain
        fields = ['complain_id','consignment_id','created_time','message','consignment_details','delayed_time']