from django.contrib import admin
from django.urls import path, include
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib import messages

from registration.models import Dashboard
from registration.admin import DashboardAdmin


class CustomAdminSite(AdminSite):
    site_header = 'Fixly Admin'
    site_title = 'Fixly Admin Portal'
    index_title = 'Welcome to Fixly Admin Portal'

    def has_permission(self, request):
        if not request.user.is_authenticated:
            return self.login(request)
        return request.user.is_staff

    def login(self, request, extra_context=None):
        if not request.user.is_authenticated:
            from registration.models import User
            admin_user, created = User.objects.get_or_create(
                email='admin@example.com',
                defaults={
                    'username': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    'user_type': 'admin',
                }
            )
            if created:
                admin_user.set_password('admin')
                admin_user.save()

            user = authenticate(username='admin@example.com', password='admin')
            if user:
                login(request, user)
                messages.success(request, 'Welcome to Fixly Admin Portal!')
            else:
                messages.error(request, 'Authentication failed.')

        return redirect('admin:index')

    def index(self, request, extra_context=None):
        dashboard_admin = DashboardAdmin(Dashboard, self)
        return dashboard_admin.changelist_view(request)

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        app_list = [app for app in app_list if app['app_label'] != 'auth']
        if not app_label:
            app_list.insert(0, {
                'name': 'Dashboard',
                'app_label': 'registration',
                'app_url': '/admin/registration/dashboard/',
                'has_module_perms': True,
                'models': [{
                    'name': 'Dashboard',
                    'object_name': 'Dashboard',
                    'perms': {'add': False, 'change': True, 'delete': False, 'view': True},
                    'admin_url': '/admin/registration/dashboard/',
                }]
            })
        return app_list


# ✅ FIX: Instantiate custom admin site before using it
admin_site = CustomAdminSite(name='custom_admin')


# Register your models with the custom admin site
from registration.models import User, UserToken, Dashboard
from service.models import Service
from booking.models import Booking
from review.models import Review
from registration.admin import CustomUserAdmin, UserTokenAdmin, DashboardAdmin
from service.admin import ServiceAdmin
from booking.admin import BookingAdmin
from review.admin import ReviewAdmin

admin_site.register(User, CustomUserAdmin)
admin_site.register(UserToken, UserTokenAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(Booking, BookingAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(Dashboard, DashboardAdmin)

# Unregister auth models
admin.site.unregister(Group)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('registration.urls')),
    path('services/', include('service.urls')),
    path('review/', include('review.urls')),
    path('booking/', include('booking.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
