from rest_framework import serializers

from movies.models import File, FilmWork


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


class FilmWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmWork
        fields = "__all__"
