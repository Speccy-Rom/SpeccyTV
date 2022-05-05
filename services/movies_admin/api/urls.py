from api.v1.urls import router_v1
from django.urls import include, path

urlpatterns = [
    path('v1/', include(router_v1.urls))
]
