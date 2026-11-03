# Template Django + Django REST Framework + PDM

Backend reutilizável para criar APIs Django com uma estrutura próxima à do template de [Marco André Mendes](https://github.com/marrcandre/template_django_pdm), ampliada com a aplicação **uploader** do [tutorial Django DRF](https://marrcandre.github.io/django-drf-tutorial/), **foto de perfil**, **username único** e autenticação **por e-mail OU username**.

> **Origem:** adaptação educacional da arquitetura de `marrcandre/template_django_pdm`. A app `uploader` mantém a ideia e os endpoints do tutorial (imagens, documentos e `attachment_key`), com validação e restrições de acesso adicionais. Não é uma cópia literal do ZIP disponibilizado pelo autor.

## Tecnologias

Python 3.10+, Django 5.2, DRF, PDM, SimpleJWT, drf-spectacular/Swagger, django-cors-headers, SQLite (desenvolvimento), PostgreSQL (opcional), Cloudinary (opcional), Pillow, python-magic e Ruff.

## 1. Criar um projeto a partir do template privado

Quando este conteúdo estiver num repositório privado do GitHub:

1. Acesse `Settings → General → Template repository` e marque essa opção (requer permissão administrativa).
2. Volte para a página principal do repositório e selecione `Use this template → Create a new repository`.
3. Escolha o nome do novo projeto e a visibilidade. **Um template privado só pode ser usado por quem tem acesso a ele.**
4. Clone o novo repositório e entre na pasta.

Também é possível baixar este pacote e publicá-lo em um repositório privado normal. Para publicar a partir de um terminal Git, veja [Publicar no GitHub](#10-publicar-no-github).

## 2. Preparar o ambiente

Instale **Python**, **PDM** e **Git**. Em seguida:

```bash
pdm install
```

Copie as configurações de ambiente:

```bash
cp .env.example .env
```

No PowerShell, use `Copy-Item .env.example .env`.

Gere uma **SECRET_KEY nova**, que ficará somente no `.env`:

```bash
pdm run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Preencha `SECRET_KEY` no `.env`. Nunca envie o `.env` ao GitHub.

## 3. Banco de dados, migrações e servidor

```bash
pdm run migrate
pdm run createsuperuser
pdm run dev
```

O `createsuperuser` solicita o e-mail, o username e a senha. O servidor fica em `http://127.0.0.1:8000`.

| Recurso | URL |
| --- | --- |
| Admin | `http://127.0.0.1:8000/admin/` |
| Swagger | `http://127.0.0.1:8000/api/doc/` |
| Schema OpenAPI | `http://127.0.0.1:8000/api/schema/` |
| ReDoc | `http://127.0.0.1:8000/api/redoc/` |

> Este template **não inclui banco de dados com usuários ou senhas de demonstração**. Execute as migrações para criar seu banco local.

## 4. Registro e login (e-mail ou username)

### Registrar usuário

**POST** `/api/registro/` — JSON:

```json
{
  "email": "pessoa@example.com",
  "username": "pessoa123",
  "name": "Pessoa Exemplo",
  "password": "UmaSenhaSegura#2026"
}
```

`email` e `username` são obrigatórios e únicos (a verificação desconsidera maiúsculas/minúsculas). O `username` aceita letras, números, ponto, hífen e underscore, mas não `@`. `name` é opcional.

### Fazer login

**POST** `/api/token/` — o mesmo campo `login` aceita e-mail **ou** username:

```json
{ "login": "pessoa@example.com", "password": "UmaSenhaSegura#2026" }
```

ou

```json
{ "login": "pessoa123", "password": "UmaSenhaSegura#2026" }
```

Para manter compatibilidade com integrações existentes, também é possível enviar o campo `email` ou o campo `username` no lugar de `login` (apenas um deles por requisição). Resposta contém `access` e `refresh`. Nas rotas protegidas, adicione o cabeçalho `Authorization: Bearer <access>`.

- **POST** `/api/token/refresh/`: `{ "refresh": "..." }` para renovar o acesso.
- **POST** `/api/token/verify/`: `{ "token": "..." }` para verificar um JWT.

No **Admin do Django**, também é possível entrar com e-mail ou username e senha.

## 5. Foto de perfil com o uploader

A imagem é opcional. O fluxo reproduz o conceito do tutorial: **enviar → receber `attachment_key` → associar ao perfil**.

### 5.1 Enviar imagem

**POST** `/api/media/images/` com autenticação JWT e `multipart/form-data`:

```bash
curl -X POST http://127.0.0.1:8000/api/media/images/ \
  -H 'Authorization: Bearer SEU_ACCESS_TOKEN' \
  -F 'file=@foto.png' \
  -F 'description=Minha foto de perfil'
```

O serviço retorna dados como:

```json
{
  "attachment_key": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "description": "Minha foto de perfil",
  "uploaded_on": "2026-11-03T12:00:00-03:00",
  "url": "/media/images/identificador.png"
}
```

Esse exemplo usa valores ilustrativos. Aceita imagens raster reconhecidas pelo Pillow de até **10 MB** (JPEG, PNG, GIF, WebP e outros formatos suportados como BMP e TIFF). Os formatos fora de JPEG/PNG/GIF/WebP são convertidos para PNG. **SVG não é aceito** por motivos de segurança.

### 5.2 Associar a imagem ao usuário autenticado

**PATCH** `/api/usuarios/me/` com JSON:

```json
{ "foto_attachment_key": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" }
```

Use **a chave real** devolvida pelo upload. A imagem deve pertencer ao usuário autenticado. A resposta contém o objeto `foto` com URL, descrição e data. Envie `{"foto_attachment_key": null}` para remover a associação (não apaga o arquivo).

**GET** `/api/usuarios/me/` retorna `id`, `email`, `username`, `name`, `foto` e outros dados somente da própria conta.

**PATCH** `/api/usuarios/me/` também permite alterar `name` e `username`. E-mail, senha e permissões não podem ser alterados nessa rota. Somente administradores podem listar outros usuários pelo endpoint `/api/usuarios/`.

## 6. Uploader de documentos

**POST** `/api/media/documents/` com `multipart/form-data`, campo `file`, autenticação JWT e PDF de até **10 MB**. A listagem de imagens/documentos mostra apenas os envios do próprio usuário (a equipe administrativa pode ver todos).

## 7. Permissões de grupos, vídeos e Cloudinary

### Permissões dos grupos Django

Após executar `pdm run migrate`, o backend cria automaticamente o grupo **Uploaders de Mídia** com permissões `add` e `view` dos modelos `Image`, `Document` e `Video`.

**Importante:** novos usuários **não** entram automaticamente nesse grupo. Um administrador deve abrir **Admin → Usuários → selecionar usuário → Grupos** e atribuir **Uploaders de Mídia**. Superusuários do Django têm todas as permissões. Sem o grupo (ou permissões individuais equivalentes), uma conta autenticada recebe **403** ao tentar enviar ou listar arquivos; anônimos recebem **401**.

A política global do DRF usa `DjangoModelPermissionsOrAnonReadOnly`: **GET, HEAD e OPTIONS são públicos por padrão** em novos endpoints que utilizam a configuração global; **POST, PUT, PATCH e DELETE** só funcionam para usuários autenticados com as permissões `add`, `change` ou `delete` do modelo concedidas pelo Django Admin, individualmente ou via grupos. Isso permite, por exemplo, que visitantes consultem livros sem login, enquanto apenas membros do grupo autorizado possam cadastrá-los, editá-los ou excluí-los. **Exceções protegidas:** as rotas `/api/usuarios/` e `/api/usuarios/me/` continuam exigindo autenticação (`IsAuthenticated`), e `/api/media/images/`, `/api/media/documents/` e `/api/media/videos/` continuam exigindo JWT e permissões de modelo. O registro e a obtenção de token permanecem públicos apenas nas rotas específicas de cadastro e login.

O uploader usa `MediaModelPermissions`, mais rigorosa: exige também `view_image`, `view_document` ou `view_video` na listagem. Um usuário que possui permissão de leitura vê **apenas os próprios uploads**, exceto usuários da equipe, que podem ver todos caso também tenham permissão `view`.

### Endpoint de vídeos

**POST** `/api/media/videos/` — envio via `multipart/form-data` com campos `file` e `description`, e cabeçalho `Authorization: Bearer SEU_ACCESS_TOKEN`. Valida o tipo real do arquivo (MIME) e aceita vídeos de até **50 MB** nos formatos MP4, MOV, WebM, MKV, AVI, MPEG, OGV, 3GP e WMV.

```bash
curl -X POST http://127.0.0.1:8000/api/media/videos/ \
  -H 'Authorization: Bearer SEU_ACCESS_TOKEN' \
  -F 'file=@video.mp4' \
  -F 'description=Meu vídeo'
```

A resposta contém `attachment_key`, `description`, `uploaded_on` e `url`. Para listar os próprios vídeos, use **GET** `/api/media/videos/` com JWT e permissão `view_video`.

### Armazenamento: local ou Cloudinary

Sem `CLOUDINARY_URL`, imagens, documentos e vídeos ficam em `media/` e são servidos automaticamente **apenas durante o desenvolvimento** (`DEBUG=True`). Não publique `media/` no Git.

Para usar o Cloudinary, defina no `.env` ou nas variáveis do serviço de hospedagem:

```dotenv
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

Em produção, configure também `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, `FRONTEND_URLS`, `DATABASE_URL` e HTTPS. Quando `CLOUDINARY_URL` estiver definido, vídeos usarão `VideoMediaCloudinaryStorage` (tipo **video**), enquanto as imagens e os documentos seguem o backend de mídia padrão. Sem a variável, todos os uploads usam armazenamento local. Os arquivos enviados e os estáticos usam armazenamentos diferentes. Não use o servidor de desenvolvimento nem o serviço local de mídia para produção.

### Exemplo: API de livros pública para leitura e restrita para escrita

Se você criar um `LivroViewSet(ModelViewSet)` com `queryset = Livro.objects.all()` e registrar suas rotas, **sem substituir `permission_classes`**, ele herdará a permissão padrão:

| Método | Visitante sem login | Usuário autenticado sem permissão | Usuário com permissão via grupo |
| --- | --- | --- | --- |
| GET | Permitido | Permitido | Permitido |
| POST | Negado | Negado | Requer `add_livro` |
| PUT/PATCH | Negado | Negado | Requer `change_livro` |
| DELETE | Negado | Negado | Requer `delete_livro` |

A visibilidade dos dados ainda é definida pela implementação do `queryset`: **nunca exponha um modelo com dados pessoais/confidenciais em um endpoint público**. Use `IsAuthenticated` ou uma política mais restritiva em cada view sensível. As permissões globais podem ser substituídas pela própria view.

## 8. Estrutura principal

```text
app/                         # settings, URLs, ASGI e WSGI
core/
  backends.py                # autenticação e-mail ou username
  models/user.py             # usuário customizado, username, foto
  serializers/user.py        # registro, perfil e attachment_key
  views/token.py             # JWT personalizado
  views/user.py              # registro e /usuarios/me/
  migrations/                # migrações do template + novos campos
  tests/                     # testes de autenticação e imagens
uploader/
  models/                    # Image, Document, Video e proprietário
  serializers/               # validação de uploads
  views.py                   # endpoints protegidos
  router.py                  # /api/media/images, /documents e /videos
  migrations/
.env.example
pyproject.toml
README.md
```

## 9. Comandos úteis

| Comando | Ação |
| --- | --- |
| `pdm install` | Instalar dependências |
| `pdm run dev` | Iniciar servidor local |
| `pdm run makemigrations` | Criar migrações após modificar modelos |
| `pdm run migrate` | Aplicar migrações |
| `pdm run test` | Executar testes |
| `pdm run check` | Verificar configuração Django |
| `pdm run format` | Formatar código com Ruff |
| `pdm run lint` | Verificar código com Ruff |
| `pdm run diagram` | Gerar diagrama dos modelos (requer Graphviz) |

O arquivo `pdm.lock` não está incluído neste pacote porque depende da resolução real das dependências. Depois de `pdm install`, faça commit do `pdm.lock` no repositório do seu projeto para garantir versões reproduzíveis. Para deploy com `build.sh`, o PDM instala as dependências de produção.

## 10. Publicar no GitHub

Crie um repositório **vazio e privado** no GitHub, por exemplo `template-django-drf-pdm`. Em seguida, na pasta do template:

```bash
git init
git add .
git commit -m "feat: template Django PDM com uploader e autenticação por email ou username"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/template-django-drf-pdm.git
git push -u origin main
```

Depois, em **Settings → General**, marque **Template repository**. O GitHub exige permissões adequadas para essa configuração. Não selecione `Public`.

## 11. Segurança e adaptações

- O modelo `User` customizado já está configurado por `AUTH_USER_MODEL=core.User`. Defina a identidade do usuário **antes de usar** este template em um banco existente; a troca de modelo de usuário depois de um projeto crescer é complexa.
- Os uploads exigem JWT, permissões dos grupos Django e validação de tamanho/tipo do arquivo. A chave de anexo não é usada como token de autenticação.
- Perfis de outros usuários não são editáveis por contas comuns; os arquivos só podem ser vinculados ao proprietário ou por alguém da equipe.
- A foto de perfil enviada não aparece automaticamente: é preciso vinculá-la pelo `attachment_key`.
- O `username` é obrigatório para novas contas; registros anteriores recebem nomes temporários durante a migração.
- Para produção, ajuste observabilidade, política de retenção, limites de mídia, backups, segurança de infraestrutura, fluxo de alteração de e-mail e recuperação de senha conforme seu projeto.

### Créditos

Arquitetura inspirada em [marrcandre/template_django_pdm](https://github.com/marrcandre/template_django_pdm), com adaptação da [app uploader e seção de foto de perfil do tutorial Django DRF](https://marrcandre.github.io/django-drf-tutorial/). Consulte o projeto original quanto às condições de uso e atribuição antes de redistribuir publicamente.

> **Atenção à privacidade:** as URLs de mídia local e Cloudinary são públicas por padrão. As permissões Django protegem o acesso aos endpoints da API, não impedem o acesso a uma URL de arquivo já conhecida. Para mídia sensível, configure entrega privada e URLs assinadas.
