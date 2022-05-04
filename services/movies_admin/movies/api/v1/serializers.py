from movies.models import FilmWork, Genre, Person
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer


class PersonSerializer(ModelSerializer):

    class Meta:
        model = Person
        exclude = ('created', 'modified')


class GenreSerializer(ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('created', 'modified')


class FilmWorkSerializer(ModelSerializer):
    genres = SlugRelatedField(slug_field='name', read_only=True, many=True)
    writers, actors, directors = ReadOnlyField(), ReadOnlyField(), ReadOnlyField()

    class Meta:
        model = FilmWork
        exclude = ('persons', 'created', 'modified', 'file_path', 'certificate')
