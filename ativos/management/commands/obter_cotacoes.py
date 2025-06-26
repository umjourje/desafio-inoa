from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from ativos.models import Ativo
from ativos.monitor import MonitoramentoService
from ativos.services import BRAPIService

class Command(BaseCommand):
    help = 'Obtém cotações dos ativos cadastrados via API BRAPI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ativo',
            type=str,
            help='Código do ativo específico para verificar (ex: PETR4)',
        )
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Verificar todos os ativos cadastrados',
        )
        parser.add_argument(
            '--teste',
            type=str,
            help='Testar API com um ticker específico (ex: PETR4)',
        )

    def handle(self, *args, **options):
        if options['teste']:
            self.testar_api(options['teste'])
        elif options['ativo']:
            self.verificar_ativo_especifico(options['ativo'])
        elif options['todos']:
            self.verificar_todos_ativos()
        else:
            self.verificar_ativos_periodicos()

    def testar_api(self, ticker):
        """Testa a API BRAPI com um ticker específico"""
        self.stdout.write(f"Testando API BRAPI para {ticker}...")
        
        try:
            cotacao = BRAPIService.get_quote(ticker)
            
            if cotacao:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Sucesso! {ticker}: R$ {cotacao['price']}"
                    )
                )
                self.stdout.write(f"   Variação: {cotacao['change']} ({cotacao['change_percent']}%)")
                self.stdout.write(f"   Volume: {cotacao['volume']:,}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Falha ao obter cotação para {ticker}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro: {str(e)}")
            )

    def verificar_ativo_especifico(self, codigo):
        """Verifica um ativo específico cadastrado"""
        try:
            ativo = Ativo.objects.get(codigo=codigo)
            self.stdout.write(f"Verificando ativo: {ativo.codigo} - {ativo.nome}")
            
            resultados = MonitoramentoService.monitorar_ativo_especifico(ativo.id)
            
            if resultados:
                for ticker, resultado in resultados.items():
                    if resultado['sucesso']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ {ticker}: R$ {resultado['preco']}"
                            )
                        )
                        if resultado['oportunidade']:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"   🎯 Oportunidade de {resultado['oportunidade']}!"
                                )
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"❌ {ticker}: {resultado['erro']}")
                        )
            else:
                self.stdout.write(self.style.ERROR("Nenhum resultado obtido"))
                
        except Ativo.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Ativo {codigo} não encontrado no banco de dados")
            )

    def verificar_todos_ativos(self):
        """Verifica todos os ativos cadastrados"""
        ativos = Ativo.objects.all()
        
        if not ativos:
            self.stdout.write("Nenhum ativo cadastrado")
            return
        
        self.stdout.write(f"Verificando {ativos.count()} ativos...")
        
        resultados = MonitoramentoService.obter_cotacoes_ativos(ativos)
        
        for ticker, resultado in resultados.items():
            if resultado['sucesso']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {ticker}: R$ {resultado['preco']}"
                    )
                )
                if resultado['oportunidade']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"   🎯 Oportunidade de {resultado['oportunidade']}!"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ {ticker}: {resultado['erro']}")
                )

    def verificar_ativos_periodicos(self):
        """Verifica apenas ativos que precisam ser monitorados baseado na periodicidade"""
        self.stdout.write("Verificando ativos que precisam de monitoramento...")
        
        resumo = MonitoramentoService.executar_monitoramento_periodico()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Monitoramento concluído: {resumo['ativos_verificados']} ativos verificados"
            )
        )
        
        if resumo['oportunidades_encontradas'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"🎯 {resumo['oportunidades_encontradas']} oportunidades encontradas!"
                )
            ) 