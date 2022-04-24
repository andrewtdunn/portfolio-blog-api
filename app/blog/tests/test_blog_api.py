import tempfile
import os

from PIL import Image

from blog.serializers import BlogDetailSerializer, BlogSerializer
from core.models import Blog, Picture, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

BLOG_URL = reverse('blog:blog-list')


def image_upload_url(picture_id):
    """Return URL for picture image upload"""
    return reverse('blog:picture-upload-image', args=[picture_id])


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

    def test_create_basic_blog(self):
        payload = {
            'title': 'Sample Blog Post',
            'text': 'Sample Blog Text'
        }
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(blog, key))

    def test_create_blog_with_tags(self):
        """Test creating a blog with tags"""
        tag1 = sample_tag(user=self.user, name='music')
        tag2 = sample_tag(user=self.user, name='AI')
        payload = {
            'title': 'Cool New Music',
            'text': 'Some cool bands',
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data['id'])
        tags = blog.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_pictures(self):
        """Test creating blog with pictures"""
        picture1 = sample_picture(user=self.user, caption='Birthday')
        picture2 = sample_picture(user=self.user, caption="New Years")
        payload = {
            'title': 'Party Pictures',
            'text': 'Fun time',
            'pictures': [picture1.id, picture2.id]
        }
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data['id'])
        pictures = blog.pictures.all()
        self.assertEqual(pictures.count(), 2)
        self.assertIn(picture1, pictures)
        self.assertIn(picture2, pictures)

    def test_partial_update_blog(self):
        """Test updating a blog with patch"""
        blog = sample_blog(user=self.user)
        blog.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='fractals')

        payload = {'title': 'The Cure Show', 'tags': [new_tag.id]}
        url = detail_url(blog.id)
        self.client.patch(url, payload)

        blog.refresh_from_db()
        self.assertEqual(blog.title, payload['title'])
        tags = blog.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_blog(self):
        """Test updating a blog with put"""
        blog = sample_blog(user=self.user)
        blog.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Justin Timberlake',
            'text': 'Cool Show'
        }
        url = detail_url(blog.id)
        self.client.put(url, payload)

        blog.refresh_from_db()
        self.assertEqual(blog.title, payload['title'])
        self.assertEqual(blog.text, payload['text'])
        tags = blog.tags.all()
        self.assertEqual(len(tags), 0)


class PictureImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@andrewtdunn.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.picture = sample_picture(user=self.user)

    def tearDown(self):
        self.picture.image.delete()

    def test_upload_image_to_picture(self):
        """Test uploading an image to picture"""
        url = image_upload_url(self.picture.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.picture.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.picture.image.path))

    def test_upload_image_bad_request(self):
        """test uploading an invalid image"""
        url = image_upload_url(self.picture.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_blogs_by_tags(self):
        """Test returning blogs with specific tags"""
        blog1 = sample_blog(user=self.user, title="Bad Brains")
        blog2 = sample_blog(user=self.user, title="Andy Warhol")
        tag1 = sample_tag(user=self.user, name="Music")
        tag2 = sample_tag(user=self.user, name="Art")
        blog1.tags.add(tag1)
        blog2.tags.add(tag2)
        blog3 = sample_blog(user=self.user, title="Ice Cream Sandwich")

        res = self.client.get(
            BLOG_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = BlogSerializer(blog1)
        serializer2 = BlogSerializer(blog2)
        serializer3 = BlogSerializer(blog3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
