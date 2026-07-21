"""Equipe ADK: orquestrador + sub-agente de clima.

O `adk web` / `adk api_server` / `adk run` esperam uma variável global
chamada `root_agent` neste módulo.
"""

from __future__ import annotations

from google.adk import Agent

from .tools import get_weather

MODEL = "gemini-flash-latest"


# ---------------------------------------------------------------------------
# Sub-agente especialista
# ---------------------------------------------------------------------------

weather_agent = Agent(
    name="weather_agent",
    model=MODEL,
    description=(
        "Especialista em clima. Use para perguntas sobre temperatura, "
        "umidade ou condições do tempo em uma cidade."
    ),
    instruction=(
        "Você é o especialista em clima. "
        "Sempre use a tool get_weather para obter dados reais. "
        "Responda de forma concisa em português, citando cidade e temperatura. "
        "Se a tool falhar, explique o erro sem inventar números."
    ),
    tools=[get_weather],
)


# ---------------------------------------------------------------------------
# Orquestrador (root_agent) — delega via sub_agents
# ---------------------------------------------------------------------------

root_agent = Agent(
    name="coordinator",
    model=MODEL,
    description="Orquestrador que roteia pedidos ao especialista de clima.",
    instruction=(
        "Você coordena uma equipe pequena. "
        "Para clima, tempo, temperatura ou umidade, delegue ao sub-agente "
        "weather_agent. "
        "Para cumprimentos ou perguntas gerais, responda você mesmo. "
        "Nunca invente dados de clima."
    ),
    sub_agents=[weather_agent],
)
