# Standard Library
import random
import string
from io import BytesIO

# Django
from django.core.files.base import ContentFile

# 3rd-party
from PIL import ImageOps
from rest_framework import request
from rest_framework import status
from rest_framework.response import Response

# Project
from core.models import Thumbnail


def validation_photo_views(user, image_data, request: request.Request) -> Response:
    """
    Validate the user, image data, and request for photo-related views.

    This function performs validation checks for user authentication, image data, and image format.

    Args:
        user: The user making the request.
        image_data: The image data received in the request.
        request: The HTTP request object.

    Returns:
        Response: A Response object with an error message and status if validation fails.

    """
    if user.is_anonymous:
        return Response(
            {"error": "Cannot Add data."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if image_data is None and 'image' not in request.FILES:
        return Response(
            {"error": "Image data not provided."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.tier is None:
        return Response(
            {"error": "User does not have a valid tier."},
            status=status.HTTP_400_BAD_REQUEST
        )

    image_format = image_data.content_type
    if image_format not in ['image/jpeg', 'image/png']:
        return Response(
            {"error": "Invalid image format. Use jpg or png."},
            status=status.HTTP_400_BAD_REQUEST
        )


def create_img_200_400(image_name, img, request) -> tuple[Thumbnail, str, str]:
    """
    Create 200x200 and 400x400 thumbnail images from the original image.

    This function creates thumbnail images with dimensions 200x200 and 400x400 pixels from the original image.

    Args:
        image_name (str): The name of the original image.
        img: The original image to create thumbnails from.
        request: The HTTP request object.

    Returns:
        Tuple[Thumbnail, str, str]: A tuple containing the created Thumbnail object, the link to the 200x200 thumbnail,
                                   and the link to the 400x400 thumbnail.

    """
    img_200 = img.copy()
    img_400 = img.copy()

    img_200.thumbnail((img.width, 200))
    thumbnail_stream_200 = BytesIO()
    img_200.save(thumbnail_stream_200, format='JPEG')

    img_400.thumbnail((img.width, 400))
    thumbnail_stream_400 = BytesIO()
    img_400.save(thumbnail_stream_400, format='JPEG')

    thumbnail = Thumbnail.objects.create()
    thumbnail.thumbnail_200.save(image_name, ContentFile(thumbnail_stream_200.getvalue()), save=False)
    thumbnail.thumbnail_400.save(image_name, ContentFile(thumbnail_stream_400.getvalue()), save=False)
    thumbnail.save()

    thumbnail_link_200 = request.build_absolute_uri(thumbnail.thumbnail_200.url)
    thumbnail_link_400 = request.build_absolute_uri(thumbnail.thumbnail_400.url)

    return thumbnail, thumbnail_link_200, thumbnail_link_400


def create_img_200(image_name: str, img, request: request.Request) -> tuple[Thumbnail, str]:
    """
    Create a 200x200 thumbnail image from the original image.

    This function creates a thumbnail image with dimensions 200x200 pixels from the original image.

    Args:
        image_name (str): The name of the original image.
        img: The original image to create the thumbnail from.
        request: The HTTP request object.

    Returns:
        Tuple[Thumbnail, str]: A tuple containing the created Thumbnail object and the link to the 200x200 thumbnail.

    """
    img = ImageOps.exif_transpose(img.convert('RGB'))
    img.thumbnail((img.width, 200))
    thumbnail_stream = BytesIO()
    img.save(thumbnail_stream, format='JPEG')
    thumbnail = Thumbnail()
    thumbnail.thumbnail_200.save(image_name, ContentFile(thumbnail_stream.getvalue()), save=True)
    thumbnail_link = request.build_absolute_uri(thumbnail.thumbnail_200.url)
    return thumbnail, thumbnail_link


def generate_random_token(length: int = 32) -> str:
    """
    Generate a random token of the specified length.

    This function generates a random token consisting of letters (both uppercase and lowercase) and digits.

    Args:
        length (int): The length of the token to be generated. Default is 32.

    Returns:
        str: A randomly generated token.

    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
