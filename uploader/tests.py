"""Testes dos endpoints de mídia, grupos e validação de arquivos."""
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image as PILImage
from rest_framework.test import APIClient


def make_image(fmt='PNG'):
    buffer = BytesIO()
    PILImage.new('RGB', (8, 8)).save(buffer, format=fmt)
    return SimpleUploadedFile('image.png', buffer.getvalue(), content_type='image/png')


class GroupUploadTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'tester@example.com', username='tester', password='StrongPassword!2026'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def grant_group(self):
        self.user.groups.add(Group.objects.get(name='Uploaders de Mídia'))
        # Permissões Django ficam em cache na instância: use novo usuário como na próxima request JWT.
        self.user = get_user_model().objects.get(pk=self.user.pk)
        self.client.force_authenticate(user=self.user)

    def test_denies_upload_and_listing_without_group(self):
        self.assertEqual(self.client.get('/api/media/images/').status_code, 403)
        self.assertEqual(
            self.client.post('/api/media/images/', {'file': make_image()}, format='multipart').status_code, 403
        )

    def test_accepts_multiple_image_formats(self):
        self.grant_group()
        for fmt in ('PNG', 'JPEG', 'GIF', 'BMP', 'TIFF'):
            with self.subTest(fmt=fmt):
                response = self.client.post(
                    '/api/media/images/', {'file': make_image(fmt)}, format='multipart'
                )
                self.assertEqual(response.status_code, 201, getattr(response, 'data', None))

    def test_video_requires_group(self):
        fake = SimpleUploadedFile('video.mp4', b'example data', content_type='video/mp4')
        with patch('uploader.serializers.video.get_content_type', return_value='video/mp4'):
            self.assertEqual(self.client.post(
                '/api/media/videos/', {'file': fake}, format='multipart'
            ).status_code, 403)
            self.grant_group()
            fake.seek(0)
            response = self.client.post('/api/media/videos/', {'file': fake}, format='multipart')
        self.assertEqual(response.status_code, 201, getattr(response, 'data', None))
        self.assertIn('/media/videos/', response.data['url'])

    def test_rejects_video_with_false_extension(self):
        self.grant_group()
        fake = SimpleUploadedFile('video.mp4', b'<html>not a video</html>', content_type='video/mp4')
        response = self.client.post('/api/media/videos/', {'file': fake}, format='multipart')
        self.assertEqual(response.status_code, 400)
