from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg
from django.urls import path
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import format_html
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import User, UserToken, Dashboard
from .forms import CustomUserChangeForm, CustomUserCreationForm
from utils.admin_actions import export_as_csv_action
from service.models import Service
from booking.models import Booking
from review.models import Review

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'get_rating', 'get_bookings', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'contact', 'location')
    ordering = ('email',)
    filter_horizontal = ()  # Remove groups and user_permissions
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'contact', 'location')}),
        ('Service Provider Info', {'fields': ('user_type', 'category', 'description', 'experience', 'profile_picture')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'username', 'first_name', 'last_name', 'user_type', 'category'),
        }),
    )
    
    def get_rating(self, obj):
        if hasattr(obj, 'rating_avg'):
            return round(obj.rating_avg, 1) if obj.rating_avg else 0
        return 0
    get_rating.short_description = 'Rating'
    
    def get_bookings(self, obj):
        if hasattr(obj, 'booking_count'):
            return obj.booking_count
        return 0
    get_bookings.short_description = 'Bookings'
    
    actions = [
        export_as_csv_action(
            description="Export selected users to CSV",
            fields=['email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location']
        )
    ]

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__email', 'user__username', 'token')
    ordering = ('-created_at',)

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dashboard.html'

    def get_urls(self):
        urls = [
            path('', self.admin_site.admin_view(self.changelist_view), name='registration_dashboard_changelist'),
        ]
        return urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Dashboard'
        extra_context['categories'] = Service.objects.values_list('category', flat=True).distinct()

        # Get filter parameters
        category = request.GET.get('category')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search = request.GET.get('search', '').strip()

        # Base querysets
        bookings = Booking.objects.all()
        reviews = Review.objects.all()
        users = User.objects.all()

        # Apply filters
        if category and category != 'all':
            bookings = bookings.filter(service_provider__category__category=category)
            reviews = reviews.filter(service_provider__category__category=category)

        if start_date:
            bookings = bookings.filter(date__gte=start_date)
        if end_date:
            bookings = bookings.filter(date__lte=end_date)

        if search:
            provider_filter = Q(service_provider__first_name__icontains=search) | \
                            Q(service_provider__last_name__icontains=search) | \
                            Q(service_provider__email__icontains=search)
            bookings = bookings.filter(provider_filter)
            reviews = reviews.filter(provider_filter)

        # Calculate statistics
        extra_context.update({
            'statistics': {
                'total_users': users.filter(user_type='USER').count(),
                'total_providers': users.filter(user_type='SERVICE_PROVIDER').count(),
                'total_bookings': bookings.count(),
                'average_rating': round(reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 1)
            },
            'bookings_over_time': list(
                bookings.values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            ),
            'top_providers': [
                {
                    'name': f"{p['service_provider__first_name']} {p['service_provider__last_name']}",
                    'bookings': p['count']
                }
                for p in bookings.values(
                    'service_provider__first_name',
                    'service_provider__last_name'
                ).annotate(count=Count('id')).order_by('-count')[:10]
            ],
            'top_rated': [
                {
                    'name': f"{p['service_provider__first_name']} {p['service_provider__last_name']}",
                    'rating': round(p['avg_rating'], 1)
                }
                for p in reviews.values(
                    'service_provider__first_name',
                    'service_provider__last_name'
                ).annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:10]
            ]
        })

        return super().changelist_view(request, extra_context=extra_context)

        return False
