
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


from django.db.models.functions import TruncDay
from django.db.models import Count
from django.utils import timezone

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
            
            if consignment_qr.objects.filter(consignment_id=consignment_obj):
                consignment_qr_obj=consignment_qr.objects.get(consignment_id=consignment_obj)
                return Response({"message": "QR already generated",
                                "qr_url":consignment_qr_obj.qr_url,
                                "barcode_url":consignment_qr_obj.barcode_url}, status=status.HTTP_400_BAD_REQUEST)
                
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
            
            route=check(data["sender"]["pincode"],data["receiver"]["pincode"])    
            
            if route:
                obj=consignment_route.objects.create(consignment_id=consignment_obj,pointer="spo_start")
                obj.save_route(route)
                obj.save()
                
                return Response({"message": "Consignment booked successfully",
                                "consignment_id":consignment_obj.consignment_id}, status=status.HTTP_200_OK)
                
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
            
            return Response({"message": "consignment related to container successfully",
                            "consignment_id":consignment_id,
                            "service":consignment_obj.service,
                            "type":consignment_obj.type,
                            "created_time":consignment_obj.created_date}, status=status.HTTP_200_OK)
        
        except consignment.DoesNotExist:
            return Response({"error": "Consignment not found"},status=status.HTTP_404_NOT_FOUND)
            
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
            
        except consignment_route.DoesNotExist:
            return Response({"error": "Consignment route not found"},status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)
        
#delete consignment from container        

