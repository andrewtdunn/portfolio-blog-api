import tempfile
import os

from PIL import Image


from picture.serializers import PictureSerializer, PictureDetailSerializer
from core.models import Picture
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

PICTURES_URL = reverse("picture:picture-list")


def image_upload_url(picture_id):
    """Return URL for picture image upload"""
    return reverse("picture:picture-upload-image", args=[picture_id])


def detail_url(picture_id):
    """Return picture detail URL"""
    return reverse("picture:picture-detail", args=[picture_id])


def sample_picture(user, caption="portrait"):
    """Create and return a sample picture"""
    return Picture.objects.create(user=user, caption=caption)


class PublicPictureApiTests(TestCase):
    """Test unauthenticated picture API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@andrewtdunn.com", "testpass"
        )

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PICTURES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePictureApiTests(TestCase):
    """Test Authenticated picture API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@andrewtdunn.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_pictures(self):
        """Test retrieving a list of pictures"""
        sample_picture(user=self.user)
        sample_picture(user=self.user)

        res = self.client.get(PICTURES_URL)

        pictures = Picture.objects.all().order_by("-id")
        serializer = PictureSerializer(pictures, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_pictures_limited_to_user(self):
        """Test retrieving pictures for the user"""
        user2 = get_user_model().objects.create_user(
            "other@andrewtdunn.com", "password123"
        )
        sample_picture(user=user2)
        sample_picture(user=self.user)

        res = self.client.get(PICTURES_URL)

        pictures = Picture.objects.filter(user=self.user)
        serializer = PictureSerializer(pictures, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_picture_detail(self):
        """Test viewing a picture detail"""
        picture = sample_picture(user=self.user)

        url = detail_url(picture.id)
        res = self.client.get(url)

        serializer = PictureDetailSerializer(picture)
        self.assertEqual(res.data, serializer.data)


class PictureImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@andrewtdunn.com", "testpass"
        )
        self.client.force_authenticate(self.user)
        self.picture = sample_picture(user=self.user)

    def tearDown(self):
        self.picture.image.delete()

    def test_upload_image_to_picture(self):
        """Test uploading an image to picture"""
        url = image_upload_url(self.picture.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.picture.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.picture.image.path))

    def test_upload_image_bad_request(self):
        """test uploading an invalid image"""
        url = image_upload_url(self.picture.id)
        res = self.client.post(url, {"image": "notimage"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
