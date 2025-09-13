from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jinja2 import Template
from jsonschema import validate as jsonschema_validate

from .utils import write_json


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Auto-Rebase Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    .ok { color: #0a0; }
    .warn { color: #ca0; }
    .bad { color: #a00; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f0f0f0; }
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 12px; }
  </style>
  </head>
<body>
  <h1>Auto-Rebase Report</h1>
  <p>Run ID: {{ run_id }}</p>
  <h2>Summary</h2>
  <ul>
    <li>Auto-merged: {{ summary.auto }}</li>
    <li>Semantic: {{ summary.semantic }}</li>
    <li>Conflicts: {{ summary.conflicts }}</li>
  </ul>
  <h2>Files</h2>
  <table>
    <thead><tr><th>File</th><th>Status</th><th>Details</th><th>Req IDs</th></tr></thead>
    <tbody>
    {% for f in files %}
      <tr>
        <td>{{ f.file }}</td>
        <td>{{ f.status }}</td>
        <td>{{ f.details }}</td>
        <td>{{ ','.join(f.req_ids) }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <h2>Validation</h2>
  <p>Status: {% if validation.success %}<span class="ok">PASS</span>{% else %}<span class="bad">FAIL</span>{% endif %}</p>
  <ul>
    {% for i in validation.issues %}
      <li>[{{ i.level }}] {{ i.file_path }} - {{ i.message }}</li>
    {% endfor %}
  </ul>
  <h2>Tool Availability</h2>
  <ul>
    {% for k, v in tools.items() %}
      <li>{{ k }}: {{ v }}</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def generate(run_id: str, outcomes: Dict[str, Any], validation: Dict[str, Any], tools: Dict[str, Any], report_json_path: Path, report_html_path: Path, schema: Dict[str, Any]) -> None:
    """Generate report.json and report.html and validate JSON against schema."""

    report = {"run_id": run_id, "summary": outcomes.get("summary", {}), "files": outcomes.get("files", []), "validation": validation, "tools": tools}
    jsonschema_validate(report, schema)
    write_json(report_json_path, report)
    html = Template(HTML_TEMPLATE).render(**report)
    report_html_path.parent.mkdir(parents=True, exist_ok=True)
    report_html_path.write_text(html, encoding="utf-8")

