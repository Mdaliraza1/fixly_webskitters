from django.contrib import admin
from django.urls import path, include
from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    def has_permission(self, request):
        return True  # Allow all access

admin_site = CustomAdminSite(name='custom_admin')

# Register your models with the custom admin site
from registration.models import User, UserToken
from service.models import Service
from booking.models import Booking
from review.models import Review
from registration.admin import CustomUserAdmin, UserTokenAdmin
from service.admin import ServiceAdmin
from booking.admin import BookingAdmin
from review.admin import ReviewAdmin

admin_site.register(User, CustomUserAdmin)
admin_site.register(UserToken, UserTokenAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(Review, ReviewAdmin)

urlpatterns = [
    path('admin/', admin_site.urls),  # Use custom admin site instead of default
    path('', include('registration.urls')),
    path('services/',include('service.urls')),
    path('review/',include('review.urls')),
    path('booking/',include('booking.urls'))
]
