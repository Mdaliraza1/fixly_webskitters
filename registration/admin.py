from django.contrib import admin
from django.db.models import Count, Avg
from django.urls import path
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import format_html
from .models import User, UserToken
from utils.admin_actions import export_as_csv_action
from service.models import Service
from booking.models import Booking
from review.models import Review

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'get_rating', 'get_bookings')
    list_filter = ('user_type', 'gender', 'category')
    search_fields = ('email', 'first_name', 'last_name', 'contact', 'location')
    ordering = ('email',)
    actions = [export_as_csv_action()]

    fieldsets = (
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'contact', 'gender', 'location')}),
        ('Service Provider Info', {'fields': ('category',), 'classes': ('collapse',)}),
        ('Type', {'fields': ('user_type',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'user_type'),
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

class DashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/dashboard.html"  # This connects to your custom template

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
        from django.db.models import Q
        from booking.models import Booking
        from review.models import Review
        from registration.models import User

        category = request.GET.get('category')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        search = request.GET.get('search', '').strip()

        filters = {}
        review_filters = {}
        user_filters = Q()
        
        if category and category != 'all':
            filters['service_provider__category__category'] = category
            review_filters['service_provider__category__category'] = category

        if start_date:
            filters['date__gte'] = start_date
        if end_date:
            filters['date__lte'] = end_date

        if search:
            user_filters |= Q(first_name__icontains=search)
            user_filters |= Q(last_name__icontains=search)
            user_filters |= Q(contact__icontains=search)

        user_ids = User.objects.filter(user_filters).values_list('id', flat=True)
        filters['service_provider__id__in'] = user_ids

        bookings = Booking.objects.filter(**filters)
        reviews = Review.objects.filter(**review_filters)

        bookings_by_provider = bookings.values(
            'service_provider__first_name', 'service_provider__last_name'
        ).annotate(count=Count('id')).order_by('-count')[:10]

        ratings_by_provider = reviews.values(
            'service_provider__first_name', 'service_provider__last_name'
        ).annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:10]

        bookings_over_time = bookings.values('date').annotate(count=Count('id')).order_by('date')

        user_type_counts = User.objects.values('user_type').annotate(count=Count('id'))

        def full_name(obj):
            return f"{obj['service_provider__first_name']} {obj['service_provider__last_name']}"

        return JsonResponse({
            'bookings_by_provider': [{'name': full_name(b), 'count': b['count']} for b in bookings_by_provider],
            'ratings_by_provider': [{'name': full_name(r), 'avg_rating': r['avg_rating']} for r in ratings_by_provider],
            'bookings_over_time': list(bookings_over_time),
            'user_type_counts': list(user_type_counts),
        })
