import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator as Max
from django.core.validators import MinValueValidator as Min
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Person(TimeStampedModel):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.TextField(_('Full name'))
    birth_date = models.DateField(_('Birthday'), null=True)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        managed = False
        db_table = f'"content"."person"'

    def __str__(self):
        return self.full_name


class Genre(TimeStampedModel):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_('Name'))
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        managed = False
        db_table = f'"content"."genre"'

    def __str__(self):
        return self.name


class File(TimeStampedModel):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    file_path = models.FileField(_('File'), upload_to='files/')
    file_format = models.CharField(_('File format'), max_length=100)
    video_codec = models.CharField(_('Video codec'), max_length=100)
    video_width = models.IntegerField(_('Width'))
    video_height = models.IntegerField(_('Height'))
    video_fps = models.IntegerField(_('Video FPS'))
    audio_codec = models.CharField(_('Audio codec'), max_length=100)
    audio_sample_rate = models.IntegerField(_('Audio sample rate'))
    audio_channels = models.IntegerField(_('Audio channels'))

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        managed = False
        db_table = f'"content"."file"'

    def __str__(self):
        return f'{self.file_path}'


class FilmWorkType(models.TextChoices):
    MOVIE = ('film', _('Film'))
    SERIES = ('series', _('Series'))


class FilmWork(TimeStampedModel):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    creation_date = models.DateField(_('Creation date'), null=True, blank=True)
    certificate = models.TextField(_('Certificate'), blank=True)
    file_path = models.FileField(_('Original file'), upload_to='film_works/')
    rating = models.FloatField(_('Rating'), validators=[Min(0), Max(10)], null=True, blank=True)
    type = models.TextField(_('Type'), choices=FilmWorkType.choices, blank=True)
    genres = models.ManyToManyField('movies.Genre', through='movies.GenreFilmWork')
    persons = models.ManyToManyField('movies.Person', through='movies.PersonFilmWork')
    files = models.ManyToManyField('movies.File', through='movies.FileFilmWork')

    class Meta:
        verbose_name = _('Film')
        verbose_name_plural = _('Films')
        managed = False
        db_table = f'"content"."film_work"'

    def __str__(self):
        return self.title


class RoleType(models.TextChoices):
    ACTOR = ('actor', _('Actor'))
    WRITER = ('writer', _('Writer'))
    DIRECTOR = ('director', _('Director'))




class PersonFilmWork(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('movies.FilmWork', on_delete=models.CASCADE)
    person = models.ForeignKey('movies.Person', on_delete=models.CASCADE)
    role = models.TextField(_('Role'), choices=RoleType.choices)
    created = models.DateTimeField(_('Created'), auto_created=True, auto_now_add=True)



    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')
        db_table = '"content"."person_film_work"'
        managed = False
        unique_together = ('film_work', 'person', 'role')






class GenreFilmWork(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('movies.FilmWork', on_delete=models.CASCADE)
    genre = models.ForeignKey('movies.Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(_('Created'), auto_created=True, auto_now_add=True)



    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        db_table = '"content"."genre_film_work"'
        managed = False
        unique_together = ('film_work', 'genre')
