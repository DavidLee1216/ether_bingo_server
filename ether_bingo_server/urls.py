"""ether_bingo_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger Bingo Document",
        default_version="v1",
        description="Swagger Document for bingo apis",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),  # admin page
    re_path(r'^api/user/', include('user.urls')),  # user app
    re_path(r'^api/game/', include('game.urls')),  # game app
    path('api/token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),  # access token
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),  # refresh token
    path('api/token/verify/', jwt_views.TokenVerifyView.as_view(),
         name='token_verify'),  # token verify
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$',
                schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r'^swagger/$', schema_view.with_ui('swagger',
                cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^docs/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), ]
