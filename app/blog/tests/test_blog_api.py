from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Blog, Tag, Picture
from blog.serializers import BlogSerializer, BlogDetailSerializer


BLOG_URL = reverse('blog:blog-list')


def detail_url(blog_id):
    """Return blog detail URL"""
    return reverse('blog:blog-detail', args=[blog_id])


def sample_tag(user, name='Music'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_picture(user, caption='portrait'):
    """Create and return a sample picture"""
    return Picture.objects.create(user=user, caption=caption)


def sample_blog(user, **params):
    """Create and return a sample blog"""
    defaults = {
        'title': 'Sample title',
        'text': 'This is the sample text.'
    }
    defaults.update(params)

    return Blog.objects.create(user=user, **defaults)


class PublicBlogApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BLOG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBlogApiTests(TestCase):
    """Test Unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@andrewtdunn.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_blogs(self):
        """Test retrieving a list of blogs"""
        sample_blog(user=self.user)
        sample_blog(user=self.user)

        res = self.client.get(BLOG_URL)

        blogs = Blog.objects.all().order_by('-id')
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_blogs_limited_to_user(self):
        """Test retrieving blogs for user"""
        user2 = get_user_model().objects.create_user(
            'other@andrewtdunn.com',
            'password123'
        )
        sample_blog(user=user2)
        sample_blog(user=self.user)

        res = self.client.get(BLOG_URL)

        blogs = Blog.objects.filter(user=self.user)
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_blog_detail(self):
        """Test viewing a blog detail"""
        blog = sample_blog(user=self.user)
        blog.tags.add(sample_tag(user=self.user))
        blog.pictures.add(sample_picture(user=self.user))

        url = detail_url(blog.id)
        res = self.client.get(url)

        serializer = BlogDetailSerializer(blog)
        self.assertEqual(res.data, serializer.data)
