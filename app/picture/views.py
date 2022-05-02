from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Picture, Slideshow
from picture import serializers


class PictureViewSet(viewsets.ModelViewSet):
    """Manage pictures in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Picture.objects.all()
    serializer_class = serializers.PictureSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-caption")

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == "upload_image":
            return serializers.PictureImageSerializer

        if self.action == "retrieve":
            return serializers.PictureDetailSerializer

        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a picture"""
        picture = self.get_object()
        serializer = self.get_serializer(picture, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SlideshowViewSet(viewsets.ModelViewSet):
    """Manage pictures in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Slideshow.objects.all()
    serializer_class = serializers.SlideshowSerializer

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-title")
