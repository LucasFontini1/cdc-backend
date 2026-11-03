from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage
from rest_framework.test import APIClient

User = get_user_model()


def png_file():
    memory = BytesIO()
    PILImage.new('RGB', (2, 2), color='green').save(memory, format='PNG')
    return SimpleUploadedFile('photo.png', memory.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT='/tmp/django-pdm-template-test-media')
class PhotoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('user@example.com', username='user', password='UmaSenhaSegura#2026')
        self.other = User.objects.create_user('other@example.com', username='other', password='UmaSenhaSegura#2026')

        group = Group.objects.get(name='Uploaders de Mídia')
        self.user.groups.add(group)
        self.other.groups.add(group)

    def test_photo_upload_and_association(self):
        self.client.force_authenticate(user=self.user)
        upload = self.client.post('/api/media/images/', {'file': png_file()}, format='multipart')
        self.assertEqual(upload.status_code, 201, getattr(upload, 'data', None))
        response = self.client.patch('/api/usuarios/me/', {
            'foto_attachment_key': upload.data['attachment_key'],
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIsNotNone(response.data['foto'])
        self.assertIn('/media/', response.data['foto']['url'])

    def test_cannot_use_photo_of_other_user(self):
        self.client.force_authenticate(user=self.other)
        uploaded = self.client.post('/api/media/images/', {'file': png_file()}, format='multipart')
        self.assertEqual(uploaded.status_code, 201)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/usuarios/me/', {
            'foto_attachment_key': uploaded.data['attachment_key'],
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_upload_fails(self):
        response = self.client.post('/api/media/images/', {'file': png_file()}, format='multipart')
        self.assertEqual(response.status_code, 401)
