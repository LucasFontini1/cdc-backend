from django.db import models

from uploader.models import Image

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem = models.ForeignKey(Image, on_delete=models.CASCADE)