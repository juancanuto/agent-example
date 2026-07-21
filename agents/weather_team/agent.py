"""Ponto de entrada do ADK: exporta `root_agent`.

O `adk web` / `adk api_server` / `adk run` esperam esta variável global.
"""

from .orchestrator import coordinator

root_agent = coordinator
