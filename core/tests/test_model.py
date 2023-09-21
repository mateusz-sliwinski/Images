# Standard Library
import uuid

# Django
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

# Project
from core.models import ExpiredLink
from core.models import Images
from core.models import Thumbnail
from core.models import Tier

User = get_user_model()


class UserModelTests(TestCase):
    def setUp(self):
        self.tier = Tier.objects.create(name='Test Tier')

    def test_create_user(self):
        user = User.objects.create(username='testuser', tier=self.tier)
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.tier, self.tier)

    def test_user_id_is_uuid(self):
        user = User.objects.create(username='testuser', tier=self.tier)
        self.assertIsNotNone(user.id)
        self.assertTrue(isinstance(user.id, uuid.UUID))

    def test_user_id_is_unique(self):
        user1 = User.objects.create(username='testuser1', tier=self.tier)
        user2 = User.objects.create(username='testuser2', tier=self.tier)
        self.assertNotEqual(user1.id, user2.id)

    def test_tier_association(self):
        user = User.objects.create(username='testuser', tier=self.tier)
        self.assertEqual(user.tier, self.tier)


class TierModelTests(TestCase):
    def test_str_representation(self):
        tier = Tier(name='Test Tier')
        self.assertEqual(str(tier), 'Test Tier')

    def test_default_values(self):
        tier = Tier(name='Default Tier')
        self.assertFalse(tier.thumbnails)
        self.assertFalse(tier.original_photo)
        self.assertFalse(tier.expiring_link)

    def test_create_tier(self):
        tier = Tier.objects.create(name='New Tier')
        self.assertEqual(str(tier), 'New Tier')

    def test_verbose_names(self):
        self.assertEqual(Tier._meta.verbose_name, 'Tier')
        self.assertEqual(Tier._meta.verbose_name_plural, 'Tiers')

    def test_update_tier(self):
        tier = Tier.objects.create(name='Update Tier')
        tier.name = 'Updated Tier'
        tier.thumbnails = True
        tier.original_photo = True
        tier.expiring_link = True
        tier.save()
        updated_tier = Tier.objects.get(pk=tier.pk)
        self.assertEqual(updated_tier.name, 'Updated Tier')
        self.assertTrue(updated_tier.thumbnails)
        self.assertTrue(updated_tier.original_photo)
        self.assertTrue(updated_tier.expiring_link)

    def test_delete_tier(self):
        tier = Tier.objects.create(name='Delete Tier')
        tier_pk = tier.pk
        tier.delete()
        with self.assertRaises(Tier.DoesNotExist):
            Tier.objects.get(pk=tier_pk)


class ThumbnailModelTests(TestCase):
    def setUp(self):
        self.thumbnail_200 = SimpleUploadedFile(
            "thumbnail_200.jpg", b"file_content", content_type="image/jpeg"
        )
        self.thumbnail_400 = SimpleUploadedFile(
            "thumbnail_400.jpg", b"file_content", content_type="image/jpeg"
        )

    def test_create_thumbnail(self):
        thumbnail = Thumbnail.objects.create(
            thumbnail_200=self.thumbnail_200, thumbnail_400=self.thumbnail_400
        )
        thumbnail_200_filename = thumbnail.thumbnail_200.name
        thumbnail_400_filename = thumbnail.thumbnail_400.name

        self.assertTrue(thumbnail_200_filename.startswith('thumbnail_200/'))
        self.assertTrue(thumbnail_200_filename.endswith('.jpg'))

        self.assertTrue(thumbnail_400_filename.startswith('thumbnail_400/'))
        self.assertTrue(thumbnail_400_filename.endswith('.jpg'))

    def test_verbose_names(self):
        self.assertEqual(Thumbnail._meta.verbose_name, 'Thumbnail')
        self.assertEqual(Thumbnail._meta.verbose_name_plural, 'Thumbnails')


class ExpiredLinkModelTests(TestCase):
    def test_create_expired_link(self):
        expiration_time = timezone.now() + timezone.timedelta(days=1)
        expired_link = ExpiredLink.objects.create(
            token='test_token', expiration_time=expiration_time
        )
        self.assertIsInstance(expired_link, ExpiredLink)
        self.assertEqual(expired_link.token, 'test_token')
        self.assertEqual(expired_link.expiration_time, expiration_time)

    def test_expired_link_with_no_token(self):
        expiration_time = timezone.now() + timezone.timedelta(days=1)
        expired_link = ExpiredLink.objects.create(
            token=None, expiration_time=expiration_time
        )
        self.assertIsInstance(expired_link, ExpiredLink)
        self.assertIsNone(expired_link.token)
        self.assertEqual(expired_link.expiration_time, expiration_time)

    def test_expired_link_with_past_expiration(self):
        expiration_time = timezone.now() - timezone.timedelta(days=1)
        expired_link = ExpiredLink.objects.create(
            token='test_token', expiration_time=expiration_time
        )
        self.assertIsInstance(expired_link, ExpiredLink)
        self.assertEqual(expired_link.token, 'test_token')
        self.assertEqual(expired_link.expiration_time, expiration_time)

    def test_verbose_names(self):
        self.assertEqual(ExpiredLink._meta.verbose_name, 'Expired Link')
        self.assertEqual(ExpiredLink._meta.verbose_name_plural, 'Expired Links')


class ImagesModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.thumbnail = Thumbnail.objects.create()
        self.expired_link = ExpiredLink.objects.create()
        image_content = b"file_content"
        self.test_image = SimpleUploadedFile(
            "test_image.jpg", image_content, content_type="image/jpeg"
        )

    def test_create_image(self):
        image_obj = Images(
            image=self.test_image,
            owner=self.user,
            thumbnail=self.thumbnail,
            expired_link=self.expired_link,
            expired_time=3600
        )
        image_obj.save()

        saved_image = Images.objects.get(id=image_obj.id)
        self.assertIsInstance(saved_image, Images)
        self.assertEqual(saved_image.owner, self.user)
        self.assertEqual(saved_image.thumbnail, self.thumbnail)
        self.assertEqual(saved_image.expired_link, self.expired_link)
        self.assertEqual(saved_image.expired_time, 3600)

    def test_image_without_owner(self):
        with self.assertRaises(ValidationError):
            image_file = SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg"
            )
            image = Images(image=image_file, thumbnail=self.thumbnail, expired_time=3600)
            image.full_clean()

    def test_str_representation(self):
        image = Images.objects.create(
            image=None, owner=self.user, thumbnail=self.thumbnail,
            expired_link=self.expired_link, expired_time=3600
        )
        expected_str = f'{self.user.username} 3600'
        self.assertEqual(str(image), expected_str)

    def test_verbose_names(self):
        self.assertEqual(Images._meta.verbose_name, 'Image')
        self.assertEqual(Images._meta.verbose_name_plural, 'Images')
