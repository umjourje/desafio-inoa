import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.utils import timezone
from .models import Ativo, Cotacao, TunelPreco
from .services import BRAPIService
from .email_service import EmailService

logger = logging.getLogger(__name__)

class MonitoramentoService:
    """Serviço para monitoramento de ativos e verificação de oportunidades"""
    
    @classmethod
    def obter_cotacoes_ativos(cls, ativos: List[Ativo] = None) -> Dict[str, Dict]:
        """
        Obtém cotações para uma lista de ativos
        
        Args:
            ativos: Lista de ativos para monitorar. Se None, monitora todos
            
        Returns:
            Dict com resultados do monitoramento
        """
        if ativos is None:
            ativos = Ativo.objects.all()
        
        if not ativos:
            logger.info("Nenhum ativo para monitorar")
            return {}
        
        # Extrair códigos dos ativos
        tickers = [ativo.codigo for ativo in ativos]
        logger.info(f"Obtendo cotações para {len(tickers)} ativos: {', '.join(tickers)}")
        
        # Obter cotações da API
        cotacoes_api = BRAPIService.get_multiple_quotes(tickers)
        
        resultados = {}
        
        for ativo in ativos:
            ticker = ativo.codigo
            cotacao_api = cotacoes_api.get(ticker)
            
            if cotacao_api and cotacao_api['price'] > 0:
                # Salvar cotação no banco
                cotacao = Cotacao.objects.create(
                    ativo=ativo,
                    preco=cotacao_api['price']
                )
                
                # Verificar oportunidades
                oportunidade = cls.verificar_oportunidade(ativo, cotacao_api['price'])
                
                # Enviar e-mail se houver oportunidade
                if oportunidade:
                    cls.enviar_notificacao_oportunidade(ativo, cotacao_api['price'], oportunidade)
                
                resultados[ticker] = {
                    'sucesso': True,
                    'preco': cotacao_api['price'],
                    'cotacao_id': cotacao.id,
                    'oportunidade': oportunidade,
                    'timestamp': cotacao_api.get('timestamp')
                }
                
                logger.info(f"Ativo {ticker}: R$ {cotacao_api['price']} - {oportunidade}")
                
            else:
                resultados[ticker] = {
                    'sucesso': False,
                    'erro': 'Cotação não disponível',
                    'preco': None
                }
                logger.warning(f"Falha ao obter cotação para {ticker}")
        
        return resultados
    
    @classmethod
    def verificar_oportunidade(cls, ativo: Ativo, preco: float) -> Optional[str]:
        """
        Verifica se há oportunidade de compra ou venda baseada no túnel de preço
        
        Args:
            ativo: Ativo a ser verificado
            preco: Preço atual do ativo
            
        Returns:
            'compra', 'venda' ou None se não há oportunidade
        """
        try:
            tunel = ativo.tunel
            if not tunel:
                return None
            
            if preco <= tunel.limite_inferior:
                return 'compra'
            elif preco >= tunel.limite_superior:
                return 'venda'
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao verificar oportunidade para {ativo.codigo}: {str(e)}")
            return None
    
    @classmethod
    def enviar_notificacao_oportunidade(cls, ativo: Ativo, preco: float, tipo_oportunidade: str):
        """
        Envia notificação por e-mail sobre oportunidade
        
        Args:
            ativo: Ativo com oportunidade
            preco: Preço atual
            tipo_oportunidade: 'compra' ou 'venda'
        """
        try:
            tunel = ativo.tunel
            if not tunel:
                return
            
            EmailService.enviar_notificacao_oportunidade(
                ativo=ativo.codigo,
                preco=preco,
                tipo_oportunidade=tipo_oportunidade,
                limite_inferior=tunel.limite_inferior,
                limite_superior=tunel.limite_superior
            )
            
            logger.info(f"Notificação de {tipo_oportunidade} enviada para {ativo.codigo}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação para {ativo.codigo}: {str(e)}")
    
    @classmethod
    def monitorar_ativo_especifico(cls, ativo_id: int) -> Dict:
        """
        Monitora um ativo específico
        
        Args:
            ativo_id: ID do ativo
            
        Returns:
            Dict com resultado do monitoramento
        """
        try:
            ativo = Ativo.objects.get(id=ativo_id)
            return cls.obter_cotacoes_ativos([ativo])
        except Ativo.DoesNotExist:
            logger.error(f"Ativo com ID {ativo_id} não encontrado")
            return {}
    
    @classmethod
    def obter_ativos_para_monitoramento(cls) -> List[Ativo]:
        """
        Obtém lista de ativos que devem ser monitorados baseado na periodicidade
        
        Returns:
            Lista de ativos que precisam ser verificados
        """
        agora = timezone.now()
        ativos_para_verificar = []
        
        for ativo in Ativo.objects.all():
            try:
                # Verificar se tem periodicidade configurada
                if not hasattr(ativo, 'periodicidade'):
                    continue
                
                periodicidade = ativo.periodicidade
                ultima_cotacao = ativo.cotacoes.first()
                
                # Se nunca teve cotação, incluir na verificação
                if not ultima_cotacao:
                    ativos_para_verificar.append(ativo)
                    continue
                
                # Calcular se já passou tempo suficiente desde a última verificação
                tempo_desde_ultima = agora - ultima_cotacao.data_hora
                tempo_minimo = timedelta(minutes=periodicidade.minutos)
                
                if tempo_desde_ultima >= tempo_minimo:
                    ativos_para_verificar.append(ativo)
                    
            except Exception as e:
                logger.error(f"Erro ao verificar periodicidade do ativo {ativo.codigo}: {str(e)}")
        
        return ativos_para_verificar
    
    @classmethod
    def executar_monitoramento_periodico(cls) -> Dict:
        """
        Executa o monitoramento periódico de todos os ativos
        
        Returns:
            Dict com resumo da execução
        """
        logger.info("Iniciando monitoramento periódico")
        
        ativos_para_verificar = cls.obter_ativos_para_monitoramento()
        
        if not ativos_para_verificar:
            logger.info("Nenhum ativo precisa ser verificado no momento")
            return {
                'total_ativos': 0,
                'ativos_verificados': 0,
                'oportunidades_encontradas': 0
            }
        
        logger.info(f"Verificando {len(ativos_para_verificar)} ativos")
        
        resultados = cls.obter_cotacoes_ativos(ativos_para_verificar)
        
        # Contar oportunidades
        oportunidades = sum(
            1 for resultado in resultados.values() 
            if resultado.get('oportunidade') in ['compra', 'venda']
        )
        
        resumo = {
            'total_ativos': len(ativos_para_verificar),
            'ativos_verificados': len([r for r in resultados.values() if r.get('sucesso')]),
            'oportunidades_encontradas': oportunidades,
            'resultados': resultados
        }
        
        logger.info(f"Monitoramento concluído: {resumo['ativos_verificados']} ativos verificados, {oportunidades} oportunidades encontradas")
        
        return resumo 