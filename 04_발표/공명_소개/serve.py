# -*- coding: utf-8 -*-
"""UTF-8 safe static server — GitHub Pages와 같은 루트 배치로 소개 사이트를 연다."""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import mimetypes
import webbrowser

ROOT = Path(__file__).resolve().parent.parent  # 04_발표
INTRO = ROOT / "공명_소개"
STATION = ROOT / "공명스테이션_예시.html"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._serve()

    def do_HEAD(self):
        self._serve(head=True)

    def _serve(self, head=False):
        parsed = urlparse(self.path)
        raw = unquote(parsed.path) or "/"

        # 스테이션
        if raw in ("/station", "/station.html", "/intro/station", "/intro/station.html"):
            return self._send_file(STATION, head)

        # /intro/... 별칭 → 소개 루트
        if raw == "/intro" or raw.startswith("/intro/"):
            rel = raw[len("/intro") :].lstrip("/")
            return self._send_intro(rel, head)

        # GitHub Pages와 동일: 루트 = 소개 폴더
        rel = raw.lstrip("/")
        return self._send_intro(rel, head)

    def _send_intro(self, rel: str, head: bool):
        if not rel or rel.endswith("/"):
            path = INTRO / rel / "index.html" if rel else INTRO / "index.html"
            if path.is_file():
                return self._send_file(path, head)
            # 디렉터리 목록 대신 404
            return self.send_error(404, "File not found")

        # 소개 안 파일 우선
        cand = INTRO / rel
        if cand.is_dir():
            idx = cand / "index.html"
            if idx.is_file():
                return self._send_file(idx, head)
        if cand.is_file():
            return self._send_file(cand, head)

        # 04_발표 하위(소설 md 등) 직접 열기
        outer = ROOT / rel
        if outer.is_dir():
            idx = outer / "index.html"
            if idx.is_file():
                return self._send_file(idx, head)
        if outer.is_file():
            return self._send_file(outer, head)

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
    print(f"Serving intro as site root (like GitHub Pages)")
    print(f"Home:    http://127.0.0.1:{args.port}/")
    print(f"Library: http://127.0.0.1:{args.port}/library.html")
    print(f"Station: http://127.0.0.1:{args.port}/station.html")
    if not args.no_open:
        webbrowser.open(f"http://127.0.0.1:{args.port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
