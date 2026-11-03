from rest_framework import serializers

from uploader.helpers.files import CONTENT_TYPE_PDF, get_content_type
from uploader.models import Document

MAX_UPLOAD_SIZE = 10 * 1024 * 1024


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['attachment_key', 'file', 'description', 'uploaded_on', 'url']
        read_only_fields = ['attachment_key', 'uploaded_on', 'url']
        extra_kwargs = {'file': {'write_only': True}}

    def validate_file(self, value):
        if value.size > MAX_UPLOAD_SIZE or get_content_type(value) != CONTENT_TYPE_PDF:
            raise serializers.ValidationError('Envie um arquivo PDF válido de até 10 MB.')
        value.name = 'upload.pdf'
        return value


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['url', 'description', 'uploaded_on']
        read_only_fields = fields
