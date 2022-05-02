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
