# -*- coding: utf-8 -*-
"""UTF-8 safe static server for 04_발표 (intro + station)."""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import mimetypes
import webbrowser

ROOT = Path(__file__).resolve().parent.parent  # 04_발표
INTRO = ROOT / "공명_소개"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._serve()

    def do_HEAD(self):
        self._serve(head=True)

    def _serve(self, head=False):
        parsed = urlparse(self.path)
        raw = unquote(parsed.path)

        # root = intro (GitHub Pages와 동일). /intro/ 도 유지.
        if raw in ("/", "/index.html"):
            return self._send_file(INTRO / "index.html", head)

        if raw in ("/station", "/station.html", "/intro/station", "/intro/station.html"):
            return self._send_file(ROOT / "공명스테이션_예시.html", head)

        if raw.startswith("/intro"):
            rel = raw[len("/intro") :].lstrip("/")
            if not rel or rel.endswith("/"):
                path = INTRO / "index.html"
            else:
                path = INTRO / rel
            return self._send_file(path, head)

        # direct UTF-8 paths under 04_발표
        rel = raw.lstrip("/")
        path = ROOT / rel
        if path.is_dir():
            idx = path / "index.html"
            if idx.exists():
                return self._send_file(idx, head)
        if path.is_file():
            return self._send_file(path, head)
        self.send_error(404, "File not found")

    def _send_file(self, path: Path, head=False):
        if not path.exists() or not path.is_file():
            self.send_error(404, "File not found")
            return
        data = path.read_bytes()
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if path.suffix.lower() in {".html", ".css", ".js", ".md"}:
            ctype = {
                ".html": "text/html; charset=utf-8",
                ".css": "text/css; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
                ".md": "text/markdown; charset=utf-8",
            }[path.suffix.lower()]
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving {ROOT}")
    print(f"Intro:   http://127.0.0.1:{args.port}/intro/")
    print(f"Station: http://127.0.0.1:{args.port}/station.html")
    if not args.no_open:
        webbrowser.open(f"http://127.0.0.1:{args.port}/intro/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()