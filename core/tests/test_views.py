# Standard Library
from datetime import datetime, timedelta

# Django
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# 3rd-party
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

# Project
from core.models import ExpiredLink
from core.models import Images
from core.models import Thumbnail
from core.models import Tier

User = get_user_model()


class UploadImageViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.tier_basic = Tier.objects.create(name='Basic')
        self.tier_premium = Tier.objects.create(name='Premium')
        self.tier_enterprise = Tier.objects.create(name='Enterprise')

        self.user_basic = User.objects.create(username='user_basic', password='password')
        self.user_basic.tier = self.tier_basic
        self.user_basic.save()

        self.user_premium = User.objects.create(username='user_premium', password='password')
        self.user_premium.tier = self.tier_premium
        self.user_premium.save()

        self.user_enterprise = User.objects.create(username='user_enterprise', password='password')
        self.user_enterprise.tier = self.tier_enterprise
        self.user_enterprise.save()

    def test_upload_image_basic_tier(self):
        self.client.force_authenticate(user=self.user_basic)

        with open('media/test.png', 'rb') as image_file:
            image = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

            response = self.client.post('/upload_image/', {'image': image}, format='multipart')
            self.assertEqual(response.status_code, 201)

    def test_upload_image_premium_tier(self):
        self.client.force_authenticate(user=self.user_premium)

        with open('media/test.png', 'rb') as image_file:
            image = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

            response = self.client.post('/upload_image/', {'image': image}, format='multipart')
            self.assertEqual(response.status_code, 201)

    def test_upload_image_enterprise_tier(self):
        expired_time = 3600
        self.client.force_authenticate(user=self.user_enterprise)

        with open('media/test.png', 'rb') as image_file:
            image = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

            response = self.client.post('/upload_image/', {'image': image, 'expired_time': expired_time},
                                        format='multipart')
            self.assertEqual(response.status_code, 201)

    def test_upload_image_invalid_tier(self):
        user_invalid_tier = User.objects.create(username='user_invalid', password='password')
        self.client.force_authenticate(user=user_invalid_tier)

        with open('media/test.png', 'rb') as image_file:
            image = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

            response = self.client.post('/upload_image/', {'image': image}, format='multipart')
            self.assertEqual(response.status_code, 400)

    def test_upload_image_no_authentication(self):
        with open('media/test.png', 'rb') as image_file:
            image = SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")

            response = self.client.post('/upload_image/', {'image': image}, format='multipart')
            self.assertEqual(response.status_code, 400)


class ListImagesViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.thumbnail = Thumbnail.objects.create(thumbnail_200="media/test.png",
                                                  thumbnail_400="media/test.png")
        self.image1 = Images.objects.create(owner=self.user, image="media/test.png", thumbnail=self.thumbnail)
        self.expired_link = ExpiredLink.objects.create(token="testtoken")
        self.image2 = Images.objects.create(owner=self.user, image="media/test.png", expired_link=self.expired_link)

    def test_list_images_authenticated_user(self):
        url = reverse('list_images')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_images_unauthenticated_user(self):
        url = reverse('list_images')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_images_no_images(self):
        url = reverse('list_images')
        self.client.force_authenticate(user=self.user)
        Images.objects.all().delete()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TokenViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpassword')

        image_content = b"image content"
        self.image = SimpleUploadedFile("media/test.png", image_content, content_type="image/jpeg")

        expiration_time = datetime.now() + timedelta(days=1)
        self.expired_link = ExpiredLink.objects.create(token="testtoken", expiration_time=expiration_time)

        self.image_record = Images.objects.create(expired_link=self.expired_link, image=self.image, owner=self.user)

    def test_token_view_expired_token(self):
        self.expired_link.expiration_time = "2022-01-01T12:00:00Z"
        self.expired_link.save()

        url = reverse("token_view", args=[self.expired_link.token])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "This link has expired.")

    def test_token_view_invalid_token(self):
        url = reverse("token_view", args=["invalidtoken"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
