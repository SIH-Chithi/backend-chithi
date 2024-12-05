from .models import *
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

from geopy.geocoders import Nominatim
from geopy.distance import geodesic


def verify_otp(otp,phone_number):
    try:
        user=User.objects.get(phone_number=phone_number)
        if not user:
            return False
        if user.otp_code==otp and user.otp_expiry>timezone.now():
            user.otp_code=None
            user.otp_expiry=None
            user.is_phone_verified=True
            user.save()
            return True
    except User.DoesNotExist:
        return False


def generate_otp():
    import random
    return random.randint(100000,999999)    
    
def send_otp(phone_number):
    try:
        user=User.objects.get(phone_number=phone_number)
        if not user:
            return False
        otp=generate_otp()
        message=f"Your verification code is {otp}"
        payload={
            'from':"Vonage APIs",
            "to":int(str(91)+str(phone_number)),
            'text':message,
            'api_key':settings.VONAGE_API_KEY,
            'api_secret':settings.VONAGE_API_SECRET
        }
        url="https://rest.nexmo.com/sms/json"
        response = sendsms(payload,url) 
        if response==True:    
            user.otp_code=otp
            user.otp_expiry=timezone.now()+timedelta(minutes=10)
            india_timezone = pytz.timezone('Asia/Kolkata')
            user.otp_expiry = user.otp_expiry.astimezone(india_timezone)
            user.save()
            threading.Timer(50000,delete_otp,args=[phone_number]).start()
            return True
        return False
    except User.DoesNotExist:
        return False
            

def delete_otp(phone_number):
    try:
        user = User.objects.get(phone_number=phone_number)
        user.otp_code = None
        user.otp_expiry = None
        user.save()
    except User.DoesNotExist:
        pass    
    
    
    
def sendsms(payload,url):
    response = requests.post(url, data=payload)
    if response.status_code==200:
        return True
    else:
        return False    
    
    
def send_otplogin(phone_number):
    try:
        otp=generate_otp()
        message=f"Your verification code is {otp}"
        payload={
            'from':"Vonage APIs",
            "to":int(str(91)+str(phone_number)),
            'text':message,
            'api_key':settings.VONAGE_API_KEY,
            'api_secret':settings.VONAGE_API_SECRET
        }
        url="https://rest.nexmo.com/sms/json"
        response = sendsms(payload,url) 
        if response==True: 
            if User.objects.filter(phone_number=phone_number).exists():
                user=User.objects.get(phone_number=phone_number)
                otp_expiry=timezone.now()+timedelta(minutes=10)
                india_timezone = pytz.timezone('Asia/Kolkata')
                otp_expiry = otp_expiry.astimezone(india_timezone) 
                user.otp_code=otp
                user.otp_expiry=otp_expiry
                user.save()
                return True
            otp_expiry=timezone.now()+timedelta(minutes=10)
            india_timezone = pytz.timezone('Asia/Kolkata')
            otp_expiry = otp_expiry.astimezone(india_timezone)   
            user=User.objects.create_user(phone_number=phone_number,is_phone_verified=False,otp_code=otp,otp_expiry=otp_expiry)
            user.save()
            threading.Timer(150,delete_otp,args=[phone_number]).start()
            threading.Timer(600,delete_user,args=[phone_number]).start()
            return True
        return False
    except User.DoesNotExist:
        return False    
    
    
    
def delete_user(phone_number):
    try:
        user = User.objects.get(phone_number=phone_number)
        if user.is_phone_verified==False:
            user.delete()    
    except User.DoesNotExist:
        pass           
    
def decode_token(token):
    try:
        decodetoken = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=['HS256'], options={"verify_exp": True})
        user_id = decodetoken.get('user_id')
        phone_number = decodetoken.get('phone_number')
        exp = datetime.utcfromtimestamp(decodetoken['exp']) 
        
        if user_id and phone_number:
            user=User.objects.get(user_id=user_id)
            return user_id, phone_number,exp
        
        else:
            return None
    except ExpiredSignatureError:
        return None    
    
    
    
def getuser(phone_number):
    try:
        user=User.objects.get(phone_number=phone_number)
        return user
    except User.DoesNotExist:
        return None    
    
    
cloudinary.config(
    cloud_name = os.getenv('cloud_name'),
    api_key = os.getenv('api_key'),
    api_secret=os.getenv('api_secret'),
    secure=True
)    


# Generate QR code and barcode
#payload=consignment_id

def generate_qr(payload):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code in memory
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Upload QR code to Cloudinary
    qr_response = cloudinary.uploader.upload(
        qr_buffer,
        public_id=f"consignments/{payload}_qr",
        folder="consignments"
    )
    qr_url = qr_response.get("secure_url")

    # Generate Barcode
    barcode_buffer = BytesIO()
    barcode = Code128(payload, writer=ImageWriter())
    barcode.write(barcode_buffer)
    barcode_buffer.seek(0)

    # Upload Barcode to Cloudinary
    barcode_response = cloudinary.uploader.upload(
        barcode_buffer,
        public_id=f"consignments/{payload}_barcode",
        folder="consignments"
    )
    barcode_url = barcode_response.get("secure_url")

    return {
        "qr_code_url": qr_url,
        "barcode_url": barcode_url
    }

