from picture.serializers import SlideshowSerializer
from core.models import Slideshow
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from picture.tests.test_pictures_api import sample_picture

SLIDESHOWS_URL = reverse("picture:slideshow-list")


def sample_slideshow(user, title="sample slideshow"):
    """Create a new sample slideshow"""
    picture1 = sample_picture(user=user)
    picture2 = sample_picture(user=user)
    slideshow = Slideshow.objects.create(user=user, title=title)
    slideshow.pictures.add(picture1)
    slideshow.pictures.add(picture2)
    return slideshow


def detail_url(slideshow_id):
    """Return slideshow detail URL"""
    return reverse("picture:slideshow-detail", args=[slideshow_id])


class PublicSlideshowAPITests(TestCase):
    """Test unauthenticated slideshow API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SLIDESHOWS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSlideshowAPITests(TestCase):
    """Test authenticated slideshow API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@andrewtdunn.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_slideshows(self):
        """Test retrieving a list of slideshows"""
        sample_slideshow(user=self.user)
        sample_slideshow(user=self.user)

        res = self.client.get(SLIDESHOWS_URL)

        slideshows = Slideshow.objects.all().order_by("-id")
        serializer = SlideshowSerializer(slideshows, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_slideshow_limited_to_user(self):
        """Test retreiving slideshows for user"""
        user2 = get_user_model().objects.create_user(
            "other@andrewtdunn.com", "password123"
        )
        sample_slideshow(user=user2)
        sample_slideshow(user=self.user)

        res = self.client.get(SLIDESHOWS_URL)

        slideshows = Slideshow.objects.filter(user=self.user)
        serializer = SlideshowSerializer(slideshows, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_slideshow_with_pictures(self):
        """Test creating slideshow with pictures"""
        picture1 = sample_picture(user=self.user, caption="Sample1")
        picture2 = sample_picture(user=self.user, caption="Sample2")
        payload = {"title": "Sample Slideshow", "pictures": [picture1.id, picture2.id]}

        res = self.client.post(SLIDESHOWS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        slideshow = Slideshow.objects.get(id=res.data["id"])
        pictures = slideshow.pictures.all()
        self.assertEqual(pictures.count(), 2)
        self.assertIn(picture1, pictures)
        self.assertIn(picture2, pictures)

    def test_partial_update_slideshow(self):
        """Test updating a slideshow with patch"""
        slideshow = sample_slideshow(user=self.user)
        slideshow.pictures.add(sample_picture(user=self.user))
        new_picture = sample_picture(user=self.user, caption="Sample Picture 2")

        payload = {"title": "Sample Slideshow", "pictures": [new_picture.id]}
        url = detail_url(slideshow.id)
        self.client.patch(url, payload)

        slideshow.refresh_from_db()
        self.assertEqual(slideshow.title, payload["title"])
        pictures = slideshow.pictures.all()
        self.assertEqual(len(pictures), 1)
        self.assertIn(new_picture, pictures)

    def test_full_update_slideshow(self):
        """Test updating a slideshow with put"""
        slideshow = sample_slideshow(user=self.user)
        slideshow.pictures.add(sample_picture(user=self.user))
        payload = {"title": "JT"}
        url = detail_url(slideshow.id)
        self.client.put(url, payload)

        slideshow.refresh_from_db()
        self.assertEqual(slideshow.title, payload["title"])
        pictures = slideshow.pictures.all()
        self.assertEqual(len(pictures), 0)
