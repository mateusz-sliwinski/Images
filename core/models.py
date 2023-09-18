from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
# Create your models here.


class Tier(models.Model):
    name = models.CharField(max_length=255)
    thumbnail_400px = models.BooleanField(default=False)
    original_photo = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)


class User(AbstractUser):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='Tier')


class Images(models.Model):
    image = models.ImageField(upload_to='media/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE,related_name='Images')
    expired_time = models.IntegerField(default=0, validators=[
        MaxValueValidator(30000),
        MinValueValidator(300)
    ])

    def save(self, *args, **kwargs):
        img = Image.open(self.image.path)
        if not img.format == 'JPG' or img.format == 'PNG':
            raise ValidationError("Use jpg or png format.")
        super().save(*args, **kwargs)
