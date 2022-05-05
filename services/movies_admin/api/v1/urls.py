from movies.api.v1.views import FilmWorkViewSet, GenreViewSet, PersonViewSet
from rest_framework import routers

router_v1 = routers.DefaultRouter()
router_v1.register('persons', PersonViewSet, basename='persons')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('movies', FilmWorkViewSet, basename='movies')