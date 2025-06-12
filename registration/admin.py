from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg, Q
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .models import User, UserToken
from .forms import CustomUserChangeForm, CustomUserCreationForm
from utils.admin_actions import export_as_csv_action

from service.models import Service
from booking.models import Booking
from review.models import Review


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'user_type', 'contact', 'location', 'get_rating', 'get_bookings')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'contact', 'location')
    ordering = ('email',)
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name', 'contact', 'location', 'gender')}),
        ('Service Provider Info', {'fields': ('user_type', 'category')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'username', 'first_name', 'last_name', 'user_type', 'category'),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            rating_avg=Avg('reviews_received__rating'),
            booking_count=Count('bookings')  # ✅ Fixed: use correct related name
        )
        return queryset

    def get_rating(self, obj):
        return round(obj.rating_avg, 1) if hasattr(obj, 'rating_avg') and obj.rating_avg else 0
    get_rating.short_description = 'Rating'

    def get_bookings(self, obj):
        return obj.booking_count if hasattr(obj, 'booking_count') else 0
    get_bookings.short_description = 'Bookings'

    actions = [
        export_as_csv_action(
            description="Export selected users to CSV",
            fields=['email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location']
        )
    ]


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at']


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        search = self.request.GET.get('search', '').strip()

        bookings = Booking.objects.all()
        reviews = Review.objects.all()
        users = User.objects.all()
        services = Service.objects.all()

        if category and category != 'all':
            bookings = bookings.filter(service_provider__category__category=category)
            reviews = reviews.filter(service_provider__category__category=category)

        if start_date:
            bookings = bookings.filter(date__gte=start_date)
        if end_date:
            bookings = bookings.filter(date__lte=end_date)

        if search:
            provider_filter = Q(service_provider__first_name__icontains=search) | Q(service_provider__last_name__icontains=search) | Q(service_provider__email__icontains=search)
            bookings = bookings.filter(provider_filter)
            reviews = reviews.filter(provider_filter)

        context.update({
            'categories': services.values_list('category', flat=True).distinct(),
            'statistics': {
                'total_users': users.filter(user_type='USER').count(),
                'total_providers': users.filter(user_type='SERVICE_PROVIDER').count(),
                'total_bookings': bookings.count(),
                'average_rating': round(reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 1)
            },
            'bookings_over_time': list(
                bookings.values('date').annotate(count=Count('id')).order_by('date')
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

        return context
