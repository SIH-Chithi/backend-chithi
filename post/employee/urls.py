from django.urls import path
from .views import *

urlpatterns = [
    path('create_employee/', create_employee.as_view(), name='create_employee'),
    path('employee_login/', employee_login.as_view(), name='employee_login'),
    path('get_consignment_details/', get_consignment_details.as_view(), name='get_consignment_details'),
    path("generate_qr/", generate_qr_view.as_view(), name="generate_qr"),
    path('update_consignment/', update_consignment_details.as_view(), name='update_consignment'),
    path('book_consignment_spo/', book_consignment_spo.as_view(), name='book_consignment_spo'),
]