#return NSH from pincode            
def get_path_from_pincode(pin, process):
    try:
        if not pin:
            return Response({"pincode": "Pincode is required"}, status=status.HTTP_400_BAD_REQUEST)

        if process not in ["start", "end"]:
            return Response({"process": "Invalid process value. Use 'start' or 'end'."}, status=status.HTTP_400_BAD_REQUEST)

        route = {}
        suffix = process  # 'start' or 'end'

        pins = pincode.objects.get(pincode=pin)
        spos = SPO.objects.filter(pincode=pins).first()
        route[f'spo_{suffix}'] = spos.spo_id

        hpos = HPO.objects.get(spo=spos)
        route[f'hpo_{suffix}'] = hpos.hpo_id

        ichs = ICH.objects.get(hpo=hpos)
        route[f'ich_{suffix}'] = ichs.ich_id

        nsh = NSH.objects.get(ich=ichs)
        route[f'nsh_{suffix}'] = nsh.nsh_id

        return route
    except Exception as e:
        return e
    
def get_nsh_from_pincode(pin):
    try:
        if not pin:
            raise ValueError("Pincode is required")

        pins = pincode.objects.get(pincode=pin)
        spos = SPO.objects.filter(pincode=pins).first()
        hpos = HPO.objects.get(spo=spos)
        ichs = ICH.objects.get(hpo=hpos)
        nsh = NSH.objects.get(ich=ichs)

        return nsh.nsh_id        
    
    except Exception as e:
        raise ValueError(str(e))

    
 
def reverse_dict(dictionary):
    return dict(reversed(list(dictionary.items())))

def merge_dicts(dict1, dict2, dict3):
    return dict1 | dict2 | dict3
    
#calculate postage


def calculate_distance(pincode1, pincode2):
    """Calculate the distance between two pincodes."""
    geolocator = Nominatim(user_agent="pincode_distance_calculator")

    try:
        # Get the locations for both pincodes
        location1 = geolocator.geocode(pincode1)
        location2 = geolocator.geocode(pincode2)

        if location1 is None or location2 is None:
            return None, "One or both pincodes could not be resolved to a location."

        # Extract coordinates
        coords_1 = (location1.latitude, location1.longitude)
        coords_2 = (location2.latitude, location2.longitude)

        # Calculate distance
        distance = geodesic(coords_1, coords_2).kilometers
        return distance, None

    except Exception as e:
        return None, f"An error occurred: {e}"


def calculate_document_cost(distance, post_name):
    """Calculate the cost for sending documents."""
    if post_name.lower() == "speedpost":
        if distance <= 200:
            return 35
        elif distance <= 1000:
            return 41
        elif distance <= 2000:
            return 47
        else:
            return 53
    else:
        if distance <= 200:
            return 20
        elif distance <= 1000:
            return 30
        else:
            return 42


