from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Avg
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import path
from django.template.response import TemplateResponse

from .models import User
from .forms import CustomUserChangeForm, CustomUserCreationForm
from utils.admin_actions import export_as_csv_action
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


# ✅ Add dashboard to admin using custom view on AdminSite
class CustomAdminSite(admin.AdminSite):
    site_header = "Fixly Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('registration/dashboard/', self.admin_view(self.dashboard_view), name="dashboard"),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        category_filter = request.GET.get("category")
        search_query = request.GET.get("search")

        bookings = Booking.objects.all()
        reviews = Review.objects.all()
        users = User.objects.all()

        if start_date:
            bookings = bookings.filter(date__gte=start_date)
            reviews = reviews.filter(created_at__date__gte=start_date)
        if end_date:
            bookings = bookings.filter(date__lte=end_date)
            reviews = reviews.filter(created_at__date__lte=end_date)

        if category_filter and category_filter != "all":
            bookings = bookings.filter(service__category=category_filter)
            reviews = reviews.filter(service_provider__services__category=category_filter)

        if search_query:
            bookings = bookings.filter(
                service_provider__first_name__icontains=search_query
            ) | bookings.filter(
                service_provider__email__icontains=search_query
            )
            reviews = reviews.filter(
                service_provider__first_name__icontains=search_query
            ) | reviews.filter(
                service_provider__email__icontains=search_query
            )

        grouped = bookings.values("date").annotate(count=Count("id")).order_by("date")
        labels = [b["date"].strftime("%Y-%m-%d") for b in grouped]
        data = [b["count"] for b in grouped]

        statistics = {
            "total_users": users.filter(user_type="CUSTOMER").count(),
            "total_providers": users.filter(user_type="SERVICE_PROVIDER").count(),
            "total_bookings": bookings.count(),
            "average_rating": round(reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 2)
        }

        top_providers = bookings.values(
            "service_provider__first_name", "service_provider__last_name"
        ).annotate(bookings=Count("id")).order_by("-bookings")[:5]

        top_providers = [
            {"name": f"{p['service_provider__first_name']} {p['service_provider__last_name']}", "bookings": p["bookings"]}
            for p in top_providers
        ]

        top_rated = reviews.values(
            "service_provider__first_name", "service_provider__last_name"
        ).annotate(rating=Avg("rating")).order_by("-rating")[:5]

        top_rated = [
            {"name": f"{p['service_provider__first_name']} {p['service_provider__last_name']}", "rating": round(p["rating"], 2)}
            for p in top_rated
        ]

        categories = Booking.objects.values_list('service__category', flat=True).distinct()

        context = dict(
            self.each_context(request),
            statistics=statistics,
            top_providers=top_providers,
            top_rated=top_rated,
            categories=categories,
            bookings_over_time=grouped,
        )
        return TemplateResponse(request, "admin/dashboard.html", context)


# Instantiate and replace the default admin site
custom_admin_site = CustomAdminSite()
custom_admin_site.register(User, CustomUserAdmin)
