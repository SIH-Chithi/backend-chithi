from django.shortcuts import render
from .functions import *
from .serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.
class customerlogin(APIView):
    def post(self, request):
        try:
            phone_number = request.data.get("phone_number")
            if not phone_number:
                return Response({"phone_number": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user=User.objects.get(phone_number=phone_number)
            if not user:
                return Response({"phone_number": "User does not exist with this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            
            send_otp(phone_number)
            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"phone_number": "User does not exist with this phone number"}, status=status.HTTP_400_BAD_REQUEST)    
        
class verifyotp(APIView):
    def post(self, request):
        try:
            phone_number = request.data.get("phone_number")
            otp = request.data.get("otp")
            if not phone_number or not otp:
                return Response({"phone_number": "Phone number and OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = customertoken(data=request.data)            
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"phone_number": "User does not exist with this phone number"}, status=status.HTTP_400_BAD_REQUEST)
        
class customerrefreshtoken(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"refresh": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            refresh_token=RefreshToken(refresh_token)
            user= User.objects.get(user_id=refresh_token.payload["user_id"])       
            
            if not user:
                return Response({"user": "User does not exist with this user id"}, status=status.HTTP_400_BAD_REQUEST) 
            
            if user.is_phone_verified==False:
                return Response({"user": "token not valid"}, status=status.HTTP_400_BAD_REQUEST)
            
            access_token = str(refresh_token.access_token)
            return Response({"access": access_token}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"user": "User does not exist with this user id"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class customersignup(APIView):
    def post(self,request):
        try:
            phone_number = request.data.get("phone_number")
            if not phone_number:
                return Response({"phone_number": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)        
            
            if User.objects.filter(phone_number=phone_number).exists() and User.objects.get(phone_number=phone_number).is_phone_verified==True:
                return Response({"phone_number": "User already exists with this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            otp=send_otplogin(phone_number)
            if otp==True:
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            return Response({"message": "OTP not sent"}, status=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class customersignupverify(APIView):
    def post(self,request):
        try:
            phone_number = request.data.get("phone_number")
            otp = request.data.get("otp")
            if not phone_number or not otp:
                return Response({"phone_number": "Phone number and OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not verify_otp(otp, phone_number):
                return Response({"otp": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"phone_number": "User does not exist with this phone number"}, status=status.HTTP_400_BAD_REQUEST)
        
class customerregistration(APIView):
    def post(self,request):
        try:
            phone_number = request.data.get("phone_number")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            address_details = request.data.get("address_details")
            country = request.data.get("country")
            city_district = request.data.get("city_district")
            pincode = request.data.get("pincode")
            email = request.data.get("email")
            
            if not phone_number:
                return Response({"phone_number": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not first_name or not last_name or not address_details or not country or not city_district or not pincode:
                return Response({"fields": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
                
            user=User.objects.get(phone_number=phone_number)
            print(user)
            newuser=customer.objects.create(user=user, first_name=first_name, last_name=last_name, address_details=address_details, country=country, city_district=city_district, pincode=pincode, Email=email if email else None)    
            newuser.save()
            
            return Response({"message": "User registered successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)