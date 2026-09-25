#!/usr/bin/env python3
"""
A local server that generates the daily/weekly dashboards natively (see
dashboard.py), so you don't need a Claude session in the loop to see
today's numbers. Meant to be opened as a Chrome app-mode window:

    open -a "Google Chrome" --args --app=http://localhost:8420

Stdlib only, no dependencies beyond openpyxl (already used everywhere
else in this project).
"""

import datetime
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dashboard  # noqa: E402
from effective_date import effective_date  # noqa: E402
from themes import THEMES  # noqa: E402

PORT = 8420


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep stdout quiet; launchd captures it to app/server.log anyway

    def _send(self, html: str, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        theme = qs.get("theme", [None])[0]
        if theme and theme not in THEMES:
            theme = None
        range_key = qs.get("range", ["today"])[0]

        try:
            if parsed.path in ("/", "/daily", "/weekly"):
                # /daily and /weekly are kept as compatibility aliases for
                # anything bookmarked before the range switcher existed.
                if parsed.path == "/daily":
                    range_key = "today"
                elif parsed.path == "/weekly":
                    range_key = "7d"
                end_str = qs.get("date", qs.get("end", [None]))[0]
                if end_str:
                    end = datetime.date.fromisoformat(end_str)
                elif range_key == "yesterday":
                    end = effective_date() - datetime.timedelta(days=1)
                else:
                    end = effective_date()
                self._send(dashboard.render(range_key, end, theme))
            else:
                self._send("<h1>Not found</h1><a href='/'>Home</a>", status=404)
        except Exception as exc:  # noqa: BLE001 - surface it in the page, don't crash the server
            self._send(f"<pre>{type(exc).__name__}: {exc}</pre>", status=500)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Dashboard serving on http://localhost:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
