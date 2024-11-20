from django.contrib import admin
from django.apps import apps
from .models import User, customer
from .admin_utils import *


app_models = apps.get_app_config('accountpannel').get_models()

for model in  app_models:
    class  ModelResource(GenericResource):
        class Meta:
            model = model
            
    class ModelAdmin(ImportExportAdmin):
        resource_class = ModelResource
    
    try:
        admin.site.register(model, ModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass               
