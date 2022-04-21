from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Picture

from blog import serializers


class BaseBlogAttrViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    """Base viewset for user owned blog attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseBlogAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class PictureViewSet(BaseBlogAttrViewSet):
    """Manage pictures in the database"""
    queryset = Picture.objects.all()
    serializer_class = serializers.PictureSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(
                        user=self.request.user
                    ).order_by('-caption')
