from django.db import models

# Create your models here.

class Ativo(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class TunelPreco(models.Model):
    TIPO_CHOICES = [
        ("estatico", "Estático"),
        ("dinamico", "Dinâmico"),
        ("assincrono", "Assíncrono"),
    ]
    ativo = models.OneToOneField(Ativo, on_delete=models.CASCADE, related_name="tunel")
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2)
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="estatico")

    def __str__(self):
        return f"Túnel de {self.ativo.codigo} ({self.tipo})"

class Periodicidade(models.Model):
    ativo = models.OneToOneField(Ativo, on_delete=models.CASCADE, related_name="periodicidade")
    minutos = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.ativo.codigo}: {self.minutos} min"

class Cotacao(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE, related_name="cotacoes")
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ativo.codigo} - {self.preco} em {self.data_hora}"
