"""Validação por assinatura de arquivo, como no uploader do tutorial."""
import magic

CONTENT_TYPE_JPG = 'image/jpeg'
CONTENT_TYPE_PNG = 'image/png'
CONTENT_TYPE_PDF = 'application/pdf'


def get_content_type(file):
    if hasattr(file, 'temporary_file_path'):
        mime = magic.from_file(file.temporary_file_path(), mime=True)
    else:
        mime = magic.from_buffer(file.read(4096), mime=True)
    if hasattr(file, 'seek'):
        file.seek(0)
    return mime
