from django.db import models
from django.urls import reverse


class River(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=2083)
    level = models.FloatField(default=0)
    date = models.CharField(max_length=255, default='')
    high_water = models.FloatField(default=0)
    middle_water = models.FloatField(default=0)
    low_water = models.FloatField(default=0)
    start_lat = models.FloatField(default=35.8)
    start_lng = models.FloatField(default=139.194)
    end_lat = models.FloatField(default=35.8)
    end_lng = models.FloatField(default=139.194)
    difficulty = models.CharField(max_length=255, default='')
    section = models.CharField(max_length=255, default='')

    def get_absolute_url(self):
        return reverse('river-detail', kwargs={'pk': self.pk})

