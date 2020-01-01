from django.db import models
from django.urls import reverse


class River(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=2083, blank=True)
    level = models.FloatField(blank=True)
    date = models.CharField(max_length=255, blank=True)
    high_water = models.FloatField(blank=True)
    middle_water = models.FloatField(blank=True)
    low_water = models.FloatField(blank=True)
    start_lat = models.FloatField(default=35.8)
    start_lng = models.FloatField(default=139.194)
    end_lat = models.FloatField(default=35.8)
    end_lng = models.FloatField(default=139.194)
    difficulty = models.CharField(max_length=255, blank=True)
    section = models.CharField(max_length=255, default='')

    def get_absolute_url(self):
        return reverse('river-detail', kwargs={'pk': self.pk})

