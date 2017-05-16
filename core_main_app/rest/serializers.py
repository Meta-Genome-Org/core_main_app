"""Serializers used throughout the Rest API
"""
from core_main_app.commons.serializers import BasicSerializer
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework.serializers import CharField
from core_main_app.components.template.models import Template
from core_main_app.components.template_version_manager.models import TemplateVersionManager


class TemplateSerializer(DocumentSerializer):
    """
        Template serializer
    """
    class Meta:
        model = Template
        fields = "__all__"


class TemplateVersionManagerSerializer(DocumentSerializer):
    """
        Template Version Manager serializer
    """
    class Meta:
        model = TemplateVersionManager
        fields = "__all__"


class CreateTemplateSerializer(BasicSerializer):
    """
        Template serializer (creation)
    """
    filename = CharField(required=True)
    content = CharField(required=True)

    def create(self, validated_data):
        return Template(**validated_data)


class CreateTemplateVersionManagerSerializer(BasicSerializer):
    """
        Template Version Manager serializer (creation)
    """
    title = CharField(required=True)

    def create(self, validated_data):
        return TemplateVersionManager(**validated_data)