class delete_consignment_container(APIView):
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
            
            
            if not consignment.objects.filter(consignment_id=consignment_id):
                return Response({"message": "consignment not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not container.objects.filter(container_id=container_id):
                return Response({"message": "container not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            container_obj=container.objects.get(container_id=container_id)
            
            if not container_obj.consignments.filter(consignment_id=consignment_id):
                return Response({"message": "consignment not related to container"}, status=status.HTTP_400_BAD_REQUEST)
            
            container_obj.consignments.remove(consignment_obj)
            container_obj.save()
            
            return Response({"message": "consignment deleted from container successfully",
                            "consignment_id":consignment_id,
                            "service":consignment_obj.service,
                            "type":consignment_obj.type,
                            "created_time":consignment_obj.created_date}, status=status.HTTP_200_OK)
        
        except consignment.DoesNotExist:
            return Response({"error": "Consignment not found"},status=status.HTTP_404_NOT_FOUND)
            
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
            
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
            return Response({"message": "checked out successfully"}, status=status.HTTP_200_OK)
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
            
            return Response({"message": "checked in successfully"}, status=status.HTTP_200_OK)
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


#get list of container created today
class get_container_created_today(APIView):
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
            
            containers=container.objects.filter(created_office_id=employee.office_id,created_at__gte=today_start,
                created_at__lt=today_end)
            serializer=container_serializer(containers, many=True)
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
            
            if container_qr.objects.filter(container_id=container_obj):
                container_qr_obj=container_qr.objects.get(container_id=container_obj)
                return Response({"message": "QR already generated",
                                "qr_url":container_qr_obj.qr_url,
                                "barcode_url":container_qr_obj.barcode_url}, status=status.HTTP_400_BAD_REQUEST)
                
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
            
            route=check(data["sender"]["pincode"],data["receiver"]["pincode"])    
            
            if route:
                obj=consignment_route.objects.create(consignment_id=consignment_obj,pointer="hpo_start")
                obj.save_route(route)
                obj.save()
                
                return Response({"message": "Consignment booked successfully",
                                "consignment_id":consignment_obj.consignment_id}, status=status.HTTP_200_OK)
                
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
            if employee.type!="nsh":
                return Response({"error": "Only NSH employee can check in"}, status=status.HTTP_400_BAD_REQUEST)
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
            
            consignments=container_obj.consignments.all()
            counting=consignments.count()
            nsh_obj=NSH.objects.get(nsh_id=employee.office_id)
            threading.Thread(target=update_checkin_count, args=(nsh_obj,counting)).start()  #update checkin count
            
            container_journey.objects.create(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_in") 
            
            return Response({"message": "checked in successfully"}, status=status.HTTP_200_OK)
        
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# Check Out from NSH       
class checkout_NSH(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            if employee.type!="nsh":
                return Response({"error": "Only NSH employee can check out"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            container_id=data['container_id']
            container_obj=container.objects.get(container_id=container_id)
            
            if container_journey.objects.filter(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_out"):
                return Response({"message": "Container already checked out"}, status=status.HTTP_400_BAD_REQUEST) 
            
            consignments=container_obj.consignments.all()
            
            counting=consignments.count()
            
            nsh_obj=NSH.objects.get(nsh_id=employee.office_id)
            threading.Thread(target=update_checkout_count, args=(nsh_obj,counting)).start()  #update checkout count
            
            for consignment_obj in consignments:
                consignment_journey.objects.create(consignment_id=consignment_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_out")
                
            container_journey.objects.create(container_id=container_obj,created_at=employee.type,created_place_id=employee.office_id,process="check_out") 
            return Response({"message": "checked out successfully"}, status=status.HTTP_200_OK)
        except container.DoesNotExist:
            return Response({"error": "Container not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#class get traffic report       
class get_traffic_report(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            six_days=timezone.now()-timedelta(days=6)
            
            consignment_report=consignment_journey.objects.filter(created_at=employee.type,created_place_id=employee.office_id,date_time__gte=six_days,process="check_in").annotate(date=TruncDay('date_time')).values('date').annotate(count=Count('pk')).order_by('date')  #__gte stands for greater than equal to
            
            report = {entry['date'].strftime('%Y-%m-%d'): entry['count'] for entry in consignment_report}

            return JsonResponse({"report":report}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get specific report      
class specific_report(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            six_days_ago = timezone.now() - timedelta(days=6)
            
            all_categories = [
            "parcel speedpost",
            "parcel other",
            "document speedpost",
            "document other"
            ]
            
            report_data=consignment_journey.objects.filter(created_at=employee.type,created_place_id=employee.office_id,date_time__gte=six_days_ago,process="check_in"
                                                        ).values(
                                                            'date_time__date',  # Group by date
                                                            'consignment_id__type',  # Category (document/parcel)
                                                            'consignment_id__service'  # Subcategory (speedpost/other)
                                                        ).annotate(
                                                            count=Count('pk')  # Count the number of entries
                                                        ).order_by('date_time__date')
                                                        
            categorized_report = {}
            
            #initializing the every category with zero
            for i in range(6):  
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                categorized_report[date] = {category: 0 for category in all_categories}
                
                
            for entry in report_data:
                date = entry['date_time__date'].strftime('%Y-%m-%d')
                category = f"{entry['consignment_id__type']} {entry['consignment_id__service']}"
                
                if date not in categorized_report:
                    categorized_report[date] = {}
                
                categorized_report[date][category] = entry['count']
                
            return Response({"report": categorized_report}, status=status.HTTP_200_OK)    
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        

# POSTMAN

class postman_consignment_in(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data
            consignment_id=data['consignment_id']
            
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not consignment.objects.filter(consignment_id=consignment_id):
                return Response({"error": "Consignment not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj=consignment.objects.get(consignment_id=consignment_id)
            
            type=consignment_obj.type
            service=consignment_obj.service
            
            consignment_receiver = receiver_details.objects.get(consignment_id=consignment_obj)
            
            receiver_address=f"{consignment_receiver.address},{consignment_receiver.city_district},{consignment_receiver.state},{consignment_receiver.country}"
            receiver_pincode=consignment_receiver.pincode
            receiver_phone_number=consignment_receiver.phone_number
            
            postman_consignments.objects.create(consignment_id=consignment_obj,postman_id=Employee_id)
            
            consignment_obj.is_out_for_delivery=True
            
            return Response({"message": "consignment checked out successfully",
                            "consignment_id":consignment_id,
                            "type":type,
                            "service":service,
                            "receiver_address":receiver_address,
                            "receiver_pincode":receiver_pincode})
        
        except consignment.DoesNotExist:
            return Response({"error": "Consignment not found"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get todays consignments for postman

class get_postman_todays_consignments(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            today=date.today()
            today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            consignments=postman_consignments.objects.filter(postman_id=Employee_id,created_at__gte=today_start,
                created_at__lt=today_end).select_related('consignment_id')
            
            Serializer=consignments_serializer_postman(consignments, many=True)
            
            
            return Response(Serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#get all the consignments of postman
class get_postman_consignments(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            consignments=postman_consignments.objects.filter(postman_id=Employee_id).select_related('consignment_id')
            serializers=consignments_serializer_postman(consignments, many=True)
            
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#get consignment by id
class get_consignment_by_id(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)    
        
        try:
            data=request.data 
            consignment_id=data['consignment_id']
            
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj=postman_consignments.objects.get(consignment_id=consignment_id,postman_id=Employee_id)
            
            serializer=consignments_serializer_postman(consignment_obj)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#get old consignments of postman

class get_old_consignments_postman(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            start_of_today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            consignments=postman_consignments.objects.filter(postman_id=Employee_id,created_at__lt=start_of_today).select_related('consignment_id')

            
            serializer = consignments_serializer_postman(consignments, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
# scan consignment for delivery 

class scan_consignment(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data 
            consignment_id=data['consignment_id']
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not consignment.objects.filter(consignment_id=consignment_id):
                return Response({"error": "Consignment not found"}, status=status.HTTP_400_BAD_REQUEST)
                
            
            if not postman_consignments.objects.filter(consignment_id=consignment_id,postman_id=Employee_id):
                return Response({"error": "Consignment not assigned to postman"}, status=status.HTTP_400_BAD_REQUEST)
            
            consignment_obj = consignment.objects.get(consignment_id=consignment_id)
            
            receiver_details_obj = receiver_details.objects.get(consignment_id=consignment_obj)
            
            phone_number=receiver_details_obj.phone_number
            
            send_delivery_otp(phone_number,consignment_obj)
            
            return Response({"message": "Consignment scanned successfully"},status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#verify otp for delivery        
class verify_delivery_otp(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
            
            if employee.type!="postman":
                return Response({"error": "Only postman can check in"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data=request.data 
            consignment_id=data['consignment_id']
            otp=data['otp']
            
            if not consignment_id:
                return Response({"consignment_id": "Consignment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not otp:
                return Response({"otp": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not consignment.objects.filter(consignment_id=consignment_id):
                return Response({"error": "Consignment not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            if not postman_consignments.objects.filter(consignment_id=consignment_id,postman_id=Employee_id):
                return Response({"error": "Consignment not assigned to postman"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            consignment_obj = consignment.objects.get(consignment_id=consignment_id)
            
            if consignment_obj.status:
                return Response({"message": "Consignment already delivered"}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp_consignments.objects.filter(consignment_id=consignment_obj):
                return Response({"message": "No otp"}, status=status.HTTP_400_BAD_REQUEST)
            
            if verify_del_otp(otp,consignment_obj):
                consignment_obj.status=True
                consignment_obj.save()
                
                return Response({"message": "Consignment delivered successfully"},status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

#COMPLAINS SECTION

class get_complains(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self,request):
        try:
            employee, employee_type, Employee_id = token_process_employee(request)
        except ValueError as e:
            return Response({"error": str(e),"message":"invalid_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            type = employee.type
            office_id = employee.office_id
            
            
            
            #pending complains and resolved complains
            pending_complains = complains.objects.filter(status="pending",current_office_type=type,current_office_id=office_id)
            
            resolved_complains = complains.objects.filter(status="resolved",current_office_type=type,current_office_id=office_id)
            
            # transferred complains
            
            transferred_complains_ids = complain_journey.objects.filter(transferred_office_type = type ,transferred_office_id=office_id).values_list('complain_id',flat=True)
            
            transferred_complains = complains.objects.filter(complain_id__in=transferred_complains_ids)
            
            pending_serializer = list_complains_serializer(pending_complains, many=True)
            resolved_serializer = list_complains_serializer(resolved_complains, many=True)
            transferred_serializer = list_complains_serializer(transferred_complains, many=True)
            
            return Response({"pending_complains": pending_serializer.data,
                            "resolved_complains": resolved_serializer.data,
                            "transferred_complains": transferred_serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class get_complain_details(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id=token_process_employee(request)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            complain_id=request.data.get("complain_id")
            if not complain_id:
                return Response({"complain_id": "Complain id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            complain_obj=complains.objects.get(complain_id=complain_id)
            consignment_obj =  complain_obj.consignment_id
            consignment_route_obj=consignment_route.objects.get(consignment_id=consignment_obj)
            if not consignment_route_obj:
                return Response({"error": "Consignment route not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            route = consignment_route_obj.get_route()
            routes = add_office_name(route)
            serializer=complain_serializer(complain_obj)
            
            return JsonResponse({"complain": serializer.data,
                                "routes":routes}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        
# resolve complain or transfer complain

class process_complain(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self,request):
        try:
            employee, employee_type, Employee_id=token_process_employee(request)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        try:
            data=request.data
            complain_id=data['complain_id']
            
            
            if not complain_id:
                return Response({"complain_id": "Complain id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not complains.objects.filter(complain_id=complain_id,current_office_type=employee.type,current_office_id=employee.office_id):
                return Response({"error": "Complain not found "}, status=status.HTTP_400_BAD_REQUEST)
            
            complain_obj=complains.objects.get(complain_id=complain_id)
            
            if complain_obj.status=="resolved":
                return Response({"message": "Complain already resolved"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            stat = data['status']
            if not stat:
                return Response({"status": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if stat == "resolved":
                complain_obj=complains.objects.get(complain_id=complain_id)
                complain_obj.status="resolved"
                complain_obj.save()
                return Response({"message": "Complain resolved successfully"}, status=status.HTTP_200_OK)
            
            elif stat == "pending":
                complain_obj = complains.objects.get(complain_id=complain_id)
                comments = data['comment']
                if not comments:
                    return Response({"comment": "Comment is required"}, status=status.HTTP_400_BAD_REQUEST)
                transferred_office_type = data['office_type']
                transferred_office_id = data['office_id']
                complain_journey.objects.create(complain_id=complain_obj,transferred_office_type=employee.type, transferred_office_id=employee.office_id,comments=comments)
                complain_obj.status = "transferred" 
                complain_obj.current_office_type = transferred_office_type
                complain_obj.current_office_id = transferred_office_id
                complain_obj.save()
                
                return Response({"message": "Complain transferred successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            
            