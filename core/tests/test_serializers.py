
# Standard Library
from unittest import TestCase

# 3rd-party
from rest_framework.test import APIClient

# Project
from core.models import Images
from core.models import Tier
from core.models import User
from core.serializers import ImageSerializer


class ImageModelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        try:
            self.user_enterprise = User.objects.get(username='testuser_enterprise')
        except User.DoesNotExist:
            self.user_enterprise = User.objects.create(username='testuser_enterprise')

        try:
            self.user_normal = User.objects.get(username='testuser_normal')
        except User.DoesNotExist:
            self.user_normal = User.objects.create(username='testuser_normal')

        self.tier_enterprise, _ = Tier.objects.get_or_create(name='Enterprise')

        self.tier_normal, _ = Tier.objects.get_or_create(name='Normal')

        self.user_enterprise.tier = self.tier_enterprise
        self.user_enterprise.save()

        self.user_normal.tier = self.tier_normal
        self.user_normal.save()

        self.image_enterprise = Images.objects.create(owner=self.user_enterprise, expired_time=3000)
        self.image_normal = Images.objects.create(owner=self.user_normal, expired_time=5000)

    def create_request(self, user=None):
        request = self.client.request().wsgi_request
        request.user = user
        return request

    def test_serializer_fields_for_enterprise(self):
        request = self.create_request(user=self.user_enterprise)
        serializer = ImageSerializer(instance=self.image_enterprise, context={'request': request})

        expected_fields = {'id', 'image', 'expired_time'}
        actual_fields = set(serializer.data.keys())

        self.assertEqual(actual_fields, expected_fields)

    def test_serializer_fields_for_normal_user(self):
        request = self.create_request(user=self.user_normal)
        serializer = ImageSerializer(instance=self.image_normal, context={'request': request})

        expected_fields = {'id', 'image'}
        actual_fields = set(serializer.data.keys())

        self.assertEqual(actual_fields, expected_fields)
