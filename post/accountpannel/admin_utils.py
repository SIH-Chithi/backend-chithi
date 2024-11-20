from import_export.admin import ImportExportMixin
from import_export import resources
from django.contrib import admin


class GenericResource(resources.ModelResource):
    class Meta:
        abstract = True
        
class ImportExportAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class  = GenericResource       