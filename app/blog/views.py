from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Picture, Blog

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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(blog__isnull=False)
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class PictureViewSet(BaseBlogAttrViewSet):
    """Manage pictures in the database"""
    queryset = Picture.objects.all()
    serializer_class = serializers.PictureSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(
                        user=self.request.user
                    ).order_by('-caption')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'upload_image':
            return serializers.PictureImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a picture"""
        picture = self.get_object()
        serializer = self.get_serializer(
            picture,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class BlogViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    search_fields = ['title', 'text', 'tags__name']
    filter_backends = (filters.SearchFilter,)
    serializer_class = serializers.BlogSerializer
    queryset = Blog.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the blogs for the authenticated user"""
        tags = self.request.query_params.get('tags')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.BlogDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Blog"""
        serializer.save(user=self.request.user)
