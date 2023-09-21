

# Django
from django.test import TestCase

# 3rd-party
from PIL import Image
from rest_framework.test import APIRequestFactory

# Project
from core.models import Thumbnail
from core.models import User
from core.utils import create_img_200
from core.utils import create_img_200_400


class CreateImageTests(TestCase):
    def setUp(self):
        with open('media/test_image.jpg', 'wb') as f:
            f.write(b'Image content')

        user = User.objects.create_user(username='testuser', password='password')

        self.factory = APIRequestFactory()
        self.request = self.factory.post('/upload_image/', {'image': 'test_image.jpg'})
        self.request.user = user

    def test_create_img_200_400(self):
        image = Image.new('RGB', (800, 600))

        username = f'testuser_{self._testMethodName}'

        user = User.objects.create_user(username=username, password='password')

        factory = APIRequestFactory()
        request = factory.post('/upload_image/', {'image': 'test_image.jpg'})
        request.user = user

        thumbnail, thumbnail_link_200, thumbnail_link_400 = create_img_200_400('test_image.jpg', image, request)

        expected_thumbnail_link_200 = 'http://testserver/media' + thumbnail.thumbnail_200.url.replace('/media', '')
        expected_thumbnail_link_400 = 'http://testserver/media' + thumbnail.thumbnail_400.url.replace('/media', '')

        self.assertEqual(thumbnail_link_200, expected_thumbnail_link_200)
        self.assertEqual(thumbnail_link_400, expected_thumbnail_link_400)

        thumbnail.delete()

    def tearDown(self):
        Thumbnail.objects.all().delete()


class CreateImg200Test(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_create_img_200(self):
        img = Image.new('RGB', (800, 600))
        request = self.factory.get('/upload_image/')
        request.user = None
        thumbnail, thumbnail_link = create_img_200('test_image.jpg', img, request)
        self.assertIsInstance(thumbnail, Thumbnail)
        expected_thumbnail_link = f'http://testserver{thumbnail.thumbnail_200.url}'
        self.assertEqual(thumbnail_link, expected_thumbnail_link)
        thumbnail.delete()
