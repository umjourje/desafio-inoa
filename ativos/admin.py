from django.contrib import admin
from .models import Ativo, TunelPreco, Periodicidade, Cotacao

admin.site.register(Ativo)
admin.site.register(TunelPreco)
admin.site.register(Periodicidade)
admin.site.register(Cotacao)
