
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta , datetime
import threading
import vonage
import pytz
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError
import jwt
from django.conf import settings
import requests
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.http import JsonResponse
from accountpannel.models import *
from rest_framework.exceptions import AuthenticationFailed
from jwt import ExpiredSignatureError, InvalidTokenError
from django.core.exceptions import ObjectDoesNotExist
from functools import wraps
from django.db.models import F 



# Function to decode the JWT token
def decode_token_employee(token):
    try:
        # Decode the JWT token
        decodetoken = jwt.decode(
            token,
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithms=['HS256'],
            options={"verify_exp": True}
        )        
        # Extract required fields from the token
        Employee_id = decodetoken.get('Employee_id')
        Employee_type = decodetoken.get('Employee_type')
        exp = datetime.utcfromtimestamp(decodetoken['exp'])
        
        # Validate fields
        if not Employee_id or not Employee_type:
            raise AuthenticationFailed("Invalid token: Employee_id or Employee_type missing.")
        
        # Retrieve the employee object
        try:
            employee = Employee.objects.get(Employee_id=Employee_id)
            return employee, employee.type, Employee_id
        except ObjectDoesNotExist:
            raise AuthenticationFailed("Employee not found.")
    
    except ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired.")
    
    except InvalidTokenError:
        raise AuthenticationFailed("Invalid token.")
    
    except Exception as e:
        raise AuthenticationFailed(f"An error occurred during token decoding: {str(e)}")


#  
def token_process_employee(request):
    try:
        token = request.headers['Authorization']
        token=token.split(" ")[1]
        employee, employee_type, Employee_id = decode_token_employee(token)
        return employee, employee_type, Employee_id
    except KeyError:
        raise AuthenticationFailed("Authorization header missing.")
    except AuthenticationFailed as e:
        raise e
    except Exception as e:
        raise AuthenticationFailed(f"An error occurred during token processing: {str(e)}")
    
    
    


def employee_required(*allowed_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Extract token from the Authorization header
            print(request.headers)
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authorization token is missing or invalid.'}, status=401)
            
            token = auth_header.split(' ')[1]

            try:
            
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                employee_id = decoded_token.get('Employee_id')  

                try:
                    employee = Employee.objects.get(Employee_id=employee_id)
                except Employee.DoesNotExist:
                    return JsonResponse({'error': 'Employee not found.'}, status=404)

                # checking
                if allowed_role != employee.type:
                    return JsonResponse({'error': 'Access forbidden for this role.'}, status=403)
                
                request.employee = employee

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired.'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token.'}, status=401)

            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def next_destination(route, point):
    if not route:
        raise Exception("Route is empty")
    
    try:
        keys = list(route.keys())
        index = keys.index(point)
        
        if index + 1 < len(keys):
            next_key = keys[index + 1]
            next_value = route[next_key]
        else:
            raise Exception("No next destination available")
        
        
        office_type = next_key[:3]  
        office_mapping = {
            "spo": SPO.objects.get,
            "hpo": HPO.objects.get,
            "ich": ICH.objects.get,
            "nsh": NSH.objects.get,
        }
        
        if office_type in office_mapping:
            office = office_mapping[office_type](**{f"{office_type}_id": next_value})
            return office.office_name, next_value
        else:
            raise Exception("Invalid Office Type")
    
    except ValueError:
        raise Exception(f"Point '{point}' not found in route")
    except Exception as e:
        raise Exception(str(e))
    
def update_next_destination(consignments,employee):
    if not consignments:
        raise Exception("Consignment list is empty")
    
    try:
        for consignment in consignments:
            consignment_route_obj=consignment_route.objects.get(consignment_id=consignment)
            route=consignment_route_obj.get_route()
            point=consignment_route_obj.pointer
            if not route:
                raise Exception("Route is empty")

            keys = list(route.keys())
            index = keys.index(point)
        
            if index + 1 < len(keys):
                next_key = keys[index + 1]
                next_value = route[next_key]
                
            else:
                raise Exception("No next destination available")
        
            consignment_route_obj.pointer=next_key
            consignment_route_obj.save()
        return True
    except ValueError:
        raise Exception(f"Point '{point}' not found in route")
    
# Function to update the next destination of a consignment   
def update_next(consignment,employee):
    try:
        consignment_route_obj=consignment_route.objects.get(consignment_id=consignment)
        route=consignment_route_obj.get_route()
       
        point=consignment_route_obj.pointer
        if not route:
            raise Exception("Route is empty")

        keys = list(route.keys())
        index = keys.index(point)
        
        if index + 1 < len(keys):
            next_key = keys[index + 1]
            next_value = route[next_key]

        else:
            raise Exception("No next destination available")
        
        consignment_route_obj.pointer=next_key
        consignment_route_obj.save()
        return True
    except consignment_route.DoesNotExist:
        raise Exception("Consignment not found")
    except ValueError:
        raise Exception(f"Point '{point}' not found in route")
    
# Function to update the traffic count of the adjacent NSHs  
def update_checkin_count(nsh_obj,counting):
    try:
        if adjacent_nsh_data.objects.filter(nsh2=nsh_obj).exists():
            data=adjacent_nsh_data.objects.filter(nsh2=nsh_obj)
            for i in data:
                i.traffic=i.traffic+counting  
                i.save()                                  
    except Exception as  e:
        return Response({"error",str(e)},status=status.HTTP_400_BAD_REQUEST)

# Function to update the checkout    
def update_checkout_count(nsh_obj,counting):
    try:
        if adjacent_nsh_data.objects.filter(nsh2=nsh_obj).exists():
            data=adjacent_nsh_data.objects.filter(nsh2=nsh_obj)
            for i in data:
                i.traffic=i.traffic-counting  
                i.save()                                  
    except Exception as  e:
        return Response({"error",str(e)},status=status.HTTP_400_BAD_REQUEST)
    
#get complains of a office

def get_complains_of_office(office_type,office_id):
    try:
        complaints = complain_journey.objects.filter(to_type=office_type,to_id=office_id,complain_status="pending"or"passed")
        return complaints
    except Exception as e:
        raise Exception(str(e))
    
#get route with office name
from django.db.models import Q

def add_office_name(route):
    try:
        updated_route = {}
        
        for key, value in route.items():
            
            office_type= key[:3]
            
            if office_type == "spo":
                office_name=SPO.objects.get(spo_id=value).office_name
            elif office_type == "hpo":
                office_name=HPO.objects.get(hpo_id=value).office_name
            elif office_type == "ich":
                office_name=ICH.objects.get(ich_id=value).office_name
            elif office_type == "nsh":
                office_name=NSH.objects.get(nsh_id=value).office_name
            else:
                office_name="none"
                
            updated_route[key]= {
                "id": value,
                "name": office_name
            }
        return updated_route
    except Exception as e:
        raise Exception(str(e))
    