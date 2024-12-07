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
        
        search_fields = [field.name for field in model._meta.fields]
        
        list_filter = [
            field.name for field in model._meta.fields 
            if field.get_internal_type() in ['BooleanField', 'DateField', 'ForeignKey', 'IntegerField']
        ]
    
    try:
        admin.site.register(model, ModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass               
