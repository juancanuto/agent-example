"""Configuração compartilhada do app weather_team."""

import os

MODEL = os.getenv("MODEL", "gemini-flash-latest")
