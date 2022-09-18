from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser

from movies.models import File, FilmWork
from movies.serializers import FileSerializer, FilmWorkSerializer


class FileViewSet(viewsets.ModelViewSet):
    parser_classes = [FormParser, MultiPartParser]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = []
    http_method_names = ['get', 'post', 'put', 'delete']


class FilmWorkViewSet(viewsets.ModelViewSet):
    queryset = FilmWork.objects.all()
    serializer_class = FilmWorkSerializer
    permission_classes = []
    http_method_names = ['get', 'post']
