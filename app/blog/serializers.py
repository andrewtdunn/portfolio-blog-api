from rest_framework import serializers

from core.models import Tag, Picture, Blog


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class PictureSerializer(serializers.ModelSerializer):
    """Serializer for a picture object"""

    class Meta:
        model = Picture
        fields = ('id', 'caption')
        read_only_fields = ('id',)


class BlogSerializer(serializers.ModelSerializer):
    """Serializer for a blog object"""
    pictures = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Picture.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Blog
        fields = ('id', 'title', 'text', 'pictures', 'tags')
        read_only_fields = ('id',)


class BlogDetailSerializer(BlogSerializer):
    """Serialize the blog detail"""
    pictures = PictureSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
