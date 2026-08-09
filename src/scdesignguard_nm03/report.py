"""Self-contained, escaped HTML report renderer."""

import html
import json
from typing import Any, Dict


def render_html(compiled: Dict[str, Any], result: Dict[str, Any]) -> str:
    esc = lambda value: html.escape(str(value), quote=True)
    rows = "".join(
        f"<tr><td>{esc(row['reason_code'])}</td><td>{esc(row['terminal_state'])}</td><td>{esc(row['definition'])}</td></tr>"
        for row in result["reason_ledger"]
    )
    embedded = html.escape(json.dumps({"compiled": compiled, "result": result}, sort_keys=True), quote=False)
    return """<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>scDesignGuard report</title>
<style>body{font-family:system-ui,sans-serif;margin:2rem;max-width:72rem}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:.45rem;text-align:left}code{background:#eee;padding:.1rem .3rem}</style></head>
<body><h1>scDesignGuard NM03 validity report</h1>
<p>Task: <code>""" + esc(result["task_id"]) + """</code></p>
<p>Terminal state: <strong>""" + esc(result["terminal_state"]) + """</strong></p>
<p>Claim limit: """ + esc(result["claim_limit"]) + """</p>
<table><thead><tr><th>Reason code</th><th>State</th><th>Definition</th></tr></thead><tbody>""" + rows + """</tbody></table>
<p>This report does not certify biological truth and does not authorize scientific execution.</p>
<details><summary>Machine-readable audit object</summary><pre>""" + embedded + """</pre></details></body></html>\n"""

