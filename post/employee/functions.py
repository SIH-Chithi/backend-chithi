
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
    