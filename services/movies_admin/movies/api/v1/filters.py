from django_filters import CharFilter, DateTimeFromToRangeFilter, FilterSet
from movies.models import FilmWork, Genre, Person


class PersonFilter(FilterSet):
    full_name = CharFilter(field_name='full_name', lookup_expr='icontains')
    birth_date = DateTimeFromToRangeFilter(field_name='birth_date')

    class Meta:
        model = Person
        fields = ('id',)


class GenreFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    description = CharFilter(field_name='description', lookup_expr='icontains')

    class Meta:
        model = Genre
        fields = ('id',)


class FilmWorkFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    description = CharFilter(field_name='description', lookup_expr='icontains')
    creation_date = DateTimeFromToRangeFilter(field_name='creation_date')

    class Meta:
        model = FilmWork
        fields = ('type', 'rating', 'certificate')
