from django.urls import path, include
from rest_framework.routers import DefaultRouter

from blog import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('pictures', views.PictureViewSet)
router.register('blogs', views.BlogViewSet)

app_name = 'blog'

urlpatterns = [
    path('', include(router.urls))
]
