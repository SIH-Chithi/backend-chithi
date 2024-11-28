from django.urls import path
from .views import *

urlpatterns = [
    path('customerlogin/', customerlogin.as_view(), name='customerlogin'),
    path('verifyotp/', verifyotp.as_view(), name='verifyotp'),
    path('customerrefreshtoken/', customerrefreshtoken.as_view(), name='customerrefreshtoken'),
    path('customersignup/', customersignup.as_view(), name='customerregister'),
    path('customersignupverify/', customersignupverify.as_view(), name='customersignupverify'),
    path('customerregister/', customerregistration.as_view(), name='customerregister'),
    path('resendotp/', customerlogin.as_view(), name='resendotp'),
    path('customerprofile/', customer_profile.as_view(), name='customerprofile'),
    path('customerdelete/', delcustomer.as_view(), name='customerdelete'),
    path('pincode/', importdata.as_view(), name='pincode'),
    path('importspo/', importspo.as_view(), name='importspo'),
    path('importhpo/', import_hpo_csv_with_path, name='importhpo'),
    path('bookconsignment/', book_consignment.as_view(), name='bookconsignment'),
    path('calculatefare/', calculate_postage.as_view(), name='calculatefare'),
    path('getconsignmentlist/', get_consignment_list.as_view(), name='getconsignmentlist'),
    path('getconsignmentdetails/', get_consignment_details.as_view(), name='getconsignmentdetails'),
    path('registercomplaint/', register_complain.as_view(), name='registercomplaint'),
    path('getcomplaintlist/', get_complains.as_view(), name='getcomplaintlist'),
    path('getroute/', route.as_view(), name='getroute'),
]
