from blog.serializers import BlogDetailSerializer, BlogSerializer
from core.models import Blog, Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from picture.tests.test_pictures_api import sample_picture

BLOG_URL = reverse("blog:blog-list")


def detail_url(blog_id):
    """Return blog detail URL"""
    return reverse("blog:blog-detail", args=[blog_id])


def sample_tag(user, name="Music"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_blog(user, **params):
    """Create and return a sample blog"""
    defaults = {"title": "Sample title", "text": "This is the sample text."}
    defaults.update(params)

    return Blog.objects.create(user=user, **defaults)


class PublicBlogApiTests(TestCase):
    """Test authenticated blog API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(BLOG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBlogApiTests(TestCase):
    """Test authenticated blog API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@andrewtdunn.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_blogs(self):
        """Test retrieving a list of blogs"""
        sample_blog(user=self.user)
        sample_blog(user=self.user)

        res = self.client.get(BLOG_URL)

        blogs = Blog.objects.all().order_by("-id")
        serializer = BlogSerializer(blogs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_blogs_limited_to_user(self):
        """Test retrieving blogs for user"""
        user2 = get_user_model().objects.create_user(
            "other@andrewtdunn.com", "password123"
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
        payload = {"title": "Sample Blog Post", "text": "Sample Blog Text"}
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(blog, key))

    def test_create_blog_with_tags(self):
        """Test creating a blog with tags"""
        tag1 = sample_tag(user=self.user, name="music")
        tag2 = sample_tag(user=self.user, name="AI")
        payload = {
            "title": "Cool New Music",
            "text": "Some cool bands",
            "tags": [tag1.id, tag2.id],
        }
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data["id"])
        tags = blog.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_blog_with_pictures(self):
        """Test creating blog with pictures"""
        picture1 = sample_picture(user=self.user, caption="Birthday")
        picture2 = sample_picture(user=self.user, caption="New Years")
        payload = {
            "title": "Party Pictures",
            "text": "Fun time",
            "pictures": [picture1.id, picture2.id],
        }
        res = self.client.post(BLOG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        blog = Blog.objects.get(id=res.data["id"])
        pictures = blog.pictures.all()
        self.assertEqual(pictures.count(), 2)
        self.assertIn(picture1, pictures)
        self.assertIn(picture2, pictures)

    def test_partial_update_blog(self):
        """Test updating a blog with patch"""
        blog = sample_blog(user=self.user)
        blog.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="fractals")

        payload = {"title": "The Cure Show", "tags": [new_tag.id]}
        url = detail_url(blog.id)
        self.client.patch(url, payload)

        blog.refresh_from_db()
        self.assertEqual(blog.title, payload["title"])
        tags = blog.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_blog(self):
        """Test updating a blog with put"""
        blog = sample_blog(user=self.user)
        blog.tags.add(sample_tag(user=self.user))
        payload = {"title": "Justin Timberlake", "text": "Cool Show"}
        url = detail_url(blog.id)
        self.client.put(url, payload)

        blog.refresh_from_db()
        self.assertEqual(blog.title, payload["title"])
        self.assertEqual(blog.text, payload["text"])
        tags = blog.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_blogs_by_tags(self):
        """Test returning blogs with specific tags"""
        blog1 = sample_blog(user=self.user, title="Bad Brains")
        blog2 = sample_blog(user=self.user, title="Andy Warhol")
        tag1 = sample_tag(user=self.user, name="Music")
        tag2 = sample_tag(user=self.user, name="Art")
        blog1.tags.add(tag1)
        blog2.tags.add(tag2)
        blog3 = sample_blog(user=self.user, title="Ice Cream Sandwich")

        res = self.client.get(BLOG_URL, {"tags": f"{tag1.id},{tag2.id}"})

        serializer1 = BlogSerializer(blog1)
        serializer2 = BlogSerializer(blog2)
        serializer3 = BlogSerializer(blog3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_search_blog_by_title(self):
        """Test searching blog by title"""
        blog1 = sample_blog(user=self.user, title="REM")
        blog2 = sample_blog(user=self.user, title="Andy Warhol")

        res = self.client.get(BLOG_URL, {"search": "REM"})
        serializer1 = BlogSerializer(blog1)
        serializer2 = BlogSerializer(blog2)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_search_blog_by_text(self):
        """Test searching blog by text"""
        blog1 = sample_blog(
            user=self.user, title="Birds", text="The jayhawk is a cool bird."
        )
        blog2 = sample_blog(
            user=self.user, title="Birds", text="The eagle is a cool bird"
        )

        res = self.client.get(BLOG_URL, {"search": "jayhawk"})

        serializer1 = BlogSerializer(blog1)
        serializer2 = BlogSerializer(blog2)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_search_blog_by_tag(self):
        """Test searching blog by tag name"""
        blog1 = sample_blog(user=self.user)
        blog2 = sample_blog(user=self.user)
        tag1 = sample_tag(user=self.user, name="Music")
        blog1.tags.add(tag1)

        res = self.client.get(BLOG_URL, {"search": "Music"})
        serializer1 = BlogSerializer(blog1)
        serializer2 = BlogSerializer(blog2)
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
