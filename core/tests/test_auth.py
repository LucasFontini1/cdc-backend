from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='usuario@example.com', username='nome123', password='UmaSenhaSegura#2026',
        )

    def test_login_with_email(self):
        response = self.client.post('/api/token/', {
            'login': 'usuario@example.com', 'password': 'UmaSenhaSegura#2026',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertIn('access', response.data)

    def test_login_with_username_case_insensitive(self):
        response = self.client.post('/api/token/', {
            'login': 'NOME123', 'password': 'UmaSenhaSegura#2026',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)

    def test_legacy_email_field(self):
        response = self.client.post('/api/token/', {
            'email': 'usuario@example.com', 'password': 'UmaSenhaSegura#2026',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)

    def test_legacy_username_field(self):
        response = self.client.post('/api/token/', {
            'username': 'nome123', 'password': 'UmaSenhaSegura#2026',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)

    def test_wrong_password_fails(self):
        response = self.client.post('/api/token/', {
            'login': 'nome123', 'password': 'senha-errada',
        }, format='json')
        self.assertEqual(response.status_code, 401)

    def test_registration_and_username_required(self):
        response = self.client.post('/api/registro/', {
            'email': 'novo@example.com', 'username': 'novo.user',
            'password': 'UmaSenhaSegura#2026',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn('password', response.data)
        self.assertEqual(User.objects.count(), 2)

    def test_duplicate_username_case_insensitive(self):
        response = self.client.post('/api/registro/', {
            'email': 'outro@example.com', 'username': 'NOME123',
            'password': 'UmaSenhaSegura#2026',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_profile_endpoint_is_private(self):
        self.assertEqual(self.client.get('/api/usuarios/me/').status_code, 401)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/usuarios/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'nome123')

    def test_cannot_patch_another_user(self):
        other = User.objects.create_user(
            email='outra@example.com', username='outra', password='UmaSenhaSegura#2026',
        )
        self.client.force_authenticate(user=self.user)
        result = self.client.patch(f'/api/usuarios/{other.pk}/', {'name': 'Alterado'}, format='json')
        self.assertEqual(result.status_code, 404)
        other.refresh_from_db()
        self.assertNotEqual(other.name, 'Alterado')
