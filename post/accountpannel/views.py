from django.shortcuts import render
from .functions import *
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

import psycopg2
from .routesss import create_graph_from_db, dijkstra    
db_config = settings.DATABASES["default"]


# Customer login : send otp to phone number
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

# Customer login : verify otp and generate token        
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
        
# Customer login : refresh token        
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
        
# Customer signup : send otp to phone number
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
        
# Customer signup : verify otp
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

# Customer signup : create user   
class customerregistration(APIView):
    
    
    def post(self,request):
        
            phone_number = request.data.get("phone_number")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            address_details = request.data.get("address_details")
            country = request.data.get("country")
            city_district = request.data.get("city_district")
            pincode = request.data.get("pincode")
            email = request.data.get("email")
            state = request.data.get("state")
            
    
            
            if not phone_number:
                return Response({"phone_number": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not first_name or not last_name or not address_details or not country or not city_district or not pincode or not state:
                return Response({"fields": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not User.objects.filter(phone_number=phone_number):
                return Response({"message":"user not exist"})
            user=User.objects.get(phone_number=phone_number)
            if customer.objects.filter(user=user):
                return Response({"message":"customer already exist"},status=status.HTTP_400_BAD_REQUEST)
            newuser=customer.objects.create(user=user, first_name=first_name, last_name=last_name, address_details=address_details, country=country, city_district=city_district, pincode=pincode,state=state, Email=email if email else None)    
            newuser.save()
            
            return Response({"message": "User registered successfully"}, status=status.HTTP_200_OK)
        


# get customer profile
class customer_profile(APIView):   
    authentication_classes = []
    permission_classes = [] 
    def get(self, request):
        try:
            token=request.headers["Authorization"]

            if not token:
                return Response({"token": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token=token.split(" ")[1]
            userid, phone_number,exp = decode_token(token)
            if not (userid or phone_number or exp):
                return Response({"token": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)  
            user = getuser(phone_number)
            if not user:
                return Response({"phone_number": "User does not exist with this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            
            Customer=customer.objects.get(user=user)
            if not Customer:
                return Response({"customer": "Customer does not exist with this user"}, status=status.HTTP_400_BAD_REQUEST)
            serializers= customerSerializer(Customer)
            return Response({"phone_number":phone_number,"data":serializers.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)   
        
#delete customer
class delcustomer(APIView):
    authentication_classes = []
    permission_classes = []
    
    def delete(self, request):
        try:
            token=request.headers["Authorization"]
            if not token:
                return Response({"token": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token=token.split(" ")[1]
            user_id, phone_number,exp = decode_token(token)
            if not (user_id or phone_number or exp):
                return Response({"token": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
            
            user= getuser(phone_number)
            if not user:
                return Response({"message": "User does not exist with this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
#book_consignment   
class book_consignment(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self,request):
        try:
            phone_number, user=token_process(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:    
            data=request.data
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if data["is_payed"]==False:
                return Response({"message": "Payment is required"}, status=status.HTTP_400_BAD_REQUEST)

            consignment_obj=consignment.objects.create(
                type=data["type"],
                user=user,
                created_place=phone_number,
                Amount=data["Amount"],
                is_payed=data["is_payed"],
                is_pickup=data["is_pickup"]
                )
            
            senders_details.objects.create(
                consignment_id=consignment_obj,
                first_name=data["sender"]["first_name"],
                last_name=data["sender"]["last_name"],
                pincode=data["sender"]["pincode"],
                address=data["sender"]["address"],
                city_district=data["sender"]["city_district"],
                state=data["sender"]["state"],
                country=data["sender"]["country"],
                phone_number=data["sender"]["phone_number"]
            )
            
            receiver_details.objects.create(
                consignment_id=consignment_obj,
                first_name=data["receiver"]["first_name"],
                last_name=data["receiver"]["last_name"],
                pincode=data["receiver"]["pincode"],
                address=data["receiver"]["address"],
                city_district=data["receiver"]["city_district"],
                state=data["receiver"]["state"],
                country=data["receiver"]["country"],
                phone_number=data["receiver"]["phone_number"]
            )
            
            if data["type"]=="parcel":
                if not data.get("parcel"):
                    return Response({"parcel": "Parcel details are required"}, status=status.HTTP_400_BAD_REQUEST)
                parcel.objects.create(
                    consignment_id=consignment_obj,
                    weight=data["parcel"]["weight"],
                    length=data["parcel"]["length"],
                    breadth=data["parcel"]["breadth"],
                    height=data["parcel"]["height"],
                    price=data["parcel"]["price"]
                )
            
            if data["is_pickup"]==True:
                consignment_pickup.objects.create(
                    consignment_id=consignment_obj,
                    pickup_date=data["pickup"]["pickup_date"],
                    pickup_time=data["pickup"]["pickup_time"],
                    pickup_amount=data["pickup"]["pickup_amount"]
                )    
            #getting nsh from pincode    
            source_nsh=get_nsh_from_pincode(data["sender"]["pincode"])
            destination_nsh=get_nsh_from_pincode(data["receiver"]["pincode"])
            
            #getting path from nsh
            sender_path_dic=get_path_from_pincode(data["sender"]["pincode"],"start")
            
            graph=create_graph_from_db(db_config,destination_nsh)
            distance, path, pathDic=dijkstra(graph, source_nsh, destination_nsh)
            
            receiver_path_dic=get_path_from_pincode(data["receiver"]["pincode"],"end")
            receiver_path_dic=reverse_dict(receiver_path_dic)
            merge_dic=merge_dicts(sender_path_dic,pathDic,receiver_path_dic)
            if distance==float('inf'):
                return Response({"error": "No path found between source and destination"}, status=status.HTTP_400_BAD_REQUEST)
            
            if consignment_route.objects.filter(consignment_id=consignment_obj):
                return Response({"message": "Consignment already booked"}, status=status.HTTP_400_BAD_REQUEST)
            
            obj=consignment_route.objects.create(consignment_id=consignment_obj,pointer="spo_start")
            obj.save_route(merge_dic)
            obj.save()
            
            
                
            return Response({"message": "Consignment booked successfully",
                        "consignment_id":consignment_obj.consignment_id}, status=status.HTTP_200_OK)   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)       
#calculate postage
class calculate_postage(APIView):
    
    def post(self,request):
        try:    
            data=request.data
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            pincode1 = data["sender_pincode"]
            pincode2 = data["receiver_pincode"]
            article_type=data["article_type"]
            service=data["service"]
            if article_type=='parcel':
                weight=data["weight"]
                
            
            if not pincode1 or not pincode2 or not article_type or not service :
                return Response({"fields": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            distance,error=calculate_distance(pincode1, pincode2)
            if error:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
            if article_type=='document':
                cost=calculate_document_cost(distance, service)
            
            elif article_type=='parcel':
                cost=calculate_cost(weight,distance,service)
                
            else:
                return Response({"error": "Invalid article type"}, status=status.HTTP_400_BAD_REQUEST)       
            
            return Response({"distance": distance, "cost": cost}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#getconsignment list
class get_consignment_list(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            phone_number, user=token_process(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            consignments=consignment.objects.filter(user=user)
            serializers=get_consignmentlist(consignments, many=True)
            if not serializers:
                return Response({"messages": "No consignments found"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#get consignment details:- giving consignment_id      
class get_consignment_details(APIView):
    def post(self,request):
        try:
            consignment_id=request.data.get("consignment_id")
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            order=consignment.objects.get(consignment_id=consignment_id)
            serializer={
                "consignment_id":order.consignment_id,
                "type":order.type,
                "created_date":order.created_date,
                "created_time":order.created_time,
                "Amount":order.Amount,
                "status":order.status,
                "service":order.service,
                "delivery_status":order.is_out_for_delivery
                
                }
            
            
            Senders_details=senders_details.objects.get(consignment_id=order)
            Receiver_details=receiver_details.objects.get(consignment_id=order)
            
            Sender_serializer=sender_details_serializer(Senders_details)
            Receiver_serializer=receiver_details_serializer(Receiver_details)
            
            
            journey=consignment_journey.objects.filter(consignment_id=consignment_id)
    
        
            if journey:
                seria=get_consignment_journey(journey, many=True)
                seria=seria.data
                
            else:
                seria=None
                
            if consignment_reviews.objects.filter(consignment_id=consignment_id):
                review=consignment_reviews.objects.get(consignment_id=consignment_id)
                rating=review.rating
            else:
                rating=None  
            
            return JsonResponse({"order": serializer, 
                                "sender": Sender_serializer.data,
                                "receiver": Receiver_serializer.data,
                                "rating": rating,
                            "journey": seria}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
            
#register complain
class register_complain(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            phone_number, user=token_process(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data    
            
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_id=data["consignment_id"]
            complain=data["complain"]
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            if not consignment_obj:
                return Response({"consignment_id": "Consignment does not exist with this id"}, status=status.HTTP_400_BAD_REQUEST)
            
            if consignment_obj.user!=user:
                return Response({"user": "User does not have permission to register complain for this consignment"}, status=status.HTTP_400_BAD_REQUEST)
            
            complain_obj=complains.objects.create(user=user,complain=complain, consignment_id=consignment_obj)
            
            return  Response({"message": "Complain registered successfully",
                            "complain_id":complain_obj.complain_id}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#get complains
class get_complains(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            phone_number, user=token_process(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            Complains=complains.objects.filter(user=user)
            serializers=get_complains_serializer(Complains, many=True)
            if not serializers:
                return Response({"messages": "No complains found"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        
        
        
class importdata(APIView):
    def get(self,request):
        csv_path = r"D:\backend-chithi\post\accountpannel\unique_pincode_data.csv"
        try:
            with open(csv_path, newline='',encoding='utf-8') as file:
                reader=csv.DictReader(file)
                pincodes=[]
                for row in reader:
                    try:
                        pincodes.append(pincode(
                            pincode=row['pincode'],
                            division_name=row['division_name'],
                            region_name=row['region_name'],
                            circle_name=row['circle_name'],
                            district_name=row['district_name'],
                            state_name=row['state_name']
                        ))
                    except KeyError as e:
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                        
                pincode.objects.bulk_create(pincodes,ignore_conflicts=True)
                return Response({"message": "Data imported successfully"}, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class importspo(APIView):
    def get(self,request):
        csv_path = r"D:\backend-chithi\post\accountpannel\suboffice.csv"
        try:
            with open(csv_path, newline='',encoding='utf-8') as file:
                reader=csv.DictReader(file)
                spos=[]
                for row in reader:
                    try:
                        pin=row['pincode']
                        pincodes=pincode.objects.get(pincode=pin)
                        spos.append(SPO(
                            pincode=pincodes,
                            office_name=row['office_name'],
                            divsion_name=row['division_name'],
                            region_name=row['region_name'],
                            circle_name=row['circle_name'],
                            district_name=row['district_name'],
                            state_name=row['state_name'],
                            
                        ))
                    except KeyError as e:
                        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                        
                SPO.objects.bulk_create(spos,ignore_conflicts=True)
                return Response({"message": "Data imported successfully"}, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)        
        



def import_hpo_csv_with_path(request):
    try:
        file_path = r"D:\backend-chithi\post\accountpannel\Modified_PincodeFile.csv"

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Preload all SPOs into a dictionary by pincode
            all_spos = SPO.objects.select_related('pincode').all()
            spo_dict = defaultdict(list)
            for spo in all_spos:
                spo_dict[spo.pincode.pincode].append(spo)

            # Collect HPOs for bulk creation
            hpo_objects = []
            hpo_mapping = {}
            new_hpos = []

            for row in reader:
                ho_pincode = int(row['HO Pincode'])
                office_name = row['Office Name']
                region_name = row['Region Name']
                division_name = row['Division Name']
                circle_name = row['Circle Name']
                district_name = row['District Name']
                state_name = row['State Name']

                hpo, created = HPO.objects.get_or_create(
                    ho_pincode=ho_pincode,
                    defaults={
                        'office_name': office_name,
                        'region_name': region_name,
                        'division_name': division_name,
                        'circle_name': circle_name,
                        'district_name': district_name,
                        'state_name': state_name,
                    }
                )

                if created:
                    new_hpos.append(hpo)
                else:
                    hpo_mapping[ho_pincode] = hpo

                # Add relationships between HPO and SPOs
                so_pincodes = eval(row['SO Pincodes'])
                for pincode in so_pincodes:
                    if pincode in spo_dict:
                        for spo in spo_dict[pincode]:
                            hpo.spo.add(spo)

            # Bulk create new HPOs
            HPO.objects.bulk_create(new_hpos)

        return JsonResponse({'message': 'CSV imported successfully with optimizations.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

class route(APIView):
    
    def post(self,request):

            data=request.data
            source=data["source"]
            destination=data["destination"]
            if not source or not destination:
                return Response({"fields": "Source and destination are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            graph=create_graph_from_db(db_config,destination)
            distance, path, pathDic=dijkstra(graph, source, destination)
            if distance==float('inf'):
                return Response({"error": "No path found between source and destination"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"distance": distance, "path": path, "pathDic": pathDic}, status=status.HTTP_200_OK)    
        
        
#post consignment reviews
class post_consignment_reviews(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            phone_number, user=token_process(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_id=data["consignment_id"]
            rating=data["rating"]
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            
            if not consignment_obj:
                return Response({"consignment_id": "Consignment does not exist with this id"}, status=status.HTTP_400_BAD_REQUEST)
            
            if consignment_reviews.objects.filter(consignment_id=consignment_obj):
                return Response({"message": "Review already posted for this consignment"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_reviews.objects.create(consignment_id=consignment_obj, rating=rating)
            
            return Response({"message": "Review posted successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get consignment reviews

class get_consignment_reviews(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            phone_number, user=token_process(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_id=data["consignment_id"]
            consignment_reviews_obj=consignment_reviews.objects.get(consignment_id=consignment_id)
            rating=consignment_reviews_obj.rating
            
            return Response({"rating": rating}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)