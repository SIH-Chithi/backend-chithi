from django.urls import path
from .views import *

urlpatterns = [
    path('create_employee/', create_employee.as_view(), name='create_employee'),
    path('employee_login/', employee_login.as_view(), name='employee_login'),
    path('access_byrefresh/', get_access_byrefresh.as_view(), name='access_byrefresh'),
    path('get_consignment_details/', get_consignment_details.as_view(), name='get_consignment_details'),
    path("generate_qr/", generate_qr_view.as_view(), name="generate_qr"),
    path('update_consignment/', update_consignment_details.as_view(), name='update_consignment'),
    path('book_consignment_spo/', book_consignment_spo.as_view(), name='book_consignment_spo'),
    path('create_container/', create_container.as_view(), name='create_container'),
    path('get_employee_details/', employee_details.as_view(), name='get_employee_details'),
    path('get_containers/', get_containers.as_view(), name='get_containers'),
    path('get_container_details/', get_details_container.as_view(), name='get_container_details'),
    path('relate_consignment_container/', relate_consignment_container.as_view(), name='relate_consignment_container'),
    path('checkout/', checkout.as_view(), name='checkout_to_hpo'),
    path('get_checkout_container/', get_container_checked_out.as_view(), name='get_checkout_container'),
    path('checkin/', checkin.as_view(), name='checkin_to_spo'),
    path('get_checkin_container/', get_container_checked_in.as_view(), name='get_checkin_container'),
    path('generate_container_qr/',generate_qr_container.as_view(),name='generate_container_qr'),
    path('book_consignment_hpo/', book_consignment_hpo.as_view(), name='book_consignment_hpo'),
    path('secondary_sort/', secondary_sorting.as_view(), name='secondary_sorting'),
    
    #NSH
    path('preliminary_sort/', preliminary_sorting.as_view(), name='preliminary_sorting'),
    path('checkin_to_nsh/', checkin_NSH.as_view(), name='checkin_to_nsh'),

]


