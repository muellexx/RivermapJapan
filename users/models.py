from django.db import models
from django.contrib.auth.models import User
from PIL import Image

from rivermap.models import Section, Spot


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    last_activity = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)
        img = crop_center(img, min(img.size), min(img.size))

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_posts(self):
        return self.user.post_set.all().order_by('-date_posted')

    def get_sections(self):
        return self.user.mapobject_set.instance_of(Section).order_by('-date_added')

    def get_spots(self):
        return self.user.mapobject_set.instance_of(Spot).order_by('-date_added')

    def get_comments(self):
        return self.user.comment_set.all().order_by('-date_posted')
