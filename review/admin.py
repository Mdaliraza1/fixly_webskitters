from django.contrib import admin
from django.db.models import Avg
from .models import User

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'contact', 'user_type', 'category', 'average_rating')
    list_filter = ('user_type', 'category')
    search_fields = ('email', 'first_name', 'last_name', 'contact')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Annotate with average rating only for service providers
        return qs.annotate(avg_rating=Avg('reviews_received__rating'))

    def average_rating(self, obj):
        # Show average rating rounded to 2 decimals or "-" if none
        return round(obj.avg_rating, 2) if obj.avg_rating else "-"
    average_rating.admin_order_field = 'avg_rating'
    average_rating.short_description = 'Avg Rating'
