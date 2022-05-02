from rest_framework import serializers

from core.models import Project, Slideshow


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for a project object"""

    slideshow = serializers.PrimarKeyRelatedField(queryset=Slideshow.objects.all())

    class Meta:
        model = Project
        fields = ("id", "title", "tagline", "slideshow")