def calculate_cost(weight, distance, post_name):
    """Calculate the cost based on weight and distance."""
    if post_name.lower() == "speedpost":
        if weight <= 50:
            if distance <= 8:
                return 18
            elif distance <= 200:
                return 41
            elif distance <= 1000:
                return 41
            elif distance <= 2000:
                return 41
            else:
                return 41
        elif weight > 50 and weight <= 200:
            if distance < 8:
                return 30
            elif distance <= 200:
                return 41
            elif distance <= 1000:
                return 47
            elif distance <= 2000:
                return 71
            else:
                return 83
        elif weight > 200 and weight <= 500:
            if distance < 8:
                return 35
            elif distance <= 200:
                return 59
            elif distance <= 1000:
                return 71
            elif distance <= 2000:
                return 94
            else:
                return 106
        elif weight > 500 and weight <= 1000:
            if distance < 8:
                return 47
            elif distance <= 200:
                return 77
            elif distance <= 1000:
                return 106
            elif distance <= 2000:
                return 142
            else:
                return 165
        elif weight > 1000 and weight <= 1500:
            if distance < 8:
                return 59
            elif distance <= 200:
                return 94
            elif distance <= 1000:
                return 142
            elif distance <= 2000:
                return 189
            else:
                return 224
        elif weight > 1500 and weight <= 2000:
            if distance < 8:
                return 71
            elif distance <= 200:
                return 112
            elif distance <= 1000:
                return 177
            elif distance <= 2000:
                return 236
            else:
                return 283
        elif weight > 2000 and weight <= 2500:
            if distance < 8:
                return 83
            elif distance <= 200:
                return 130
            elif distance <= 1000:
                return 212
            elif distance <= 2000:
                return 283
            else:
                return 342
        elif weight > 2500 and weight <= 3000:
            if distance < 8:
                return 94
            elif distance <= 200:
                return 148
            elif distance <= 1000:
                return 248
            elif distance <= 2000:
                return 330
            else:
                return 401
        elif weight > 3000 and weight <= 3500:
            if distance < 8:
                return 106
            elif distance <= 200:
                return 165
            elif distance <= 1000:
                return 283
            elif distance <= 2000:
                return 378
            else:
                return 460
        elif weight > 3500 and weight <= 4000:
            if distance < 8:
                return 118
            elif distance <= 200:
                return 183
            elif distance <= 1000:
                return 319
            elif distance <= 2000:
                return 425
            else:
                return 519
        elif weight > 4000 and weight <= 4500:
            if distance < 8:
                return 130
            elif distance <= 200:
                return 201
            elif distance <= 1000:
                return 354
            elif distance <= 2000:
                return 472
            else:
                return 578
        elif weight > 4500 and weight <= 5000:
            if distance < 8:
                return 142
            elif distance <= 200:
                return 218
            elif distance <= 1000:
                return 389
            elif distance <= 2000:
                return 519
            else:
                return 637
        else:
            return 0
    else:
        if weight<=500:
            if distance<8:
                return 30
            elif distance<=200:
                return 50
            elif distance<=1000:
                return 60
            elif distance<=2000:
                return 70
            elif distance<=5000:
                return 90
            else:
                return 0
        
        elif weight<=1000 and weight<5000:
                if distance<8:
                    return 38
                elif distance<=200:
                    return 64
                elif distance<=1000:
                    return 78
                elif distance<=2000:
                    return 100
                elif distance<=5000:
                    return 110
                else:
                    return 0
        
        else:
                if distance<8:
                    return 40
                elif distance<=200:
                    return 66
                elif distance<=1000:
                    return 80
                elif distance<=2000:
                    return 102
                elif distance<=5000:
                    return 112
                else:
                    return 0
            
            

#token 
def token_process(request):
    try:
        token = request.headers.get("Authorization")  # Use .get() to avoid KeyError
        if not token:
            raise ValueError("Token is required")

        token = token.split(" ")[1]
        user_id, phone_number, exp = decode_token(token)
        if not (user_id and phone_number and exp):
            raise ValueError("Invalid token")

        user = getuser(phone_number)
        if not user:
            raise ValueError("User does not exist with this phone number")

        return phone_number, user

    except Exception as e:
        raise ValueError(str(e))
    

#for postman   
def send_delivery_otp(phone_number,consignment_obj):
    try:
        if not otp_consignments.objects.filter(consignment_id=consignment_obj).exists():
            obj=otp_consignments.objects.create(consignment_id=consignment_obj)
            obj.save()
        else: 
            obj=otp_consignments.objects.get(consignment_id=consignment_obj)
            if obj.created_count>=3:
                raise ValueError("You have reached the maximum limit of otp generation")
            
        otp=generate_otp()
        message=f"Your otp code for the consignment {consignment_obj.consignment_id} is {otp}"
        payload={
            'from':"Vonage APIs",
            "to":int(str(91)+str(phone_number)),
            'text':message,
            'api_key':settings.VONAGE_API_KEY,
            'api_secret':settings.VONAGE_API_SECRET
        }
        url="https://rest.nexmo.com/sms/json"
        response = sendsms(payload,url) 
        if response==True:  
            obj.otp=otp
            obj.otp_expiry=timezone.now()+timedelta(minutes=10)
            obj.created_count=obj.created_count+1
            obj.save()
            threading.Timer(50000,delete_delivery_otp,args=[consignment_obj]).start()
            return True
        return False
    except ValueError as e:
        raise ValueError(str(e))


def verify_del_otp(otp,consignment_obj):
    try:
        obj=otp_consignments.objects.get(consignment_id=consignment_obj)
        if not obj:
            raise ValueError("No otp found")
        if not obj:
            return False
        if obj.otp==otp and obj.otp_expiry>timezone.now():
            obj.delete()
            return True
    except otp_consignments.DoesNotExist:
        return False
    
def delete_delivery_otp(consignment_obj):
    try:
        obj=otp_consignments.objects.get(consignment=consignment_obj)
        obj.delete()
    except otp_consignments.DoesNotExist:
        pass    


def start_complain_journey(consignment_obj,complain_obj):
    try:
        consignment_route_obj=consignment_route.objects.get(consignment_id=consignment_obj)
        
        route=consignment_route_obj.get_route()
        nsh_start=route['nsh_start']
        
        complain_obj.status="pending"
        complain_obj.nsh_office=nsh_start
        
        complain_obj.current_office_type="nsh"
        complain_obj.current_office_id=nsh_start
        
        complain_obj.save()
        
    
    except consignment_route.DoesNotExist:
        raise ValueError("Consignment not found")
    
    except Exception as e:
        raise ValueError(str(e))



    
        