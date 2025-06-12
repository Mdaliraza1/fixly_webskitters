from django.contrib import admin
from django.urls import path, include
from django.contrib.admin import AdminSite
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from django.contrib import messages
from registration.forms import CustomAdminAuthenticationForm
from registration.admin import DashboardView

class CustomAdminSite(AdminSite):
    site_header = 'Fixly Admin'
    site_title = 'Fixly Admin Portal'
    index_title = 'Welcome to Fixly Admin Portal'
    login_form = CustomAdminAuthenticationForm
    login_template = 'admin/login.html'

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        at least one page in the admin site.
        """
        return request.user.is_active and request.user.is_staff

    def login(self, request, extra_context=None):
        """
        Handle the login form submission.
        """
        if request.method == 'POST':
            form = self.login_form(request, data=request.POST)
            if form.is_valid():
                login(request, form.get_user())
                return redirect('admin:index')
        else:
            form = self.login_form(request)

        context = {
            **self.each_context(request),
            'title': 'Log in',
            'app_path': request.get_full_path(),
            'username': request.user.get_username() if request.user.is_authenticated else '',
            'form': form,
            'next': request.GET.get('next', ''),
            **(extra_context or {}),
        }

        if request.path.startswith('/admin/'):
            return render(request, self.login_template, context)
        return redirect('index')

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request, app_label)
        
        # Remove the Authentication and Authorization app
        app_list = [app for app in app_list if app['app_label'] != 'auth']
        
        # Add Dashboard as the first item if user has permission
        if not app_label and request.user.has_module_perms('registration'):
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('registration/dashboard/', DashboardView.as_view(), name='registration_dashboard'),
        ]
        return custom_urls + urls

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
    path('admin/', admin_site.urls),
    path('', include('registration.urls')),
    path('services/', include('service.urls')),
    path('review/', include('review.urls')),
    path('booking/', include('booking.urls'))
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
