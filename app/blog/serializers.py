from rest_framework import serializers

from core.models import Tag, Picture


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )


class PictureSerializer(serializers.ModelSerializer):
    """Serializer for a picture object"""

    class Meta:
        model = Picture
        fields = ('id', 'caption')
        read_only_fields = ('id',)
