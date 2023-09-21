# Standard Library
import mimetypes
from datetime import timedelta

# Django
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone

# 3rd-party
from PIL import Image as PILImage
from PIL import ImageOps
from rest_framework import status
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

# Project
from core.models import ExpiredLink
from core.models import Images
from core.serializers import ImageSerializer
from core.utils import create_img_200
from core.utils import create_img_200_400
from core.utils import generate_random_token
from core.utils import validation_photo_views


class UploadImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        image_data = request.data['image']
        expired_time = request.data.get('expired_time', None)
        validation_result = validation_photo_views(user, image_data, request)

        if validation_result is not None:
            return validation_result

        user_tier = user.tier.name if user.tier else None

        image = Images(owner=user)
        image_name = image_data.name

        if user_tier == 'Basic':
            with PILImage.open(image_data) as img:
                thumbnail, thumbnail_link = create_img_200(image_name, img, request)
            image.expired_link = None
            image.image = None
            image.thumbnail = thumbnail
            image.save()

            serializer_data = {
                "id": str(image.id),
                "thumbnail_link": thumbnail_link,
                "owner": str(image.owner.id)
            }
            return Response(serializer_data, status=status.HTTP_201_CREATED)

        if user_tier == 'Premium':
            with PILImage.open(image_data) as img:
                img = ImageOps.exif_transpose(img.convert('RGB'))
                thumbnail, thumbnail_link_200, thumbnail_link_400 = create_img_200_400(image_name, img, request)

            image.expired_link = None
            image.image.save(image_name, image_data)
            image.thumbnail = thumbnail

            image.save()

            serializer_data = {
                "id": str(image.id),
                "image": request.build_absolute_uri(image.image.url),
                "thumbnail_link_200": thumbnail_link_200,
                "thumbnail_link_400": thumbnail_link_400,
                "owner": str(image.owner.id)
            }
            return Response(serializer_data, status=status.HTTP_201_CREATED)

        if user_tier == 'Enterprise':
            expiration_timedelta = timedelta(seconds=int(expired_time))
            expiration_time = timezone.now() + expiration_timedelta

            with PILImage.open(image_data) as img:
                img = ImageOps.exif_transpose(img.convert('RGB'))

                thumbnail, thumbnail_link_200, thumbnail_link_400 = create_img_200_400(image_name, img, request)

            expired_link = ExpiredLink.objects.create(token=generate_random_token(), expiration_time=expiration_time)
            image.image.save(image_name, image_data)
            image.thumbnail = thumbnail
            image.expired_link = expired_link
            image.save()

            base_url = request.build_absolute_uri('/')
            token_url = reverse('token_view', args=[expired_link.token])
            complete_url = f'{base_url}{token_url}'

            serializer_data = {
                "id": str(image.id),
                "image": request.build_absolute_uri(image.image.url),
                "thumbnail_link_200": thumbnail_link_200,
                "thumbnail_link_400": thumbnail_link_400,
                "expired_link": complete_url,
                "owner": str(image.owner.id)
            }
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        else:
            return Response("Expired time is not provided for this image.", status=status.HTTP_400_BAD_REQUEST)


class ListImagesView(APIView):
    def get(self, request):
        user = request.user

        images = Images.objects.filter(owner=user)
        serializer_data = []

        for img in images:

            complete_url = None
            if img.expired_link:
                token_url = reverse('token_view', args=[img.expired_link.token])
                complete_url = request.build_absolute_uri(token_url)

            thumbnail_200_url = request.build_absolute_uri(
                img.thumbnail.thumbnail_200.url) if img.thumbnail and img.thumbnail.thumbnail_200 else None
            thumbnail_400_url = request.build_absolute_uri(
                img.thumbnail.thumbnail_400.url) if img.thumbnail and img.thumbnail.thumbnail_400 else None

            img_data = {
                "id": str(img.id),
                "image": request.build_absolute_uri(img.image.url) if img.image else None,
                "thumbnail_200": thumbnail_200_url,
                "thumbnail_400": thumbnail_400_url,
                "expired_link": complete_url,
                "owner": str(img.owner.id)
            }
            serializer_data.append(img_data)

        return Response(serializer_data, status=status.HTTP_200_OK)


class TokenView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, token):
        expired_link = get_object_or_404(ExpiredLink, token=token)

        if expired_link.expiration_time < timezone.now():
            return Response({"detail": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST)

        image = expired_link.images_set.first()
        if not image:
            return Response({"detail": "No image found for this link."}, status=status.HTTP_400_BAD_REQUEST)

        image_path = image.image.path

        content_type, encoding = mimetypes.guess_type(image_path)
        extension = mimetypes.guess_extension(content_type)
        filename = f"{image.image.name}{extension}"

        response = FileResponse(open(image_path, "rb"), content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response
