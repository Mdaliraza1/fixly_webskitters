from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db.models import Count, Avg
from django.urls import path
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import format_html
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import User, UserToken, Dashboard
from utils.admin_actions import export_as_csv_action
from service.models import Service
from booking.models import Booking
from review.models import Review

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'contact', 'gender', 'location', 'user_type', 'category')

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'contact', 'gender', 'location', 'user_type', 'category')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'get_rating', 'get_bookings', 'is_active')
    list_filter = ('user_type', 'category', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'contact', 'location')
    ordering = ('email',)
    actions = ['activate_users', 'deactivate_users', export_as_csv_action()]

    fieldsets = (
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'username', 'contact', 'gender', 'location')
        }),
        ('Service Provider Info', {
            'fields': ('category',),
            'classes': ('collapse',),
            'description': 'Only applicable for service providers'
        }),
        ('Account Settings', {
            'fields': ('password', 'user_type', 'is_active')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 
                      'contact', 'gender', 'location', 'user_type', 'category'),
        }),
    )

    def get_rating(self, obj):
        if obj.user_type == 'SERVICE_PROVIDER':
            avg_rating = Review.objects.filter(service_provider=obj).aggregate(Avg('rating'))['rating__avg']
            if avg_rating:
                stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
                return format_html('<span style="color: #FFD700;">{}</span> ({:.1f})', stars, avg_rating)
        return '-'
    get_rating.short_description = 'Rating'

    def get_bookings(self, obj):
        if obj.user_type == 'SERVICE_PROVIDER':
            count = Booking.objects.filter(service_provider=obj).count()
            return count
        elif obj.user_type == 'USER':
            count = Booking.objects.filter(user=obj).count()
            return count
        return 0
    get_bookings.short_description = 'Bookings'

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        messages.success(request, f'{queryset.count()} users were successfully activated.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        messages.success(request, f'{queryset.count()} users were successfully deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'

    def save_model(self, request, obj, form, change):
        try:
            if not change:  # If creating new user
                if not obj.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
                    obj.set_password(obj.password)
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.error(request, str(e))

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expired_at')
    list_filter = ('created_at', 'expired_at')
    search_fields = ('user__email', 'token')
    ordering = ('-created_at',)
    actions = [export_as_csv_action()]
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token', 'expired_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user', 'token', 'created_at')
        return ('created_at',)

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dashboard.html'

    def get_urls(self):
        urls = [
            path('', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
            path('data/', self.admin_site.admin_view(self.dashboard_data), name='dashboard-data'),
        ]
        return urls

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def dashboard_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Dashboard',
            'categories': Service.objects.values_list('category', flat=True).distinct(),
        }
        return render(request, 'admin/dashboard.html', context)

    def dashboard_data(self, request):
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
        total_users = users.filter(user_type='USER').count()
        total_providers = users.filter(user_type='SERVICE_PROVIDER').count()
        total_bookings = bookings.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Get bookings by date
        bookings_by_date = bookings.values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Get top providers by bookings
        top_providers = bookings.values(
            'service_provider__first_name',
            'service_provider__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Get top rated providers
        top_rated = reviews.values(
            'service_provider__first_name',
            'service_provider__last_name'
        ).annotate(
            avg_rating=Avg('rating')
        ).order_by('-avg_rating')[:10]

        # Format provider names
        def format_name(provider):
            return f"{provider['service_provider__first_name']} {provider['service_provider__last_name']}"

        return JsonResponse({
            'statistics': {
                'total_users': total_users,
                'total_providers': total_providers,
                'total_bookings': total_bookings,
                'average_rating': round(avg_rating, 1)
            },
            'bookings_over_time': list(bookings_by_date),
            'top_providers': [
                {'name': format_name(p), 'bookings': p['count']}
                for p in top_providers
            ],
            'top_rated': [
                {'name': format_name(p), 'rating': round(p['avg_rating'], 1)}
                for p in top_rated
            ]
        })
