from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),  # Temporary redirect
    # We'll enable these as we build each app
    # path('dashboard/', include('core.urls')),
    # path('clients/', include('clients.urls')),
    # path('monitoring/', include('monitoring.urls')),
    # path('billing/', include('billing.urls')),
    # path('content/', include('content_manager.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
