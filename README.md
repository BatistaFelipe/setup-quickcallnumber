# Setup Quick Call Number

Automação em Python para atualizar o número de discagem rápida (**Quick Call Number**) em dispositivos de intercomunicação via API (ISAPI), utilizando autenticação Digest.

## 🚀 Funcionalidades

- **Atualização em lote**: Suporta múltiplos dispositivos configurados por portas.
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

```bash
pip install .

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

O projeto utiliza `pytest` para validação das chamadas de API. Para rodar:

```bash
pytest

```

## 📄 Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação.
- `sip_params.py`: Lógica de comunicação com a API ISAPI (GET/PUT).
- `utils/helpers.py`: Funções auxiliares (Logs, Slack, Auth, CLI).
- `pyproject.toml`: Gerenciamento de dependências e metadados.
