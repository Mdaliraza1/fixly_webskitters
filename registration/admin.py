from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.db.models import Count, Avg
from service.models import Service
from booking.models import Booking
from review.models import Review
from registration.models import User

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
        category = request.GET.get('category')
        filters = {}
        if category and category != 'all':
            filters['service_provider__category__category'] = category

        bookings_by_category = Booking.objects.filter(**filters).values('service_provider__category__category') \
            .annotate(count=Count('id')).order_by('-count')

        bookings_by_provider = Booking.objects.filter(**filters).values(
            'service_provider__first_name',
            'service_provider__last_name'
        ).annotate(count=Count('id')).order_by('-count')[:10]

        ratings_by_provider = Review.objects.filter(**filters).values(
            'service_provider__first_name',
            'service_provider__last_name'
        ).annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:10]

        user_type_counts = User.objects.values('user_type').annotate(count=Count('id'))

        reviews_by_category = Review.objects.filter(**filters).values('service_provider__category__category') \
            .annotate(count=Count('id')).order_by('-count')

        return JsonResponse({
            'bookings_by_category': list(bookings_by_category),
            'bookings_by_provider': list(bookings_by_provider),
            'ratings_by_provider': list(ratings_by_provider),
            'user_type_counts': list(user_type_counts),
            'reviews_by_category': list(reviews_by_category),
        })

# Replace this with any dummy model or existing one like Service
from service.models import Service
admin.site.register(Service, DashboardAdmin)
