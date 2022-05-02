from rest_framework import serializers

from core.models import Picture, Slideshow


class PictureSerializer(serializers.ModelSerializer):
    """Serializer for a picture object"""

    class Meta:
        model = Picture
        fields = ("id", "caption", "image")
        read_only_fields = ("id",)


class PictureImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to Picture"""

    class Meta:
        model = Picture
        fields = ("id", "image")
        read_only_fields = ("id",)


class PictureDetailSerializer(serializers.ModelSerializer):
    """Serializer for a single picture object"""

    class Meta:
        model = Picture
        fields = ("id", "caption", "image")
        read_only_fields = ("id",)


class SlideshowSerializer(serializers.ModelSerializer):
    """Serializer for a slideshow object"""

    pictures = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Picture.objects.all()
    )

    class Meta:
        model = Slideshow
        fields = ("id", "title", "pictures")
