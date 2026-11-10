# Setup Quick Call Number

Automação em Python para atualizar o número de discagem rápida (**Quick Call Number**) em dispositivos de intercomunicação via API (ISAPI), utilizando autenticação Digest.

## 🚀 Funcionalidades

- **Atualização em lote**: Suporta múltiplos dispositivos configurados por portas.
- **Atualização completa pós-firmware**: Para leitores Hikvision com firmware recente
  (DS-K1T673DX-BR, DS-K1T671MF-L), o `callNumber` também é alterado em
  `/ISAPI/VideoIntercom/keyCfg/1` e o dispositivo é reiniciado automaticamente após
  a configuração, garantindo que o botão de discagem passe a usar o novo número.
- **Autenticação Digest**: Integração segura com o protocolo ISAPI.
- **Alertas no Slack**: Notificação automática em caso de falha na configuração.
- **CLI Flexível**: Permite definir o número via linha de comando ou variáveis de ambiente.

## 🛠️ Pré-requisitos

- Python >= 3.8
- Dispositivo Intercom com suporte a ISAPI (Ex: Hikvision).

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
INTERCOM_HOST=192.168.1.100
INTERCOM_PORTS=80,81,82
INTERCOM_USER=admin
INTERCOM_PASSWORD=sua_senha
QUICK_CALL_NUMBER=61
SLACK_URL=https://hooks.slack.com/services/seu_webhook
LOG_PATH=app.log

```

## 💻 Como usar

### 1. Instalação

Para uso em produção:

```bash
pip install .

```

Para desenvolvimento (inclui `pytest`, `ruff`, `black`, `pytest-cov`, `requests-mock`, `bandit`):

```bash
pip install -e ".[dev]"

```

### 2. Execução

Você pode executar o script de duas formas:

**Usando o valor padrão do `.env`:**

```bash
setup-intercom

```

**Passando um número específico via argumento:**

```bash
setup-intercom --number 3001

```

## 🧪 Testes

O projeto utiliza `pytest`. Testes unitários usam `requests-mock`; testes de
integração (marcados com `@pytest.mark.integration`) batem em dispositivo real
e são excluídos por padrão.

Rodar testes unitários (default):

```bash
pytest

```

Com cobertura:

```bash
pytest --cov=src --cov-report=term-missing

```

Rodar testes de integração (requer dispositivo real acessível):

```bash
pytest -m integration

```

## 📄 Estrutura do Projeto

- `src/main.py`: Ponto de entrada da aplicação.
- `src/sip_params.py`: Lógica SIP (GET/PUT) e orquestração por dispositivo.
- `src/key_cfg.py`: Cliente ISAPI do keyCfg (configuração do botão de discagem).
- `src/reboot.py`: Cliente ISAPI de reboot do dispositivo.
- `src/utils/helpers.py`: Funções auxiliares (Logs, Slack, Auth, CLI).
- `src/utils/xml_helpers.py`: Parsing e serialização de XML ISAPI.
- `tests/`: Testes unitários (mockados) e de integração (`@pytest.mark.integration`).
- `pyproject.toml`: Gerenciamento de dependências e metadados.
