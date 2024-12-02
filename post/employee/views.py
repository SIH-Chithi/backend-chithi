
from accountpannel.functions import *
from accountpannel.serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .functions import *
from .serializers import *
from accountpannel.routesss import *
from datetime import date
import threading

db_config = settings.DATABASES["default"]
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

#get access token by refresh token

class get_access_byrefresh(APIView):
    def post(self,request):
        try:
            data=request.data
            refresh=RefreshToken(data['refresh'])
            if not refresh:
                return Response({"error":"Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
            access=str(refresh.access_token)
            
            return Response({"access":access}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
#Login API for Employee: takes employee_id and password as input
class employee_login(APIView):
    def post(self,request):
        serializer=employee_token(data=request.data)
        if serializer.is_valid():
            return JsonResponse(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#class get consignment details
class get_consignment_details(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id=token_process_employee(request)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
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
                "is_pickup":order.is_pickup,
                
                }
            #getting sender details
            sender=senders_details.objects.get(consignment_id=consignment_id)
            sender_serializer=consignment_sender(sender)
            #getting receiver details
            Receiver_details=receiver_details.objects.get(consignment_id=consignment_id)
            receiver_serializer=consignment_receiver(Receiver_details)
            #getting parcel details
            if order.type=="parcel":
                Parcel=parcel.objects.get(consignment_id=consignment_id)
                parcel_serializer=consignment_parcel(Parcel)
                parcel_details=parcel_serializer.data
            else:
                parcel_details=None    
            
            if order.is_pickup:
                pickup=consignment_pickup.objects.get(consignment_id=consignment_id)
                pickup_serializer=consignment_pickup_details(pickup)
                pickup_details=pickup_serializer.data
            else:
                pickup_details=None
                    
            journey=consignment_journey.objects.filter(consignment_id=consignment_id)
            
            barcode=consignment_qr.objects.filter(consignment_id=consignment_id)
            if barcode:
                barcode=consignment_qr.objects.get(consignment_id=consignment_id)
                barcodeurl=barcode.barcode_url
                qrurl=barcode.qr_url
            else:
                barcodeurl=None
                qrurl=None  
    
        
            if journey:
                seria=get_consignment_journey(journey, many=True)
                seria=seria.data
                
            else:
                seria=None
            
            return JsonResponse({"order": serializer, 
                                "sender_details": sender_serializer.data,
                                "receiver_details": receiver_serializer.data,
                                "parcel_details": parcel_details,
                                "pickup_details": pickup_details,
                                "barcode_url": barcodeurl,
                                "qr_url": qrurl,
                            "journey": seria}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  
        
class generate_qr_view(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id=token_process_employee(request)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:    
            data=request.data
            consignment_id=data['consignment_id']
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)        
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            if not consignment_obj:
                return Response({"error": "Consignment does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            urls=generate_qr(str(consignment_id))
            if urls:
                qr_obj=consignment_qr.objects.create(consignment_id=consignment_obj, barcode_url=urls['barcode_url'], qr_url=urls['qr_code_url'],created_by_id=Employee_id)
                return JsonResponse({"consignment_id":consignment_id,
                                    "urls":urls}, status=status.HTTP_200_OK)
            return Response({"error": "QR generation failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            
#update consignment details
class update_consignment_details(APIView):
    authentication_classes = []
    permission_classes = []

    def put(self, request):
        try:
            # Authenticate employee
            employee, employee_type, Employee_id = token_process_employee(request)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate consignment_id
            consignment_id = request.data.get("consignment_id")
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the consignment
            try:
                order = consignment.objects.get(consignment_id=consignment_id)
            except consignment.DoesNotExist:
                return Response({"error": "Consignment not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update consignment fields
            order.is_payed = request.data.get("is_payed", order.is_payed)
            order.type = request.data.get("type", order.type)
            order.service = request.data.get("service", order.service)
            order.Amount = request.data.get("Amount", order.Amount) 
            order.save()

            # Update sender details
            try:
                sender = senders_details.objects.get(consignment_id=consignment_id)
                sender.first_name = request.data.get("sender_first_name", sender.first_name)
                sender.last_name = request.data.get("sender_last_name", sender.last_name)
                sender.address = request.data.get("sender_address", sender.address)
                sender.phone_number = request.data.get("sender_phone_number", sender.phone_number)
                sender.save()
            except senders_details.DoesNotExist:
                return Response({"error": "Sender details not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update receiver details
            try:
                receiver = receiver_details.objects.get(consignment_id=consignment_id)
                receiver.first_name = request.data.get("receiver_first_name", receiver.first_name)
                receiver.last_name = request.data.get("receiver_last_name", receiver.last_name)
                receiver.address = request.data.get("receiver_address", receiver.address)
                receiver.phone_number = request.data.get("receiver_phone_number", receiver.phone_number)
                receiver.save()
            except receiver_details.DoesNotExist:
                return Response({"error": "Receiver details not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update parcel details (if type is 'parcel')
            if order.type == "parcel" and request.data.get("type")=="parcel":
                try:
                    parcel_details = parcel.objects.get(consignment_id=consignment_id)
                    parcel_details.weight = request.data.get("parcel_weight", parcel_details.weight)
                    parcel_details.length = request.data.get("parcel_length", parcel_details.length)
                    parcel_details.breadth = request.data.get("parcel_breadth", parcel_details.breadth)
                    parcel_details.height = request.data.get("parcel_height", parcel_details.height)
                    parcel_details.price = request.data.get("parcel_price", parcel_details.price)
                    parcel_details.save()
                except parcel.DoesNotExist:
                    return Response({"error": "Parcel details not found"}, status=status.HTTP_404_NOT_FOUND)
                
            elif order.type == "document" and request.data.get("type")=="parcel":
                try:
                    parcel_obj=parcel.objects.create(consignment_id=order, weight=request.data.get("parcel_weight"), length=request.data.get("parcel_length"), breadth=request.data.get("parcel_breadth"), height=request.data.get("parcel_height"), price=request.data.get("parcel_price"))
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
                
            elif order.type == "parcel" and request.data.get("type")=="document":
                try:
                    parcel_obj=parcel.objects.get(consignment_id=consignment_id)
                    parcel_obj.delete()
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
                    


            return Response({"message": "Consignment updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#book consignment by spo      
class book_consignment_spo(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:    
            data=request.data
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if data["is_payed"]==False:
                return Response({"message": "Payment is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user=User.objects.get(phone_number=data["sender"]["phone_number"])
            if not user:
                return Response({"error": "sender must be register first"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj=consignment.objects.create(
                type=data["type"],
                user=user,
                created_place=f"{employee.office_id}-spo",
                Amount=data["Amount"],
                is_payed=data["is_payed"],
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
            
            obj=consignment_route.objects.create(consignment_id=consignment_obj,route=merge_dic,pointer="spo_start")
            obj.save()
            
            
                
            return Response({"message": "Consignment booked successfully",
                        "consignment_id":consignment_obj.consignment_id}, status=status.HTTP_200_OK)   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    

#create container
class create_container(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:    
            type=employee.type
            office_id=employee.office_id
            
            
            container_obj=container.objects.create(
                created_by=Employee_id,
                created_office_type=type,
                created_office_id=office_id,
                )
            container_obj.save()
            return Response({"message": "Container created successfully",
                            "container_id":container_obj.container_id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get Employee details

class employee_details(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            serializer=employee_details_serializer(employee)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#get containers of the office
class get_containers(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            containers=container.objects.filter(created_office_id=employee.office_id)
            serializer=container_serializer(containers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#relating consignments to container

class relate_consignment_container(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            consignment_id=data['consignment_id']
            container_id=data['container_id']
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            container_obj=container.objects.get(container_id=container_id)

            
            if container_obj.consignments.filter(consignment_id=consignment_id):
                return Response({"message": "consignment already related to container"}, status=status.HTTP_400_BAD_REQUEST)
            
            if container_obj.consignments.count()==0:
                consignment_route_obj=consignment_route.objects.get(consignment_id=consignment_obj)
                point=consignment_route_obj.pointer
                Route=consignment_route_obj.get_route()
                office_name,office_id=next_destination(Route,point)
                container_obj.going_to=f"{office_id}_{office_name}"
                container_obj.save()

            container_obj.consignments.add(consignment_obj)
            container_obj.save()    
            
            consignment_journey.objects.create(consignment_id=consignment_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in")
            
            return Response({"message": "consignment related to container successfully"}, status=status.HTTP_200_OK)
        
        except consignment.DoesNotExist:
            return Response({"error": "Consignment not found"},status=status.HTTP_404_NOT_FOUND)
            
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
            
        except consignment_route.DoesNotExist:
            return Response({"error": "Consignment route not found"},status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        
#get details inside the container

class get_details_container(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            container_id=data['container_id']
            container_obj=container.objects.get(container_id=container_id)
            serializer=container_serializer(container_obj)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#check out container 

class checkout(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            container_id=data['container_id']
            container_obj=container.objects.get(container_id=container_id)
            if container_journey.objects.filter(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_out"):
                return Response({"message": "Container already checked out"}, status=status.HTTP_400_BAD_REQUEST)
            consignments=container_obj.consignments.all()
            for consignment_obj in consignments:
                consignment_journey.objects.create(consignment_id=consignment_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_out")
                
            container_journey.objects.create(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_out")
            return Response({"message": "checked out successfully"}, status=status.HTTP_400_BAD_REQUEST)
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get list of containers checked out today 
from django.utils.timezone import now, make_aware
from datetime import timedelta
class get_container_checked_out(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            today=date.today()
            today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            containers=container_journey.objects.filter(created_at=employee.type,created_place_id=employee.office_id,process="check_out",date_time__gte=today_start,
                date_time__lt=today_end).select_related('container_id') 
            serializer=container_journey_serializer(containers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)        

#check in to spo
class checkin(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            container_id=data['container_id']
            container_obj=container.objects.get(container_id=container_id)
            if container_journey.objects.filter(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in"):
                return Response({"message": "Container already checked in"}, status=status.HTTP_400_BAD_REQUEST)
            consignments=container_obj.consignments.all()
            
            for consignment_obj in consignments:
                consignment_journey.objects.create(consignment_id=consignment_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in")   
                
            container_journey.objects.create(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in")
            
            threading.Thread(target=update_next_destination, args=(consignments,employee)).start()  #start thread to update next destination
            
            return Response({"message": "checked in successfully"}, status=status.HTTP_400_BAD_REQUEST)
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get containers checked in today
class get_container_checked_in(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            today=date.today()
            today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            containers=container_journey.objects.filter(created_at=employee.type,created_place_id=employee.office_id,process="check_in",date_time__gte=today_start,
                date_time__lt=today_end).select_related('container_id') 
            serializer=container_journey_serializer(containers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    


#generate qr for container
class generate_qr_container(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id=token_process_employee(request)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:    
            data=request.data
            container_id=data['container_id']
            if not container_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)        
            
            container_obj=container.objects.get(container_id=container_id)
            if not container_obj:
                return Response({"error": "Container does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            urls=generate_qr(str(container_id))
            if urls:
                container_qr.objects.create(container_id=container_obj, barcode_url=urls['barcode_url'], qr_url=urls['qr_code_url'],created_by_id=Employee_id)
                return JsonResponse({"container_id":container_id,
                                    "urls":urls}, status=status.HTTP_200_OK)
            return Response({"error": "QR generation failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
# HPO START

class book_consignment_hpo(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:    
            data=request.data
            if not data:
                return Response({"data": "Data is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if data["is_payed"]==False:
                return Response({"message": "Payment is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user=User.objects.get(phone_number=data["sender"]["phone_number"])
            if not user:
                return Response({"error": "sender must be register first"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj=consignment.objects.create(
                type=data["type"],
                user=user,
                created_place=f"{employee.office_id}-spo",
                Amount=data["Amount"],
                is_payed=data["is_payed"],
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
            
            obj=consignment_route.objects.create(consignment_id=consignment_obj,route=merge_dic,pointer="hpo_start")
            obj.save()
            
            
                
            return Response({"message": "Consignment booked successfully",
                        "consignment_id":consignment_obj.consignment_id}, status=status.HTTP_200_OK)   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        
        
        
#Secondary sorting
class secondary_sorting(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            consignment_id=data['consignment_id']
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            if not consignment_obj:
                return Response({"error": "Consignment not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_route_obj=consignment_route.objects.get(consignment_id=consignment_obj)
            
            if not consignment_route_obj:
                return Response({"error": "Consignment route not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            route=consignment_route_obj.get_route()
            point=consignment_route_obj.pointer
            office_name,office_id=next_destination(route,point)
            
            return Response({"office_id":office_id,"office_name":office_name,"consignment_id":consignment_id}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#NSH :- National sorting hub

class preliminary_sorting(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            consignment_id=data['consignment_id']
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if consignment_journey.objects.filter(consignment_id=consignment_id,created_at=employee.type,created_place_id=employee.office_id,process="check_in"):
                return Response({"message": "Consignment already checked in"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            
            update_next(consignment_id,employee)
            
            consignment_journey.objects.create(consignment_id=consignment_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in")
            
            return Response({"service":consignment_obj.service,"consignment_id":consignment_id,"type":consignment_obj.type}, status=status.HTTP_200_OK)
            
        except consignment.DoesNotExist:
            return Response({"error": "Consignment not found"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
# Check In to NSH

class checkin_NSH(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data
            container_id=data['container_id']
            
            if not container_id:
                return Response({"container_id": "Container id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            container_obj=container.objects.get(container_id=container_id)
            if not container_obj:
                return Response({"error": "Container not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            if container_journey.objects.filter(container_id=container_id,created_at=employee.type,created_place_id=employee.office_id,process="check_in"):
                return Response({"message": "Container already checked in"}, status=status.HTTP_400_BAD_REQUEST)
            
            container_journey.objects.create(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in")
            
            return Response({"message": "checked in successfully"}, status=status.HTTP_200_OK)
        
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        