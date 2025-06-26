# Sistema de Monitoramento de Ativos B3

Sistema desenvolvido em Django para auxiliar investidores nas decisões de compra/venda de ativos da B3, monitorando cotações e alertando sobre oportunidades de negociação.

## 🚀 Funcionalidades

- **Interface Web Intuitiva**: Configure ativos, túneis de preço e periodicidade
- **Monitoramento Automático**: Obtenção periódica de cotações via API BRAPI
- **Alertas Inteligentes**: Sugestões de compra/venda baseadas em túneis de preço
- **Histórico de Cotações**: Visualização de dados históricos dos ativos
- **Notificações por E-mail**: Alertas automáticos quando há oportunidades

## 📋 Pré-requisitos

- Python 3.8+
- Django 5.2+
- Token da API BRAPI (gratuito)

## 🛠️ Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd desafio-inoa
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o token da API BRAPI**
   
   a. Acesse [https://brapi.dev/](https://brapi.dev/) e obtenha seu token gratuito
   
   b. Edite o arquivo `config.env` e adicione seu token:
   ```env
   BRAPI_TOKEN=seu_token_aqui
   DEBUG=True
   SECRET_KEY=django-insecure-change-this-in-production
   ```

5. **Execute as migrações**
   ```bash
   python manage.py migrate
   ```

6. **Crie um superusuário (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

## 🌐 Acessando o Sistema

- **Interface Principal**: http://localhost:8000/
- **Admin Django**: http://localhost:8000/admin/
- **Testar API**: http://localhost:8000/ativos/testar-api/

## 📊 Como Usar

### 1. Configurar Ativos
- Acesse a interface web
- Clique em "Adicionar Ativo"
- Preencha:
  - **Código**: Ticker do ativo (ex: PETR4)
  - **Nome**: Nome da empresa
  - **Limite Inferior**: Preço mínimo para sugerir compra
  - **Limite Superior**: Preço máximo para sugerir venda
  - **Tipo de Túnel**: Estático, Dinâmico ou Assíncrono
  - **Periodicidade**: Intervalo em minutos para verificação

### 2. Monitorar Cotações
- Use o comando para obter cotações:
  ```bash
  python manage.py obter_cotacoes --todos
  ```
- Ou execute monitoramento periódico:
  ```bash
  python manage.py obter_cotacoes
  ```

### 3. Visualizar Dados
- Acesse a lista de ativos para ver cotações atuais
- Clique no ícone de gráfico para ver histórico
- Use a interface para editar configurações

## 🔧 Comandos Disponíveis

```bash
# Testar API com um ticker específico
python manage.py obter_cotacoes --teste PETR4

# Verificar um ativo específico cadastrado
python manage.py obter_cotacoes --ativo PETR4

# Verificar todos os ativos cadastrados
python manage.py obter_cotacoes --todos

# Executar monitoramento periódico
python manage.py obter_cotacoes
```

## 📁 Estrutura do Projeto

```
desafio-inoa/
├── b3_oportunidades/          # Configurações do projeto Django
├── ativos/                    # App principal
│   ├── models.py             # Modelos de dados
│   ├── views.py              # Views da interface web
│   ├── forms.py              # Formulários
│   ├── services.py           # Integração com API BRAPI
│   ├── monitor.py            # Lógica de monitoramento
│   └── templates/            # Templates HTML
├── config.env                # Configurações de ambiente
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

## 🔌 API BRAPI

O sistema utiliza a API BRAPI (https://brapi.dev/) para obter cotações em tempo real:

- **Endpoint**: `https://brapi.dev/api/quote/{ticker}`
- **Limite**: 1000 requisições/dia (gratuito)
- **Dados**: Preço, variação, volume, market cap
- **Autenticação**: Token Bearer obrigatório

## 🚨 Próximos Passos

- [ ] Implementar sistema de e-mail para alertas
- [ ] Configurar Celery para automação de tarefas
- [ ] Adicionar gráficos e análises técnicas
- [ ] Implementar túneis dinâmicos e assíncronos
- [ ] Adicionar testes automatizados

## 📝 Licença

Este projeto foi desenvolvido como parte de um desafio técnico.

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ usando Django e Python**
