"""Verifica leitura anônima por padrão e escrita via permissões de grupos Django."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from uploader.models import Image


class ExampleCollectionView(APIView):
    """Endpoint fictício, usado somente nos testes (não registrado em urls.py)."""

    queryset = Image.objects.none()

    def get(self, request):
        return Response({'results': []})

    def post(self, request):
        return Response({'created': True}, status=201)

    def put(self, request):
        return Response({'updated': True})

    def patch(self, request):
        return Response({'updated': True})

    def delete(self, request):
        return Response(status=204)


class DefaultPermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ExampleCollectionView.as_view()
        self.user = get_user_model().objects.create_user(
            email='leitor@example.com',
            username='leitor',
            password='SenhaSegura#2026',
        )

    def request_as_user(self, method, user=None):
        request = getattr(self.factory, method)('/somente-para-testes/livros/')
        if user is not None:
            force_authenticate(request, user=user)
        return self.view(request)

    def test_unauthenticated_get_is_public(self):
        self.assertEqual(self.request_as_user('get').status_code, 200)

    def test_unauthenticated_write_is_blocked(self):
        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                self.assertEqual(self.request_as_user(method).status_code, 401)

    def test_authenticated_without_permissions_cannot_write(self):
        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                self.assertEqual(self.request_as_user(method, self.user).status_code, 403)

    def test_group_with_add_permission_can_create_but_not_edit(self):
        group = Group.objects.create(name='Editores de conteúdo de teste')
        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(Image),
            codename='add_image',
        )
        group.permissions.add(permission)
        self.user.groups.add(group)
        # Limpa o cache de permissões obtendo outra instância de usuário.
        user = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(self.request_as_user('post', user).status_code, 201)
        self.assertEqual(self.request_as_user('put', user).status_code, 403)
        self.assertEqual(self.request_as_user('patch', user).status_code, 403)
        self.assertEqual(self.request_as_user('delete', user).status_code, 403)

    def test_private_existing_endpoints_stay_protected(self):
        client = APIClient()
        self.assertEqual(client.get('/api/usuarios/me/').status_code, 401)
        for path in ('images', 'documents', 'videos'):
            with self.subTest(path=path):
                self.assertEqual(client.get(f'/api/media/{path}/').status_code, 401)
