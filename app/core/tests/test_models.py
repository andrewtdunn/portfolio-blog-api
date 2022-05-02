from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="test@andrewtdunn.com", password="testpass"):
    """Create a sample user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_success(self):
        """Test creating a new user with an email is successful"""
        email = "test@andrewtdunn.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@ANDREWTDUNN.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            "test@andrewtdunn.com", "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(user=sample_user(), name="Music")

        self.assertEqual(str(tag), tag.name)

    def test_picture_str(self):
        """Test the picture representative"""
        picture = models.Picture.objects.create(
            user=sample_user(), caption="Test Caption"
        )
        self.assertEqual(str(picture), picture.caption)

    def test_blog_str(self):
        """Test the blog string representation."""
        blog = models.Blog.objects.create(
            user=sample_user(), title="Sample Title", text="Sample Text"
        )

        self.assertEqual(str(blog), blog.title)

    @patch("uuid.uuid4")
    def test_picture_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.picture_image_file_path(None, "myimage.jpg")

        exp_path = f"uploads/picture/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)

    def test_project_str(self):
        """Test the project string representation."""
        project = models.Project.objects.create(
            user=sample_user(), title="Delta", tagline="major airline migration"
        )
        self.assertEqual(str(project), project.title)

    def test_slideshow_str(self):
        """Test the slideshow string representation."""
        slideshow = models.Slideshow.objects.create(
            user=sample_user(), title="Projects"
        )
        self.assertEqual(str(slideshow), slideshow.title)
