# Django
from django.test import SimpleTestCase
from django.urls import resolve
from django.urls import reverse

# Project
from core.views import ListImagesView
from core.views import TokenView
from core.views import UploadImageView


class TestUrls(SimpleTestCase):

    def test_upload_image_url_resolves(self):
        url = reverse('upload_image')
        self.assertEquals(resolve(url).func.view_class, UploadImageView)

    def test_list_images_url_resolves(self):
        url = reverse('list_images')
        self.assertEquals(resolve(url).func.view_class, ListImagesView)

    def test_token_view_url_resolves(self):
        url = reverse('token_view', args=['some_token'])
        self.assertEquals(resolve(url).func.view_class, TokenView)
