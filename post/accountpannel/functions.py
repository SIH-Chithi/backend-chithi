from .models import *
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import threading
import vonage
import pytz

from django.conf import settings
import requests


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
            otp_expiry=timezone.now()+timedelta(minutes=10)
            india_timezone = pytz.timezone('Asia/Kolkata')
            otp_expiry = otp_expiry.astimezone(india_timezone)   
            user=User.objects.create_user(phone_number=phone_number,is_phone_verified=False,otp_code=otp,otp_expiry=otp_expiry)
            user.save()
            threading.Timer(50000,delete_otp,args=[phone_number]).start()
            return True
        return False
    except User.DoesNotExist:
        return False    