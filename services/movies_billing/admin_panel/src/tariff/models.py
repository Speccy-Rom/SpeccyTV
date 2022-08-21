from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tariff(models.Model):
    class Meta:
        db_table = "tariff"

    id = models.AutoField(primary_key=True)
    name = models.CharField(_('Имя тарифа'), max_length=100)
    description = models.CharField(_('Описание'), max_length=255)
    price = models.IntegerField(_('Цена (копейки)'), validators=[MinValueValidator(0)])
    duration = models.IntegerField(_('Длительность'), validators=[MinValueValidator(1)])
    active = models.BooleanField(_('Активный ли'), default=True)

    def __str__(self):
        return f'{self.name}'
