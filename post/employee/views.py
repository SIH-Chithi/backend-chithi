from django.shortcuts import render
from accountpannel.functions import *
from .serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import pandas as pd
import csv
from collections import defaultdict

class create_employee(APIView):
    def post(self,request):
        try:
            data=request.data
            Employee_id=data['Employee_id']
            password=data['password']
            type=data['type']
            first_name=data['first_name']
            last_name=data['last_name']
            address=data['address']
            pincode=data['pincode']
            city_district=data['city_district']
            state=data['state']
            office_id=data['office_id']
            
            employee=Employee.objects.create(Employee_id=Employee_id,password=password,type=type,first_name=first_name,last_name=last_name,address=address,pincode=pincode,city_district=city_district,state=state,office_id=office_id)
            employee.make(password)
            employee.save()
            return Response({"message":"Employee created successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)    


#Login API for Employee: takes employee_id and password as input
class employee_login(APIView):
    def post(self,request):
        serializer=employee_token(data=request.data)
        if serializer.is_valid():
            return JsonResponse(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
