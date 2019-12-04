from django.db import models


class River(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=2083)
    level = models.FloatField(default=0)
    start_lat = models.FloatField(default=35.8)
    start_lng = models.FloatField(default=139.194)
    end_lat = models.FloatField(default=35.8)
    end_lng = models.FloatField(default=139.194)

