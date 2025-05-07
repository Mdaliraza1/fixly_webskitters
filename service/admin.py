from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'price')
    search_fields = ('category',)
    list_filter = ('category',)
