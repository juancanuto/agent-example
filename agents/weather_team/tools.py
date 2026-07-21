"""Function tools usadas pelos sub-agentes.

Cada função tipada + docstring vira automaticamente uma FunctionTool
no Google ADK quando colocada em `tools=[...]`.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


def get_weather(city: str) -> dict:
    """Consulta o clima atual de uma cidade via Open-Meteo (sem API key).

    Usa a Geocoding API para resolver o nome da cidade em lat/lon e depois
    a Forecast API para obter temperatura e umidade.

    Args:
        city: Nome da cidade (ex.: "Sao Paulo", "London", "Tokyo").

    Returns:
        Dict com status e dados de clima, ou mensagem de erro.
    """
    try:
        geo_params = urllib.parse.urlencode(
            {
                "name": city,
                "count": 1,
                "language": "pt",
                "format": "json",
            }
        )
        with urllib.request.urlopen(
            f"https://geocoding-api.open-meteo.com/v1/search?{geo_params}",
            timeout=10,
        ) as response:
            geo = json.loads(response.read().decode())

        results = geo.get("results") or []
        if not results:
            return {
                "status": "error",
                "error_message": f"Cidade não encontrada: {city}",
            }

        place = results[0]
        latitude = place["latitude"]
        longitude = place["longitude"]
        label = place.get("name", city)

        weather_params = urllib.parse.urlencode(
            {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "timezone": "auto",
            }
        )
        with urllib.request.urlopen(
            f"https://api.open-meteo.com/v1/forecast?{weather_params}",
            timeout=10,
        ) as response:
            forecast = json.loads(response.read().decode())

        current = forecast.get("current") or {}
        return {
            "status": "success",
            "city": label,
            "country": place.get("country"),
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "weather_code": current.get("weather_code"),
        }
    except urllib.error.URLError as exc:
        return {"status": "error", "error_message": f"Falha de rede: {exc}"}
    except Exception as exc:  # noqa: BLE001 — superfície estável para o LLM
        return {"status": "error", "error_message": str(exc)}
