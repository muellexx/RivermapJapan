from PIL import Image
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Case, When, Value, IntegerField
from django.urls import reverse
from django.utils import timezone
from polymorphic.models import PolymorphicModel
from django.utils.translation import get_language

from blog.models import save_image

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
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"


class Prefecture(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    name_jp = models.CharField(max_length=255, unique=True)
    slug = models.SlugField()
    lat = models.FloatField(default=35.80251)
    lng = models.FloatField(default=139.19437)
    zoom = models.IntegerField(default=8)

    def __str__(self):
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"

    def get_sections(self):
        return self.mapobject_set.instance_of(Section)

    def get_spots(self):
        return self.mapobject_set.instance_of(Spot)

    def get_absolute_url(self):
        return reverse('prefecture-detail', kwargs={'slug': self.slug})

    def section_count(self):
        return self.mapobject_set.instance_of(Section).count()

    def spot_count(self):
        return self.mapobject_set.instance_of(Spot).count()


class RiverSystem(models.Model):
    region = models.ManyToManyField(Region)
    prefecture = models.ManyToManyField(Prefecture)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255, unique=True)

    def __str__(self):
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"

    def get_absolute_url(self):
        return reverse('river-detail', kwargs={'pk': self.pk})


class River(models.Model):
    region = models.ManyToManyField(Region)
    prefecture = models.ManyToManyField(Prefecture)
    riversystem = models.ManyToManyField(RiverSystem)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255, unique=True)

    def __str__(self):
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"

    def get_absolute_url(self):
        return reverse('river-detail', kwargs={'pk': self.pk})

    def system_observatories_set(self):
        result = self.observatory_set.all().annotate(custom_order=Case(When(river=self, then=Value(1)), default=2,
                                    output_field=IntegerField(), )).order_by('custom_order', 'name')
        for riversystem in self.riversystem.all():
            result = result | riversystem.observatory_set.all()
        return result

    def system_dams_set(self):
        result = self.dam_set.all().annotate(custom_order=Case(When(river=self, then=Value(1)), default=2,
                                    output_field=IntegerField(), )).order_by('custom_order', 'name')
        for riversystem in self.riversystem.all():
            result = result | riversystem.dam_set.all()
        return result


class Observatory(models.Model):
    river = models.ForeignKey(River, on_delete=models.PROTECT)
    riversystem = models.ForeignKey(RiverSystem, on_delete=models.PROTECT, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255)
    url = models.CharField(max_length=2083, unique=True)
    level = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(max_length=255, null=True, blank=True)

    def __str__(self):
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"


class Dam(models.Model):
    river = models.ForeignKey(River, on_delete=models.PROTECT)
    riversystem = models.ForeignKey(RiverSystem, on_delete=models.PROTECT, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    name_jp = models.CharField(max_length=255)
    url = models.CharField(max_length=2083, unique=True)
    level = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(max_length=255, null=True, blank=True)

    def __str__(self):
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"


class MapObject(PolymorphicModel):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, default='')
    name_jp = models.CharField(max_length=255, default='')
    content = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    lat = models.FloatField(
        validators=[MinValueValidator(21), MaxValueValidator(47)],
    )
    lng = models.FloatField(
        validators=[MinValueValidator(119), MaxValueValidator(151)],
    )

    def __str__(self):
        if get_language() == "ja":
            return self.name_jp
        else:
            return self.name + " (" + self.name_jp + ")"

    class Meta:
        ordering = ['name']

    def description(self):
        return self.__class__.__name__


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
    end_lat = models.FloatField(
        validators=[MinValueValidator(21), MaxValueValidator(47)],
    )
    end_lng = models.FloatField(
        validators=[MinValueValidator(119), MaxValueValidator(151)],
    )

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
    image1 = models.ImageField(upload_to='comment_pics', null=True, blank=True)
    image2 = models.ImageField(upload_to='comment_pics', null=True, blank=True)
    image3 = models.ImageField(upload_to='comment_pics', null=True, blank=True)
    image4 = models.ImageField(upload_to='comment_pics', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date_posted']

    def num_pics(self):
        num_pics = 0
        if self.image1:
            num_pics += 1
        if self.image2:
            num_pics += 1
        if self.image3:
            num_pics += 1
        if self.image4:
            num_pics += 1
        return num_pics

    def save(self, *args, **kwargs):
        super(Comment, self).save(*args, **kwargs)
        print('hi')
        if self.image1:
            save_image(Image.open(self.image1.path), self.image1.path)
        if self.image2:
            save_image(Image.open(self.image2.path), self.image2.path)
        if self.image3:
            save_image(Image.open(self.image3.path), self.image3.path)
        if self.image4:
            save_image(Image.open(self.image4.path), self.image4.path)


class RiverComment(Comment):
    parent = models.ForeignKey(River, on_delete=models.CASCADE)


class ObservatoryComment(Comment):
    parent = models.ForeignKey(Observatory, on_delete=models.CASCADE)


class MapObjectComment(Comment):
    parent = models.ForeignKey(MapObject, on_delete=models.CASCADE)


class CommentComment(models.Model):
    parent = models.ForeignKey(Comment, on_delete=models.CASCADE)

