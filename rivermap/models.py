from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from polymorphic.models import PolymorphicModel

"""
Models:

Region
Prefecture
River
Observatory
Dam
MapObject
    Shop
    School
    RiverObject
        Section
        Spot
Comment
    CommentComment
    RiverComment
    ObservatoryComment
    MapObjectComment

"""


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


class MapObject(PolymorphicModel):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, default='')
    name_jp = models.CharField(max_length=255, default='')
    date_added = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    lat = models.FloatField(default=35.8)
    lng = models.FloatField(default=139.194)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class RiverObject(MapObject):
    river = models.ForeignKey(River, on_delete=models.PROTECT)
    observatory = models.ForeignKey(Observatory, on_delete=models.PROTECT, blank=True, null=True)
    dam = models.ForeignKey(Dam, on_delete=models.PROTECT, blank=True, null=True)
    high_water = models.FloatField(blank=True, null=True)
    middle_water = models.FloatField(blank=True, null=True)
    low_water = models.FloatField(blank=True, null=True)
    difficulty = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['name']


class Shop(MapObject):

    def get_absolute_url(self):
        return reverse('shop-detail', kwargs={'pk': self.pk, 'prefecture': self.prefecture.slug})


class School(MapObject):

    def get_absolute_url(self):
        return reverse('school-detail', kwargs={'pk': self.pk, 'prefecture': self.prefecture.slug})


class Section(RiverObject):
    end_lat = models.FloatField(default=35.8)
    end_lng = models.FloatField(default=139.194)

    def get_absolute_url(self):
        return reverse('section-detail', kwargs={'pk': self.pk, 'prefecture': self.prefecture.slug})


class Spot(RiverObject):

    def get_absolute_url(self):
        return reverse('spot-detail', kwargs={'pk': self.pk, 'prefecture': self.prefecture.slug})


class Comment(PolymorphicModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date_posted']


class RiverComment(Comment):
    parent = models.ForeignKey(River, on_delete=models.CASCADE)


class ObservatoryComment(Comment):
    parent = models.ForeignKey(Observatory, on_delete=models.CASCADE)


class MapObjectComment(Comment):
    parent = models.ForeignKey(MapObject, on_delete=models.CASCADE)


class CommentComment(models.Model):
    parent = models.ForeignKey(Comment, on_delete=models.CASCADE)

