# Standard Library
import uuid

# Django
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

# 3rd-party
from PIL import Image


class UUIDMixin(models.Model):
    """
    A mixin for adding a UUID (Universally Unique Identifier) field as the primary key to a Django model.

    This mixin provides a UUID field named 'id' as the primary key for the model, ensuring each record
    has a unique identifier. The 'id' field is automatically generated using the uuid4 function from the
    uuid module.

    Attributes:
        id (uuid.UUID): The UUID field serving as the primary key.

    Meta:
        abstract (bool): Indicates that this model is abstract and should not be created as a separate database table.
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
    Represents a membership tier with specific features and settings.

    Each tier can have a unique name and specific features, such as the availability of thumbnails,
    original photos, and expiring links.

    Attributes:
        id (uuid.UUID): The UUID serving as the primary key.
        name (str): The name of the membership tier.
        thumbnails (bool): True if thumbnails are available for this tier, False otherwise.
        original_photo (bool): True if original photos are available for this tier, False otherwise.
        expiring_link (bool): True if expiring links are available for this tier, False otherwise.

    Meta:
        verbose_name (str): The singular display name for this model in the Django admin interface.
        verbose_name_plural (str): The plural display name for this model in the Django admin interface.

    Methods:
        __str__: Returns the name of the tier as its string representation.

    Inherits:
        UUIDMixin: A mixin providing a UUID field as the primary key.

    """
    name = models.CharField(max_length=255)
    thumbnails = models.BooleanField(default=False)
    original_photo = models.BooleanField(default=False)
    expiring_link = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tier'
        verbose_name_plural = 'Tiers'

    def __str__(self) -> str:
        """
        Return the name of the membership tier as its string representation.

        Returns:
            str: The name of the membership tier.
        """
        return f'{self.name}'


class User(AbstractUser):
    """
    Represents a user in the system.

    This class extends the Django AbstractUser class and includes additional fields such as a UUID-based
    primary key and a foreign key to represent the user's membership tier.

    Attributes:
        id (uuid.UUID): The UUID serving as the primary key for the user.
        tier (Tier): The membership tier associated with the user (if any).

    Meta:
        verbose_name (str): The singular display name for this model in the Django admin interface.
        verbose_name_plural (str): The plural display name for this model in the Django admin interface.

    Methods:
        __str__: Returns a string representation of the user, including the username and associated tier.

    Inherits:
        AbstractUser: Django's built-in abstract base class for user management.

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
        """
        Return a string representation of the user, including the username and associated tier.

        Returns:
            str: A string representing the user, in the format '<username> <tier>'.
        """
        return f'{self.username} {self.tier} '


class Thumbnail(UUIDMixin, models.Model):
    """
    Represents thumbnail images with specific dimensions.

    This class defines fields to store thumbnail images with dimensions of 200x200 and 400x400 pixels.

    Attributes:
        id (uuid.UUID): The UUID serving as the primary key for the thumbnail.
        thumbnail_200 (django.db.models.fields.files.ImageField): The thumbnail image with dimensions 200x200 pixels.
        thumbnail_400 (django.db.models.fields.files.ImageField): The thumbnail image with dimensions 400x400 pixels (nullable).

    Meta:
        verbose_name (str): The singular display name for this model in the Django admin interface.
        verbose_name_plural (str): The plural display name for this model in the Django admin interface.

    Inherits:
        UUIDMixin: A mixin providing a UUID field as the primary key.

    """
    thumbnail_200 = models.ImageField(upload_to='thumbnail_200')
    thumbnail_400 = models.ImageField(upload_to='thumbnail_400', null=True)

    class Meta:
        verbose_name = 'Thumbnail'
        verbose_name_plural = 'Thumbnails'


class ExpiredLink(UUIDMixin, models.Model):
    """
    Represents an expired link with a token and expiration time.

    This class stores information about an expired link, including a token and the time when the link expired.

    Attributes:
        id (uuid.UUID): The UUID serving as the primary key for the expired link.
        token (str): The token associated with the expired link.
        expiration_time (datetime.datetime): The date and time when the link expired.

    Meta:
        verbose_name (str): The singular display name for this model in the Django admin interface.
        verbose_name_plural (str): The plural display name for this model in the Django admin interface.

    Methods:
        __str__: Returns a string representation of the expiration time of the link.

    Inherits:
        UUIDMixin: A mixin providing a UUID field as the primary key.

    """
    token = models.CharField(max_length=255, null=True)
    expiration_time = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Expired Link'
        verbose_name_plural = 'Expired Links'

    def __str__(self) -> str:
        """
        Return a string representation of the expiration time of the link.

        Returns:
              str: A string representing the expiration time of the link.
        """
        return f'{self.expiration_time.strftime("%Y-%m-%d %H:%M:%S")}'


class Images(UUIDMixin, models.Model):
    """
    Represents an image uploaded by a user, with associated details.

    This class stores information about an uploaded image, including the image file, the owner (a user),
    a thumbnail associated with the image, an expired link (if any), and the expired time for the link.

    Attributes:
        id (uuid.UUID): The UUID serving as the primary key for the image.
        image (django.db.models.fields.files.ImageField): The uploaded image file (nullable).
        owner (User): The user who uploaded the image.
        thumbnail (Thumbnail): The associated thumbnail for the image (nullable).
        expired_link (ExpiredLink): The associated expired link for the image (nullable).
        expired_time (int): The expiration time for the link in seconds (nullable).

    Meta:
        verbose_name (str): The singular display name for this model in the Django admin interface.
        verbose_name_plural (str): The plural display name for this model in the Django admin interface.

    Methods:
        save: Overrides the save method to validate the image format before saving.
        __str__: Returns a string representation of the image, including the owner's username and expiration time.

    Inherits:
        UUIDMixin: A mixin providing a UUID field as the primary key.

    """
    image = models.ImageField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail = models.ForeignKey(Thumbnail, on_delete=models.CASCADE, null=True)
    expired_link = models.ForeignKey(ExpiredLink, on_delete=models.CASCADE, null=True)
    expired_time = models.IntegerField(
        null=True,
        validators=[
            MaxValueValidator(30000),
            MinValueValidator(300)
        ]
    )

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    def save(self, *args, **kwargs):
        """
                Overrides the save method to validate the image format before saving.

                Raises:
                    ValidationError: If the image format is not 'jpeg' or 'png'.

                """
        if self.image:
            try:
                img = Image.open(self.image.path)
                img_format = img.format.lower() if img.format else None
                if img_format not in ['jpeg', 'jpg', 'png']:
                    raise ValidationError("Use jpg or png format.")
            except FileNotFoundError:
                pass
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representation of the image, including the owner's username and expiration time.

        Returns:
            str: A string representing the image in the format '<username> <expiration_time>'.
        """
        return f'{self.owner.username} {self.expired_time}'
