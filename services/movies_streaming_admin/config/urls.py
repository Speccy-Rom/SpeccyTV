from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from movies.views import FileViewSet, FilmWorkViewSet

schema_view = get_schema_view(
    openapi.Info(title="Streaming admin API", default_version="v1", description=""),
    public=True,
    permission_classes=[]
)


router = routers.DefaultRouter()
router.register("files", FileViewSet)
router.register("filmworks", FilmWorkViewSet)

urlpatterns = [
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('streaming_admin/', admin.site.urls),
    path('', include(router.urls))
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

