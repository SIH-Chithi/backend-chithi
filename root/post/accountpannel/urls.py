from django.urls import path
from .views import *

urlpatterns = [
    path('customerlogin/', customerlogin.as_view(), name='customerlogin'),
    path('verifyotp/', verifyotp.as_view(), name='verifyotp'),
    path('customerrefreshtoken/', customerrefreshtoken.as_view(), name='customerrefreshtoken'),
    path('customersignup/', customersignup.as_view(), name='customerregister'),
    path('customersignupverify/', customersignupverify.as_view(), name='customersignupverify'),
    path('customerregister/', customerregistration.as_view(), name='customerregister'),
]
