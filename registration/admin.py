from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg, Q
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

    list_display = (
        'email', 'first_name', 'last_name', 'user_type', 'contact',
        'location', 'get_rating', 'get_provider_bookings', 'get_user_bookings'
    )
    list_filter = ('user_type',)
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
        qs = super().get_queryset(request)
        return qs.annotate(
            rating_avg=Avg('reviews_received__rating'),
            provider_booking_count=Count('provider_bookings', distinct=True),
            user_booking_count=Count('bookings', distinct=True)
        )

    def get_rating(self, obj):
        return round(obj.rating_avg, 1) if obj.rating_avg else 0
    get_rating.short_description = 'Rating'

    def get_provider_bookings(self, obj):
        return obj.provider_booking_count
    get_provider_bookings.short_description = 'Provider Bookings'

    def get_user_bookings(self, obj):
        return obj.user_booking_count
    get_user_bookings.short_description = 'User Bookings'

    actions = [
        export_as_csv_action(
            description="Export selected users to CSV",
            fields=['email', 'username', 'first_name', 'last_name', 'user_type', 'contact', 'location']
        )
    ]


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ⏱ Filter parameters
        category = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        search = self.request.GET.get('search', '').strip()

        bookings = Booking.objects.select_related('service_provider', 'user')
        reviews = Review.objects.select_related('service_provider', 'reviewer')
        users = User.objects.all()
        services = Service.objects.all()

        if category and category != 'all':
            provider_ids = Service.objects.filter(category=category).values_list('provider_id', flat=True).distinct()
            bookings = bookings.filter(service_provider__id__in=provider_ids)
            reviews = reviews.filter(service_provider__id__in=provider_ids)


        if start_date:
            bookings = bookings.filter(date__gte=start_date)
        if end_date:
            bookings = bookings.filter(date__lte=end_date)

        if search:
            provider_filter = (
                Q(service_provider__first_name__icontains=search) |
                Q(service_provider__last_name__icontains=search) |
                Q(service_provider__email__icontains=search)
            )
            bookings = bookings.filter(provider_filter)
            reviews = reviews.filter(provider_filter)

        # 📊 Bookings chart data (date-wise)
        bookings_chart_data = [
            {"date": b["date"].strftime("%Y-%m-%d"), "count": b["count"]}
            for b in bookings.values("date").annotate(count=Count("id")).order_by("date")
        ]

        # 🏆 Top 5 providers by bookings
        top_providers = [
            {
                'name': f"{p['service_provider__first_name']} {p['service_provider__last_name']}",
                'email': p['service_provider__email'],
                'bookings': p['count']
            }
            for p in bookings.values(
                'service_provider__first_name',
                'service_provider__last_name',
                'service_provider__email'
            ).annotate(count=Count('id')).order_by('-count')[:5]
        ]

        # ⭐ Top 5 providers by rating
        top_rated = [
            {
                'name': f"{p['service_provider__first_name']} {p['service_provider__last_name']}",
                'email': p['service_provider__email'],
                'rating': round(p['avg_rating'], 1)
            }
            for p in reviews.values(
                'service_provider__first_name',
                'service_provider__last_name',
                'service_provider__email'
            ).annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:5]
        ]

        context.update({
            'categories': services.values_list('category', flat=True).distinct(),
            'statistics': {
                'total_users': users.filter(user_type='USER').count(),
                'total_providers': users.filter(user_type='SERVICE_PROVIDER').count(),
                'total_bookings': bookings.count(),
                'average_rating': round(reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 1)
            },
            'bookings_over_time': bookings_chart_data,
            'top_providers': top_providers,
            'top_rated': top_rated,
        })

        return context


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at']
