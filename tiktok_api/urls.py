from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version='v1',
        description="Your API Description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/user/', include('user.urls')),
    path('api/v1/post/', include('post.urls')),
    path('api/v1/comment/', include('comment.urls')),
    path('api/v1/like/', include('like.urls')),
    path('api/v1/follow/', include('follow.urls')),
    path('api/v1/report/', include('report.urls')),
    path('api/v1/share/', include('share.urls')),
    # path('api/v1/tag/', include('tag.urls')),
    
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
