## Weather Team ADK – Exemplo de orquestrador + sub-agente

Exemplo mínimo com [Google Agent Development Kit (ADK)](https://adk.dev/): um **orquestrador** (`coordinator`) que delega para um **sub-agente** (`weather_agent`), e esse sub-agente chama uma **function tool** que consulta a [Open-Meteo](https://open-meteo.com/) (API pública de clima, sem API key).

### Arquitetura

```text
Usuário
   │
   ▼
adk web / adk run / adk api_server
   │
   ▼
root_agent  (coordinator)     ← orquestrador
   │  sub_agents
   ▼
weather_agent                 ← sub-agente especialista
   │  tools
   ▼
get_weather()                 ← function tool
   │
   ▼
Open-Meteo (geocoding + forecast)
```

### Estrutura principal

- `agents/`
  - Diretório pai passado ao CLI (`adk web agents`). Cada subpasta é um “app” de agente.
- `agents/weather_team/`
  - Pacote do agente. O ADK exige `__init__.py` + `agent.py` com `root_agent`.
- `agents/weather_team/__init__.py`
  - Marca o pacote e importa `agent` para o runtime descobrir o `root_agent`.
- `agents/weather_team/agent.py`
  - Define o sub-agente, o orquestrador e exporta `root_agent`.
- `agents/weather_team/tools.py`
  - Function tool `get_weather` (HTTP para Open-Meteo).
- `requirements.txt`
  - Dependência `google-adk`.
- `Dockerfile` / `docker-compose.yml`
  - Empacota e sobe o `adk api_server` na porta 8080.
- `.env.example`
  - Modelo das variáveis de ambiente (chave Gemini).

### Fluxos típicos

- **Pergunta de clima**: o `coordinator` reconhece o intent e transfere para `weather_agent` → a tool `get_weather` busca dados reais → o sub-agente responde em português.
- **Cumprimento / pergunta geral**: o orquestrador responde sozinho, sem chamar o especialista.
- **Cidade inexistente**: a tool devolve `status: error` e o agente comunica o problema sem inventar temperatura.

---

### Explicação do código

#### `agents/weather_team/__init__.py`

```python
from . import agent
```

O CLI do ADK carrega o pacote do agente. Esse import garante que `agent.py` seja executado e a variável `root_agent` exista no módulo.

#### `agents/weather_team/tools.py` – a tool

| Parte | O que faz |
| --- | --- |
| Assinatura `get_weather(city: str) -> dict` | Tipos claros viram schema da tool para o LLM. |
| Docstring + `Args` / `Returns` | O ADK usa isso como descrição da ferramenta. |
| Geocoding Open-Meteo | Resolve `"Sao Paulo"` → latitude/longitude. |
| Forecast Open-Meteo | Busca `temperature_2m`, umidade e `weather_code`. |
| Retorno `dict` com `status` | Superfície estável: sucesso ou erro sem exception não tratada. |

Não precisa de API key: a Open-Meteo é pública para uso não comercial / fair use.

Quando você passa `tools=[get_weather]` no `Agent`, o ADK envolve a função em uma `FunctionTool` automaticamente.

#### `agents/weather_team/agent.py` – agentes

**Modelo**

```python
MODEL = "gemini-flash-latest"
```

Nome canônico do modelo Gemini usado pelos dois agentes.

**Sub-agente `weather_agent`**

- `name`: identificador interno (usado na delegação).
- `description`: texto que o orquestrador usa para decidir *quando* transferir.
- `instruction`: comportamento do especialista (sempre chamar a tool, falar em PT).
- `tools=[get_weather]`: única ferramenta disponível para ele.

**Orquestrador `root_agent`**

- Nome da variável **obrigatório**: `root_agent` (contrato do `adk web` / `api_server` / `run`).
- `sub_agents=[weather_agent]`: padrão de **delegação LLM** — o coordinator analisa o pedido e transfere o turno ao especialista quando a `description` combina.
- `instruction`: regras de roteamento (clima → `weather_agent`; resto → responde sozinho).

Alternativa (não usada neste exemplo): envolver o sub-agente com `AgentTool` e colocar em `tools=[...]` do root, para invocação explícita como função em vez de transferência de conversa.

---

### Dependências e ambiente

- Python **≥ 3.10** (recomendado 3.12)
- `google-adk>=2.5.0`
- Variáveis:
  - `GOOGLE_API_KEY`: chave do [Google AI Studio](https://aistudio.google.com/apikey)
  - `GOOGLE_GENAI_USE_ENTERPRISE=FALSE`: usa Gemini Developer API (não Vertex)

Copie o exemplo:

```bash
cp .env.example .env
# edite GOOGLE_API_KEY
```

O CLI também aceita `.env` dentro de `agents/weather_team/` se preferir.

---

### Como rodar localmente

1. Crie o ambiente e instale dependências:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure `.env` com `GOOGLE_API_KEY`.

3. Escolha um runtime (sempre a partir da raiz do projeto):

```bash
# Dev UI (navegador) — ótimo para ver delegação e tool calls
adk web agents

# Terminal interativo
adk run agents/weather_team

# API REST (FastAPI embutida, porta 8000 por padrão)
adk api_server agents
```

4. Exemplos de pergunta:

- `Qual a temperatura em São Paulo agora?`
- `Como está o clima em Tokyo?`
- `Oi, tudo bem?` (orquestrador sozinho)

---

### Docker

Build e sobe o `adk api_server` em `http://localhost:8080`:

```bash
# garanta GOOGLE_API_KEY no .env
docker compose up --build
```

Sem Compose:

```bash
docker build -t weather-team-adk .
docker run --rm -p 8080:8080 --env-file .env weather-team-adk
```

O `Dockerfile` instala `google-adk`, copia `agents/` e executa:

```text
adk api_server --host 0.0.0.0 --port 8080 agents
```

Para Dev UI no container, troque o `CMD` por `adk web --host 0.0.0.0 --port ${PORT} agents`.

---

### Referências

- [ADK – site oficial](https://adk.dev/)
- [Multi-agent patterns](https://developers.googleblog.com/en/developers-guide-to-multi-agent-patterns-in-adk/)
- [Open-Meteo API](https://open-meteo.com/en/docs)
