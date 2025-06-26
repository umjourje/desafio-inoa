import requests
import logging
from decimal import Decimal
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class BRAPIService:
    """Serviço para integração com a API BRAPI"""
    
    BASE_URL = settings.BRAPI_BASE_URL
    
    @classmethod
    def get_quote(cls, ticker: str) -> Optional[Dict]:
        """
        Obtém a cotação atual de um ativo específico
        
        Args:
            ticker: Código do ativo (ex: PETR4)
            
        Returns:
            Dict com dados da cotação ou None se erro
        """
        try:
            url = f"{cls.BASE_URL}/quote/{ticker}"
            
            # Preparar headers com token se disponível
            headers = {}
            if settings.BRAPI_TOKEN:
                headers['Authorization'] = f'Bearer {settings.BRAPI_TOKEN}'
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('results'):
                logger.warning(f"Nenhum resultado encontrado para {ticker}")
                return None
                
            result = data['results'][0]
            
            # Extrair dados relevantes
            quote_data = {
                'ticker': result.get('symbol'),
                'price': Decimal(str(result.get('regularMarketPrice', 0))),
                'change': Decimal(str(result.get('regularMarketChange', 0))),
                'change_percent': Decimal(str(result.get('regularMarketChangePercent', 0))),
                'volume': result.get('regularMarketVolume', 0),
                'market_cap': result.get('marketCap', 0),
                'timestamp': result.get('regularMarketTime', 0)
            }
            
            logger.info(f"Cotação obtida para {ticker}: R$ {quote_data['price']}")
            return quote_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {ticker}: {str(e)}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Erro ao processar dados da API para {ticker}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter cotação para {ticker}: {str(e)}")
            return None
    
    @classmethod
    def get_multiple_quotes(cls, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Obtém cotações de múltiplos ativos de uma vez
        
        Args:
            tickers: Lista de códigos dos ativos
            
        Returns:
            Dict com ticker como chave e dados da cotação como valor
        """
        if not tickers:
            return {}
            
        try:
            # BRAPI aceita múltiplos tickers separados por vírgula
            tickers_str = ','.join(tickers)
            url = f"{cls.BASE_URL}/quote/{tickers_str}"
            
            # Preparar headers com token se disponível
            headers = {}
            if settings.BRAPI_TOKEN:
                headers['Authorization'] = f'Bearer {settings.BRAPI_TOKEN}'
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = {}
            
            if not data.get('results'):
                logger.warning("Nenhum resultado encontrado para os tickers")
                return {ticker: None for ticker in tickers}
            
            # Criar dicionário com resultados
            for result in data['results']:
                ticker = result.get('symbol')
                if ticker:
                    quote_data = {
                        'ticker': ticker,
                        'price': Decimal(str(result.get('regularMarketPrice', 0))),
                        'change': Decimal(str(result.get('regularMarketChange', 0))),
                        'change_percent': Decimal(str(result.get('regularMarketChangePercent', 0))),
                        'volume': result.get('regularMarketVolume', 0),
                        'market_cap': result.get('marketCap', 0),
                        'timestamp': result.get('regularMarketTime', 0)
                    }
                    results[ticker] = quote_data
                    logger.info(f"Cotação obtida para {ticker}: R$ {quote_data['price']}")
            
            # Adicionar None para tickers sem resultado
            for ticker in tickers:
                if ticker not in results:
                    results[ticker] = None
                    logger.warning(f"Nenhum resultado encontrado para {ticker}")
            
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para múltiplos tickers: {str(e)}")
            return {ticker: None for ticker in tickers}
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Erro ao processar dados da API: {str(e)}")
            return {ticker: None for ticker in tickers}
        except Exception as e:
            logger.error(f"Erro inesperado ao obter cotações: {str(e)}")
            return {ticker: None for ticker in tickers}
    
    @classmethod
    def validate_ticker(cls, ticker: str) -> bool:
        """
        Valida se um ticker existe na B3
        
        Args:
            ticker: Código do ativo
            
        Returns:
            True se o ticker é válido, False caso contrário
        """
        quote = cls.get_quote(ticker)
        return quote is not None and quote['price'] > 0 