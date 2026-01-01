"""
URL configuration for volleyball_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from team.views import CustomLoginView, signup, logout_get
from django.http import JsonResponse


def healthz(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout-get/', logout_get, name='logout_get'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('healthz/', healthz),
    path('signup/', signup, name='signup'),
    path('api/', include('team.api_urls')),
    path('', include('team.urls')),
]

# Serve media files in development and production
if settings.DEBUG or not settings.DEBUG:  # Always serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
