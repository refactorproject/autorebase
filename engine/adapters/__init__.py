"""Adapters entrypoint.

Each adapter implements a common protocol with graceful fallbacks when
external tools are unavailable.
"""

from . import text_generic, json_cfg, yaml_cfg, c_cpp, dtsi

__all__ = [
    "text_generic",
    "json_cfg",
    "yaml_cfg",
    "c_cpp",
    "dtsi",
]

