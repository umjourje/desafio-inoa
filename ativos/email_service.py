import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class EmailService:
    """Serviço para envio de e-mails"""
    
    @classmethod
    def enviar_notificacao_oportunidade(cls, ativo: str, preco: float, tipo_oportunidade: str, 
                                       limite_inferior: float = None, limite_superior: float = None,
                                       destinatarios: List[str] = None) -> bool:
        """
        Envia e-mail de notificação sobre oportunidade de compra/venda
        
        Args:
            ativo: Código do ativo
            preco: Preço atual
            tipo_oportunidade: 'compra' ou 'venda'
            limite_inferior: Limite inferior do túnel
            limite_superior: Limite superior do túnel
            destinatarios: Lista de e-mails destinatários
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            if not destinatarios:
                # Usar e-mail padrão se não especificado
                destinatarios = [settings.EMAIL_HOST_USER] if settings.EMAIL_HOST_USER else []
            
            if not destinatarios:
                logger.warning("Nenhum destinatário configurado para envio de e-mail")
                return False
            
            # Preparar dados do e-mail
            assunto = f"🎯 Oportunidade de {tipo_oportunidade.upper()} - {ativo}"
            
            # Renderizar template HTML
            context = {
                'ativo': ativo,
                'preco': preco,
                'tipo_oportunidade': tipo_oportunidade,
                'limite_inferior': limite_inferior,
                'limite_superior': limite_superior,
            }
            
            html_message = render_to_string('ativos/email_oportunidade.html', context)
            plain_message = render_to_string('ativos/email_oportunidade.txt', context)
            
            # Enviar e-mail
            send_mail(
                subject=assunto,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"E-mail de oportunidade enviado para {ativo}: {tipo_oportunidade}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de oportunidade: {str(e)}")
            return False
    
    @classmethod
    def enviar_relatorio_diario(cls, resumo: Dict, destinatarios: List[str] = None) -> bool:
        """
        Envia relatório diário de monitoramento
        
        Args:
            resumo: Dicionário com resumo das atividades
            destinatarios: Lista de e-mails destinatários
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            if not destinatarios:
                destinatarios = [settings.EMAIL_HOST_USER] if settings.EMAIL_HOST_USER else []
            
            if not destinatarios:
                logger.warning("Nenhum destinatário configurado para envio de relatório")
                return False
            
            assunto = "📊 Relatório Diário - Monitoramento B3"
            
            context = {
                'resumo': resumo,
                'data': resumo.get('data', ''),
            }
            
            html_message = render_to_string('ativos/email_relatorio.html', context)
            plain_message = render_to_string('ativos/email_relatorio.txt', context)
            
            send_mail(
                subject=assunto,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info("Relatório diário enviado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório diário: {str(e)}")
            return False
    
    @classmethod
    def enviar_email_teste(cls, destinatario: str) -> bool:
        """
        Envia e-mail de teste para verificar configuração
        
        Args:
            destinatario: E-mail do destinatário
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Validar destinatário
            if not destinatario or not destinatario.strip():
                logger.error("Destinatário vazio ou inválido")
                return False
            
            # Validar configurações de e-mail
            if not settings.EMAIL_HOST_USER:
                logger.error("EMAIL_HOST_USER não configurado")
                return False
            
            if not settings.EMAIL_HOST_PASSWORD:
                logger.error("EMAIL_HOST_PASSWORD não configurado")
                return False
            
            # Usar EMAIL_HOST_USER como remetente se DEFAULT_FROM_EMAIL não estiver configurado
            from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
            
            if not from_email:
                logger.error("Nenhum e-mail de origem configurado")
                return False
            
            assunto = "🧪 Teste de Configuração - Sistema B3"
            
            context = {
                'mensagem': 'Este é um e-mail de teste para verificar se a configuração de e-mail está funcionando corretamente.',
            }
            
            html_message = render_to_string('ativos/email_teste.html', context)
            plain_message = render_to_string('ativos/email_teste.txt', context)
            
            logger.info(f"Tentando enviar e-mail de teste para {destinatario} de {from_email}")
            
            send_mail(
                subject=assunto,
                message=plain_message,
                from_email=from_email,
                recipient_list=[destinatario],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"E-mail de teste enviado para {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de teste: {str(e)} para {destinatario}")
            return False 