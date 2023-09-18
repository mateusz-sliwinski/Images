# Standard Library
import uuid

# Django
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

# 3rd-party
from PIL import Image


class UUIDMixin(models.Model):
    """
    A mixin providing a UUID-based primary key for Django models.

    Attributes:
        id (UUID): The UUID-based primary key of the model.

    Meta:
        abstract (bool): Specifies that this is an abstract model and should not be created as a database table.

    Fields:
        id (UUIDField): A UUIDField representing the primary key of the model.

    Usage:
        To use this mixin, inherit from it in your Django model class.

        Example:
            class YourModel(UUIDMixin):
                name = models.CharField(max_length=100)

            This will add a UUID-based primary key to YourModel.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        verbose_name='ID',
    )

    class Meta:
        abstract = True


class Tier(UUIDMixin, models.Model):
    """
    Model representing a tier with a UUID-based primary key.

    Attributes:
        id (UUID): The UUID-based primary key of the tier.
        name (str): The name of the tier.
        thumbnail_400px (bool): Indicates if the tier has a 400px thumbnail.
        original_photo (bool): Indicates if the tier has an original photo.
        expiring_link (bool): Indicates if the tier has an expiring link.

    Meta:
        verbose_name (str): The human-readable name for the model in the Django admin.
        verbose_name_plural (str): The plural name for the model in the Django admin.

    Methods:
        __str__(): Returns a string representation of the tier.

    Usage:
        To use this model, inherit from it in your Django app.

        Example:
            class YourModel(Tier):
                additional_field = models.CharField(max_length=50)

            This will create a model with a UUID-based primary key and additional fields.
    """

    name = models.CharField(max_length=255)
    thumbnails = models.BooleanField(default=False)
    original_photo = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tier'
        verbose_name_plural = 'Tiers'

    def __str__(self) -> str:
        return f'{self.name}'


class User(AbstractUser):
    """
    Custom User model with a UUID-based primary key and tier association.

    Attributes:
        id (UUID): The UUID-based primary key of the user.
        tier (ForeignKey): The tier associated with the user.

    Meta:
        verbose_name (str): The human-readable name for the model in the Django admin.
        verbose_name_plural (str): The plural name for the model in the Django admin.

    Methods:
        __str__(): Returns a string representation of the user.

    Usage:
        To use this model, inherit from it in your Django app and customize as needed.

        Example:
            class YourUserModel(User):
                additional_field = models.CharField(max_length=50)

            This will create a custom user model with a UUID-based primary key and additional fields.
    """
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        unique=True,
        verbose_name='ID',
    )
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='users_tier', null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f'{self.username} {self.tier} '


class Images(UUIDMixin, models.Model):
    """
    Model representing an image with a UUID-based primary key.

    Attributes:
        id (UUID): The UUID-based primary key of the image.
        image (ImageField): The image file.
        owner (ForeignKey): The user who owns the image.
        expired_time (int): The expiration time for the image in seconds.

    Meta:
        verbose_name (str): The human-readable name for the model in the Django admin.
        verbose_name_plural (str): The plural name for the model in the Django admin.

    Methods:
        save(): Overrides the default save method to perform additional checks.
        __str__(): Returns a string representation of the image.

    Usage:
        To use this model, inherit from it in your Django app.

        Example:
            class YourImageModel(Images):
                additional_field = models.CharField(max_length=50)

            This will create a model with a UUID-based primary key and additional fields.
    """

    image = models.ImageField(upload_to='media/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    expired_time = models.IntegerField(
        default=300,
        validators=[
            MaxValueValidator(30000),
            MinValueValidator(300)
        ]
    )

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def save(self, *args, **kwargs):
        img = Image.open(self.image.path)
        if not img.format == 'JPG' or img.format == 'PNG':
            raise ValidationError("Use jpg or png format.")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.owner.username} {self.expired_time} '
