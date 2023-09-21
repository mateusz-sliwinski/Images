# Standard Library
import random
import string
from io import BytesIO

# Django
from django.core.files.base import ContentFile

# 3rd-party
from PIL import ImageOps
from rest_framework import status
from rest_framework.response import Response

# Project
from core.models import Thumbnail


def validation_photo_views(user, image_data, request):
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


def create_img_200_400(image_name, img, request):
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


def create_img_200(image_name, img, request):
    img = ImageOps.exif_transpose(img.convert('RGB'))
    img.thumbnail((img.width, 200))
    thumbnail_stream = BytesIO()
    img.save(thumbnail_stream, format='JPEG')
    thumbnail = Thumbnail()
    thumbnail.thumbnail_200.save(image_name, ContentFile(thumbnail_stream.getvalue()), save=True)
    thumbnail_link = request.build_absolute_uri(thumbnail.thumbnail_200.url)
    return thumbnail, thumbnail_link


def generate_random_token(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
