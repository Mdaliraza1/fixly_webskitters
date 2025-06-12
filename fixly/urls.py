from django.contrib import admin
from django.urls import path, include
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

class CustomAdminSite(AdminSite):
    def has_permission(self, request):
        return True  # Allow all access
    
    def login(self, request, extra_context=None):
        # Skip login and set session
        if not request.user.is_authenticated:
            # Create or get a default user for admin access
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'is_staff': True,
                    'is_superuser': True,
                    'email': 'admin@example.com'
                }
            )
            if created:
                user.set_password('admin')
                user.save()
            
            # Authenticate and login the user
            user = authenticate(username='admin', password='admin')
            if user:
                login(request, user)
        
        return self.index(request, extra_context)

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request, app_label)
        
        # Remove the Authentication and Authorization app
        app_list = [app for app in app_list if app['app_label'] != 'auth']
        
        return app_list

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

# Register models
admin_site.register(User, CustomUserAdmin)
admin_site.register(UserToken, UserTokenAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(Review, ReviewAdmin)

# Explicitly unregister auth models
admin.site.unregister(Group)

urlpatterns = [
    path('admin/', admin_site.urls),  # Use custom admin site instead of default
    path('', include('registration.urls')),
    path('services/',include('service.urls')),
    path('review/',include('review.urls')),
    path('booking/',include('booking.urls'))
]
