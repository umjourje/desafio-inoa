from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lista/', views.lista_ativos, name='lista_ativos'),
    path('adicionar/', views.adicionar_ativo, name='adicionar_ativo'),
    path('editar/<int:ativo_id>/', views.editar_ativo, name='editar_ativo'),
    path('excluir/<int:ativo_id>/', views.excluir_ativo, name='excluir_ativo'),
    path('cotacoes/<int:ativo_id>/', views.visualizar_cotacoes, name='visualizar_cotacoes'),
    path('testar-api/', views.testar_api, name='testar_api'),
    path('executar-monitoramento/', views.executar_monitoramento, name='executar_monitoramento'),
    path('enviar-email-teste/', views.enviar_email_teste, name='enviar_email_teste'),
    path('api/cotacao/', views.obter_cotacao_ajax, name='obter_cotacao_ajax'),
] 