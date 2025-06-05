from django.contrib import admin
from django.urls import path
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter

from .models import User, UserToken
from booking.models import Booking
from review.models import Review
from service.models import Service

import datetime

admin.site.site_header = "Fixly Admin Dashboard"
admin.site.site_title = "Fixly Admin Portal"
admin.site.index_title = "Welcome to Fixly Admin Panel"


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'contact', 'user_type', 'category', 'average_rating')
    list_filter = ('user_type', 'category')
    search_fields = ('email', 'first_name', 'last_name', 'contact')
    ordering = ('email',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(avg_rating=Avg('reviews_received__rating'))

    def average_rating(self, obj):
        return round(obj.avg_rating, 2) if obj.avg_rating else "-"
    average_rating.admin_order_field = 'avg_rating'
    average_rating.short_description = 'Avg Rating'


class ServiceProviderFilter(SimpleListFilter):
    title = 'Service Provider'
    parameter_name = 'service_provider'

    def lookups(self, request, model_admin):
        providers = User.objects.filter(user_type='SERVICE_PROVIDER').values_list('id', 'first_name', 'last_name')
        return [(str(id), f"{first} {last}") for id, first, last in providers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service_provider_id=self.value())
        return queryset


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'service_provider_name', 'date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', ServiceProviderFilter, 'date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                     'service_provider__email', 'service_provider__first_name', 'service_provider__last_name')
    ordering = ('-created_at',)
    list_editable = ('status', 'time_slot')

    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.admin_order_field = 'user__first_name'
    user_name.short_description = 'User Name'

    def service_provider_name(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name}"
    service_provider_name.admin_order_field = 'service_provider__first_name'
    service_provider_name.short_description = 'Service Provider Name'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer_info', 'provider_info', 'rating', 'comment', 'created_at')
    search_fields = (
        'reviewer__first_name', 'reviewer__last_name', 'reviewer__email',
        'service_provider__first_name', 'service_provider__last_name', 'service_provider__email',
        'comment'
    )
    list_filter = ('rating', 'created_at', 'service_provider__category')

    def reviewer_info(self, obj):
        return f"{obj.reviewer.first_name} {obj.reviewer.last_name} ({obj.reviewer.email})"
    reviewer_info.short_description = 'Reviewer'

    def provider_info(self, obj):
        return f"{obj.service_provider.first_name} {obj.service_provider.last_name} ({obj.service_provider.email})"
    provider_info.short_description = 'Service Provider'


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'price')
    search_fields = ('category',)
    list_filter = ('category',)


# Dashboard admin with charts and filters

class DashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/dashboard.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard-data/', self.admin_site.admin_view(self.dashboard_data), name="dashboard-data"),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        categories = Service.objects.values_list('category', flat=True).distinct()
        extra_context = extra_context or {}
        extra_context['categories'] = categories
        return super().changelist_view(request, extra_context=extra_context)

    def dashboard_data(self, request):
        # Fetch filter params
        category = request.GET.get('category')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        filters = {}
        if category and category != 'all':
            filters['service_provider__category__category'] = category
        if start_date:
            filters['date__gte'] = start_date
        if end_date:
            filters['date__lte'] = end_date

        # Bookings per day
        bookings = Booking.objects.filter(**filters).values('date').annotate(count=Count('id')).order_by('date')
        bookings_data = list(bookings)

        # Average ratings by category
        rating_filters = {}
        if category and category != 'all':
            rating_filters['service_provider__category__category'] = category

        avg_rating = Review.objects.filter(**rating_filters).aggregate(avg=Avg('rating'))['avg'] or 0

        data = {
            'bookings': bookings_data,
            'average_rating': round(avg_rating, 2)
        }
        return JsonResponse(data)


admin.site.register(User, CustomUserAdmin)

admin.site.register(Booking, BookingAdmin)
admin.site.register(Review, ReviewAdmin)

admin.site.register(Service, DashboardAdmin)  # Register Dashboard on Service model (dummy)


