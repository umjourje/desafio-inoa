from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Ativo, TunelPreco, Periodicidade, Cotacao
from .forms import AtivoForm
from .services import BRAPIService
from .monitor import MonitoramentoService
from .email_service import EmailService

def home(request):
    """Página inicial com resumo do sistema"""
    # Estatísticas básicas
    total_ativos = Ativo.objects.count()
    total_cotacoes = Cotacao.objects.count()
    ativos_com_tunel = TunelPreco.objects.count()
    
    # Últimas cotações
    ultimas_cotacoes = Cotacao.objects.select_related('ativo').order_by('-data_hora')[:5]
    
    context = {
        'total_ativos': total_ativos,
        'total_cotacoes': total_cotacoes,
        'ativos_com_tunel': ativos_com_tunel,
        'ultimas_cotacoes': ultimas_cotacoes,
    }
    
    return render(request, 'ativos/home.html', context)

def lista_ativos(request):
    ativos = Ativo.objects.all()
    return render(request, 'ativos/lista_ativos.html', {'ativos': ativos})

def adicionar_ativo(request):
    if request.method == 'POST':
        form = AtivoForm(request.POST)
        if form.is_valid():
            ativo = form.save()
            messages.success(request, f'Ativo {ativo.codigo} adicionado com sucesso!')
            return redirect('lista_ativos')
    else:
        form = AtivoForm()
    
    return render(request, 'ativos/form_ativo.html', {'form': form, 'titulo': 'Adicionar Ativo'})

def editar_ativo(request, ativo_id):
    ativo = get_object_or_404(Ativo, id=ativo_id)
    if request.method == 'POST':
        form = AtivoForm(request.POST, instance=ativo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ativo {ativo.codigo} atualizado com sucesso!')
            return redirect('lista_ativos')
    else:
        form = AtivoForm(instance=ativo)
    
    return render(request, 'ativos/form_ativo.html', {'form': form, 'titulo': 'Editar Ativo'})

def visualizar_cotacoes(request, ativo_id):
    ativo = get_object_or_404(Ativo, id=ativo_id)
    cotacoes = ativo.cotacoes.all().order_by('-data_hora')[:50]  # Últimas 50 cotações
    return render(request, 'ativos/cotacoes.html', {'ativo': ativo, 'cotacoes': cotacoes})

def excluir_ativo(request, ativo_id):
    ativo = get_object_or_404(Ativo, id=ativo_id)
    if request.method == 'POST':
        ativo.delete()
        messages.success(request, f'Ativo {ativo.codigo} excluído com sucesso!')
        return redirect('lista_ativos')
    return render(request, 'ativos/confirmar_exclusao.html', {'ativo': ativo})

def testar_api(request):
    """View para testar a API BRAPI"""
    resultado = None
    ticker = None
    
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '').strip().upper()
        if ticker:
            try:
                resultado = BRAPIService.get_quote(ticker)
                if resultado:
                    messages.success(request, f'Cotação obtida para {ticker}: R$ {resultado["price"]}')
                else:
                    messages.error(request, f'Falha ao obter cotação para {ticker}')
            except Exception as e:
                messages.error(request, f'Erro ao conectar com API: {str(e)}')
    
    return render(request, 'ativos/testar_api.html', {
        'resultado': resultado,
        'ticker': ticker
    })

def executar_monitoramento(request):
    """View para executar monitoramento manualmente"""
    if request.method == 'POST':
        resumo = MonitoramentoService.executar_monitoramento_periodico()
        
        if resumo['ativos_verificados'] > 0:
            messages.success(
                request, 
                f'Monitoramento executado: {resumo["ativos_verificados"]} ativos verificados'
            )
            
            if resumo['oportunidades_encontradas'] > 0:
                messages.warning(
                    request,
                    f'🎯 {resumo["oportunidades_encontradas"]} oportunidades encontradas!'
                )
        else:
            messages.info(request, 'Nenhum ativo precisava ser verificado no momento')
    
    return redirect('lista_ativos')

def enviar_email_teste(request):
    """View para enviar e-mail de teste"""
    if request.method == 'POST':
        # Debug: verificar todos os dados POST
        print("DEBUG: Dados POST recebidos:", request.POST)
        
        email = request.POST.get('email', '').strip()
        print("DEBUG: E-mail capturado:", repr(email))
        
        if not email:
            messages.error(request, 'E-mail é obrigatório')
            return redirect('home')
        
        # Validar formato do e-mail
        if '@' not in email or '.' not in email:
            messages.error(request, 'Formato de e-mail inválido')
            return redirect('home')
        
        try:
            sucesso = EmailService.enviar_email_teste(email)
            if sucesso:
                messages.success(request, f'E-mail de teste enviado para {email}')
            else:
                messages.error(request, 'Falha ao enviar e-mail de teste')
        except Exception as e:
            print("DEBUG: Erro ao enviar e-mail:", str(e))
            messages.error(request, f'Erro ao enviar e-mail: {str(e)}')
    else:
        messages.error(request, 'Método não permitido')
    
    return redirect('home')

@csrf_exempt
def obter_cotacao_ajax(request):
    """Endpoint AJAX para obter cotação de um ativo específico"""
    if request.method == 'POST':
        ticker = request.POST.get('ticker', '').strip().upper()
        if ticker:
            cotacao = BRAPIService.get_quote(ticker)
            if cotacao:
                return JsonResponse({
                    'sucesso': True,
                    'ticker': ticker,
                    'preco': str(cotacao['price']),
                    'variacao': str(cotacao['change']),
                    'variacao_percentual': str(cotacao['change_percent'])
                })
            else:
                return JsonResponse({
                    'sucesso': False,
                    'erro': f'Falha ao obter cotação para {ticker}'
                })
    
    return JsonResponse({'sucesso': False, 'erro': 'Requisição inválida'})
