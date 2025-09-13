from __future__ import annotations

from jsonschema import validate as jsonschema_validate


def validate_json(data: dict, schema: dict) -> None:
    jsonschema_validate(data, schema)

