"""Aceita imagens raster reconhecidas pelo Pillow; normaliza formatos incomuns para PNG."""
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from PIL import UnidentifiedImageError
from rest_framework import serializers

from uploader.models import Image

MAX_UPLOAD_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
NATIVE_FORMATS = {'JPEG': '.jpg', 'PNG': '.png', 'GIF': '.gif', 'WEBP': '.webp'}


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['attachment_key', 'file', 'description', 'uploaded_on', 'url']
        read_only_fields = ['attachment_key', 'uploaded_on', 'url']
        extra_kwargs = {'file': {'write_only': True}}

    def validate_file(self, value):
        if value.size <= 0 or value.size > MAX_UPLOAD_SIZE:
            raise serializers.ValidationError('A imagem deve ter no máximo 10 MB.')
        try:
            with PILImage.open(value) as image:
                source_format = image.format
                if not source_format or image.width * image.height > MAX_IMAGE_PIXELS:
                    raise serializers.ValidationError('Imagem inválida ou com dimensões excessivas.')
                image.verify()
            value.seek(0)
            if source_format in NATIVE_FORMATS:
                value.name = f'upload{NATIVE_FORMATS[source_format]}'
                return value
            # BMP, TIFF, ICO, AVIF etc. são convertidos para PNG.
            with PILImage.open(value) as image:
                if getattr(image, 'is_animated', False):
                    raise serializers.ValidationError('Animação nesse formato não é suportada.')
                image.load()
                if image.mode not in ('RGB', 'RGBA'):
                    image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                buffer = BytesIO()
                image.save(buffer, format='PNG')
                if buffer.tell() > MAX_UPLOAD_SIZE:
                    raise serializers.ValidationError('Imagem convertida ultrapassou 10 MB.')
                return SimpleUploadedFile('upload.png', buffer.getvalue(), content_type='image/png')
        except (UnidentifiedImageError, OSError, ValueError, PILImage.DecompressionBombError) as exc:
            raise serializers.ValidationError('Imagem inválida, corrompida ou não reconhecida.') from exc
        finally:
            value.seek(0)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['url', 'description', 'uploaded_on']
        read_only_fields = fields
