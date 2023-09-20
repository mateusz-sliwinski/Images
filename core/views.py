# Django
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image as PILImage, ImageOps

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Project
from core.models import Images
from core.serializers import ImageSerializer
from core.utils import validation_photo_views, create_img_200_400, create_img_200


class UploadImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        image_data = request.data['image']
        validation_result = validation_photo_views(user, image_data, request)

        if validation_result is not None:
            return validation_result

        user_tier = user.tier.name if user.tier else None

        image = Images(owner=user)
        image_name = image_data.name

        if user_tier == 'Basic':
            with PILImage.open(image_data) as img:
                thumbnail, thumbnail_link = create_img_200(image_name, img, request)
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
            with PILImage.open(image_data) as img:
                img = ImageOps.exif_transpose(img.convert('RGB'))

                thumbnail, thumbnail_link_200, thumbnail_link_400 = create_img_200_400(image_name, img, request)

            image.image.save(image_name, image_data)
            image.thumbnail = thumbnail
            image.save()

            serializer_data = {
                "id": str(image.id),
                "image": request.build_absolute_uri(image.image.url),
                "thumbnail_link_200": thumbnail_link_200,
                "thumbnail_link_400": thumbnail_link_400,
                "expired_time": image.expired_time,
                "owner": str(image.owner.id)
            }
            return Response(serializer_data, status=status.HTTP_201_CREATED)


class ListImagesView(APIView):
    def get(self, request):
        user = request.user

        images = Images.objects.filter(owner=user)
        serializer_data = []
        for img in images:
            thumbnail_200_url = request.build_absolute_uri(img.thumbnail.thumbnail_200.url) if img.thumbnail and img.thumbnail.thumbnail_200 else None
            thumbnail_400_url = request.build_absolute_uri(img.thumbnail.thumbnail_400.url) if img.thumbnail and img.thumbnail.thumbnail_400 else None

            img_data = {
                "id": str(img.id),
                "image": request.build_absolute_uri(img.image.url) if img.image else None,
                "thumbnail_200": thumbnail_200_url,
                "thumbnail_400": thumbnail_400_url,
                "expired_link": img.expired_time if img.expired_time else None,
                "owner": str(img.owner.id)
            }
            serializer_data.append(img_data)

        return Response(serializer_data, status=status.HTTP_200_OK)
