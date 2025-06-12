from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import timedelta
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = 'django-insecure-^ri)g2#*bkb14-+-v1h&u&oyw#7%1=z#4oxj0a4c-5p*y-82+d'
DEBUG = False
ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    'jazzmin', # Admin Theme
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # My Apps
    'registration.apps.RegistrationConfig',
    'service.apps.ServiceConfig',
    'review.apps.ReviewConfig',
    'booking.apps.BookingConfig',

    # Installed Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'whitenoise.runserver_nostatic',  
    
   
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS Middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'fixly.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'template')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fixly.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Authentication Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# User model configuration
AUTH_USER_MODEL = 'registration.User'

# CORS and CSRF Settings (Updated)
CORS_ALLOWED_ORIGINS = [
    "https://fixlywebskitters-production-ebff.up.railway.app",
    "http://localhost:3000",
    "http://localhost:8000",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://fixlywebskitters-production-ebff.up.railway.app",
    "http://localhost:3000",
    "http://localhost:8000",
]

APPEND_SLASH = False

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

JAZZMIN_SETTINGS = {
    "site_title": "Fixly Admin Portal",
    "site_header": "Fixly Admin Dashboard",
    "site_brand": "Fixly",
    "welcome_sign": "Welcome to Fixly Admin Panel",
    "copyright": "Fixly",
    "search_model": ["registration.User", "booking.Booking", "review.Review"],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    "order_with_respect_to": [
        "registration",
        "booking",
        "review",
        "service",
    ],

    "icons": {
        "registration.User": "fas fa-user",
        "registration.UserToken": "fas fa-key",
        "booking.Booking": "fas fa-calendar-check",
        "review.Review": "fas fa-star",
        "service.Service": "fas fa-tools",
    },

    "custom_links": {
        "service": [{
            "name": "Dashboard Analytics",
            "url": "admin:dashboard-data",
            "icon": "fas fa-chart-line",
            "permissions": ["service.view_service"],
        }],
    },

    "topmenu_links": [
        {"name": "Home", "url": "/", "permissions": ["auth.view_user"]},
        {"model": "registration.user"},
        {"app": "booking"},
    ],

    "usermenu_links": [
        {"name": "Support", "url": "https://fixlysupport.example.com", "new_window": True},
    ],

    "changeform_format": "horizontal_tabs",  # or "collapsible", "vertical_tabs"
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_flat_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_child_indent": True,
}
"custom_links": {
    "service": [
        {
            "name": "Dashboard Analytics",
            "url": "admin:dashboard-data",
            "icon": "fas fa-chart-line",
            "permissions": ["service.view_service"],
        }
    ],
},

