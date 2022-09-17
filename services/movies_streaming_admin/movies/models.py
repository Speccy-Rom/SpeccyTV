import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class File(TimeStampedModel):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    file_path = models.FileField(_('File'), upload_to='files/')
    resolution = models.CharField(_('Resolution'), max_length=100)
    codec_name = models.CharField(_('Codec'), max_length=100, null=True, blank=True)
    display_aspect_ratio = models.CharField(_('Display Aspect Ratio'), max_length=100, null=True, blank=True)
    fps = models.IntegerField(_('FPS'), null=True, blank=True)

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        managed = False
        db_table = f'"content"."file"'
        ordering = ["file_path"]

    def __str__(self):
        return f'{self.file_path}'


class FilmWork(TimeStampedModel):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('Name'), max_length=255)
    certificate = models.TextField(_('Certificate'), blank=True)
    file_path = models.FileField(_('Original file'), upload_to='film_works/')
    files = models.ManyToManyField('movies.File', through='movies.FileFilmWork', related_name='filmworks')

    class Meta:
        verbose_name = _('Film')
        verbose_name_plural = _('Films')
        managed = False
        db_table = f'"content"."film_work"'
        ordering = ["title"]

    def __str__(self):
        return self.title


class FileFilmWork(models.Model):
    id = models.UUIDField(_('id'), primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('movies.FilmWork', on_delete=models.CASCADE)
    file = models.ForeignKey('movies.File', on_delete=models.CASCADE)
    created = models.DateTimeField(_('Created'), auto_created=True, auto_now_add=True)

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        db_table = '"content"."file_film_work"'
        managed = False
        unique_together = ('film_work', 'file')
