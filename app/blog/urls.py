from django.urls import include, path
from rest_framework.routers import DefaultRouter

from blog import views

router = DefaultRouter()
router.register("tags", views.TagViewSet)
router.register("blogs", views.BlogViewSet)

app_name = "blog"

urlpatterns = [path("", include(router.urls))]
