"""Sub-agente especialista em clima."""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent

from ...config import MODEL
from ...utils import load_prompt
from .tools import get_weather

_PROMPTS = Path(__file__).resolve().parent / "prompts"

weather_agent = Agent(
    name="weather_agent",
    model=MODEL,
    description=load_prompt(_PROMPTS / "description.md"),
    instruction=load_prompt(_PROMPTS / "instruction.md"),
    tools=[get_weather],
)
