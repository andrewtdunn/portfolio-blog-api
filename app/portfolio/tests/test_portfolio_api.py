from portfolio.serializers import ProjectDetailSerializer, ProjectSerializer
from core.models import Project
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from picture.tests.test_slideshows_api import sample_slideshow

PROJECT_URL = reverse("portfolio:project-list")


def detail_url(project_id):
    """Return project detail URL"""
    return reverse("project:project-detail", args=[project_id])


def sample_project(user, **params):
    """Create and return a sample project"""
    defaults = {"title": "Google", "tagline": "tagline"}
    defaults.update(params)

    return Project.objects.create(user=user, **defaults)


class PublicProjectApiTests(TestCase):
    """Test unauthenticted project API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHENTICATED)


class PrivateProjectApiTests(TestCase):
    """Test authenticated project API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create("test@andrewtdunn.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_retrieve_projects(self):
        """Test retrieving a list of projects"""
        sample_project(user=self.user)
        sample_project(user=self.user)

        res = self.client.get(PROJECT_URL)

        projects = Project.objects.all().order_by("-id")
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_projects_limited_to_user(self):
        """Test retrieving projects fro user"""
        user2 = get_user_model().objects.create_user(
            "other@andrewtdunn.com", "testpass"
        )
        sample_project(user=user2)
        sample_project(user=self.user)

        res = self.client.get(PROJECT_URL)

        projects = Project.objects.filter(user=self.user)
        serializer = ProjectSerializer(projects, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_project_detail(self):
        """Test viewing a project detail"""
        project = sample_project(user=self.user)
        project.slideshow = sample_slideshow(user=self.user)

        url = detail_url(project.id)
        res = self.client.get(url)

        serializer = ProjectDetailSerializer(project)
        self.assertEqual(res.data, serializer.data)

    def test_create_project_with_slideshow(self):
        """Test creatign project with slideshow"""
        slideshow1 = sample_slideshow(user=self.user)
        payload = {"title": "Google", "tagline": "tagline one", "slideshow": slideshow1}
        res = self.client.post(PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=res.data["id"])
        slideshow = project.slideshow
        self.assertEqual(slideshow1, slideshow)

    def test_partial_update_blog(self):
        """Test updateing a project with patch"""
        project = sample_project(user=self.user)
        project.slideshow = sample_slideshow(user=self.user, title="Google")
        new_slideshow = sample_slideshow(user=self.user, title="Time Inc")

        payload = {"title": "New title", "slideshow": new_slideshow.id}
        url = detail_url(project.id)
        self.client.put(url, payload)

        project.refresh_from_db()
        self.assertEqual(project.title, payload["title"])

    def test_full_update_blog(self):
        """Test updating a project with put"""
        project = sample_project(user=self.user)
        project.slideshow = sample_slideshow(user=self.user)
        payload = {"title": "Google", "tagline": "test1"}
        url = detail_url(project.id)
        self.client.put(url, payload)

        project.refresh_from_db()
        self.assertEqual(project.title, payload["title"])
        self.assertEqual(project.taglind, payload["tagline"])
        slideshow = project.slideshow
        self.assertEqual(slideshow, None)
