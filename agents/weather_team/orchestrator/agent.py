"""Orquestrador (root) que delega aos sub-agentes."""

from __future__ import annotations

from pathlib import Path

from google.adk import Agent

from ..config import MODEL
from ..sub_agents import weather_agent
from ..utils import load_prompt

_PROMPTS = Path(__file__).resolve().parent / "prompts"

coordinator = Agent(
    name="coordinator",
    model=MODEL,
    description=load_prompt(_PROMPTS / "description.md"),
    instruction=load_prompt(_PROMPTS / "instruction.md"),
    sub_agents=[weather_agent],
)
