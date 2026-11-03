"""Permite vídeos por MIME real, não por extensão informada."""
from rest_framework import serializers

from uploader.helpers.files import get_content_type
from uploader.models import Video

MAX_VIDEO_SIZE = 50 * 1024 * 1024
VIDEO_MIME_EXTENSIONS = {
    'video/mp4': '.mp4', 'video/quicktime': '.mov', 'video/webm': '.webm',
    'video/x-matroska': '.mkv', 'video/x-msvideo': '.avi',
    'video/mpeg': '.mpeg', 'video/ogg': '.ogv',
    'video/3gpp': '.3gp', 'video/3gpp2': '.3g2', 'video/x-ms-wmv': '.wmv',
}


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['attachment_key', 'file', 'description', 'uploaded_on', 'url']
        read_only_fields = ['attachment_key', 'uploaded_on', 'url']
        extra_kwargs = {'file': {'write_only': True}}

    def validate_file(self, value):
        if value.size <= 0 or value.size > MAX_VIDEO_SIZE:
            raise serializers.ValidationError('O vídeo deve ter no máximo 50 MB.')
        extension = VIDEO_MIME_EXTENSIONS.get(get_content_type(value))
        if extension is None:
            raise serializers.ValidationError('Formato de vídeo não reconhecido ou não permitido.')
        value.seek(0)
        value.name = f'upload{extension}'
        return value


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['url', 'description', 'uploaded_on']
        read_only_fields = fields
