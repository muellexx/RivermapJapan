import os

from PIL import Image
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


def save_image(img, path):
    if img.height > 800 or img.width > 800:
        output_size = (800, 800)
        img.thumbnail(output_size)
        img.save(path)


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to='blog_pics', null=True, blank=True)
    image2 = models.ImageField(upload_to='blog_pics', null=True, blank=True)
    image3 = models.ImageField(upload_to='blog_pics', null=True, blank=True)
    image4 = models.ImageField(upload_to='blog_pics', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

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
        if Post.objects.filter(id=self.id):
            post = Post.objects.get(id=self.id)
            for [before, after] in [[post.image1, self.image1], [post.image2, self.image2], [post.image3, self.image3], [post.image4, self.image4]]:
                if before:
                    if not after or not before.url == after.url:
                        if os.path.isfile(before.path):
                            os.remove(before.path)
                            print(before.path)

        if not self.image3:
            self.image3 = self.image4
            self.image4 = None
        if not self.image2:
            self.image2 = self.image3
            self.image3 = self.image4
            self.image4 = None
        if not self.image1:
            self.image1 = self.image2
            self.image2 = self.image3
            self.image3 = self.image4
            self.image4 = None

        super(Post, self).save(*args, **kwargs)
        if self.image1:
            save_image(Image.open(self.image1.path), self.image1.path)
        if self.image2:
            save_image(Image.open(self.image2.path), self.image2.path)
        if self.image3:
            save_image(Image.open(self.image3.path), self.image3.path)
        if self.image4:
            save_image(Image.open(self.image4.path), self.image4.path)

    def delete(self):
        self.image1.delete()
        self.image1.delete()
        self.image1.delete()
        self.image1.delete()
        super(Post, self).delete()
