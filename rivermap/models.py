from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    name_jp = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Prefecture(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    name_jp = models.CharField(max_length=255, unique=True)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('prefecture-detail', kwargs={'slug': self.slug})


class River(models.Model):
    region = models.ManyToManyField(Region)
    prefecture = models.ManyToManyField(Prefecture)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('river-detail', kwargs={'pk': self.pk})


class Observatory(models.Model):
    river = models.ManyToManyField(River)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255)
    url = models.CharField(max_length=2083, unique=True)
    level = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Dam(models.Model):
    river = models.ManyToManyField(River)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255)
    url = models.CharField(max_length=2083, unique=True)
    level = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    river = models.ForeignKey(River, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    observatory = models.ForeignKey(Observatory, on_delete=models.PROTECT, blank=True, null=True)
    dam = models.ForeignKey(Dam, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=255, default='')
    name_jp = models.CharField(max_length=255, default='')
    high_water = models.FloatField(blank=True, null=True)
    middle_water = models.FloatField(blank=True, null=True)
    low_water = models.FloatField(blank=True, null=True)
    start_lat = models.FloatField(default=35.8)
    start_lng = models.FloatField(default=139.194)
    end_lat = models.FloatField(default=35.8)
    end_lng = models.FloatField(default=139.194)
    difficulty = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('section-detail', kwargs={'pk': self.pk, 'prefecture': self.prefecture.slug})


class Spot(models.Model):
    river = models.ForeignKey(River, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    observatory = models.ForeignKey(Observatory, on_delete=models.PROTECT, blank=True, null=True)
    dam = models.ForeignKey(Dam, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=255, default='')
    name_jp = models.CharField(max_length=255, default='')
    high_water = models.FloatField(blank=True, null=True)
    middle_water = models.FloatField(blank=True, null=True)
    low_water = models.FloatField(blank=True, null=True)
    lat = models.FloatField(default=35.8)
    lng = models.FloatField(default=139.194)
    difficulty = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class RiverComment(models.Model):
    river = models.ForeignKey(River, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class ObservatoryComment(models.Model):
    observatory = models.ForeignKey(Observatory, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class SectionComment(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
