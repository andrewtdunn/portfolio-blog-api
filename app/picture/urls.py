from django.urls import include, path
from rest_framework.routers import DefaultRouter

from picture import views

router = DefaultRouter()
router.register("picture", views.PictureViewSet)
router.register("slideshow", views.SlideshowViewSet)

app_name = "picture"

urlpatterns = [path("", include(router.urls))]
