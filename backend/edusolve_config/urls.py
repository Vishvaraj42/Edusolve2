from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI setup
schema_view = get_schema_view(
    openapi.Info(
        title="EduSolve API",
        default_version='v1',
        description="API documentation for EduSolve - Educational platform for 9th & 10th grade students",
        terms_of_service="https://www.edusolve.com/terms/",
        contact=openapi.Contact(email="support@edusolve.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/doubts/', include('doubts.urls')),
    path('api/practice/', include('practice.urls')),
    path('api/community/', include('community.urls')),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)