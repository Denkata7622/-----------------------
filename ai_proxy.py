#!/usr/bin/env python3
"""ai_proxy.py — локален сървър за сайта + прокси към Hack Club AI API.
Решава CORS проблема при file:// като сервира всичко от http://localhost:8000.

Стартиране:
    python ai_proxy.py
После отвори:
    http://localhost:8000/index.html
"""
import json
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from http.server import ThreadingHTTPServer
import requests

API_URL = 'https://ai.hackclub.com/proxy/v1/chat/completions'
API_KEY = 'sk-hc-v1-34cc3c13c2629d51060697b428993eb61bee4ba1e8ae412a7f50639014974ef7'
PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def log_message(self, fmt, *args):
        # Тихо — не спамим конзолата
        pass

    def copyfile(self, source, outputfile):
        """Override за да хванем ConnectionAbortedError при затворен таб / F5."""
        try:
            super().copyfile(source, outputfile)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # Browser-ът затвори връзката — нормално, не е грешка
            pass

    def do_GET(self):
        # Блокирай .bak / .tmp / backups / __pycache__ / .git
        path = self.path.split('?', 1)[0].lower()
        if (path.endswith(('.bak', '.tmp', '.pyc')) or
            '/backups/' in path or '/__pycache__/' in path or '/.git/' in path):
            self.send_response(404)
            self.end_headers()
            return
        try:
            super().do_GET()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def do_POST(self):
        if self.path != '/api/chat':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        # Model allowlist (за production — ако сайтът е публичен)
        ALLOWED_MODELS = {
            'z-ai/glm-5.3-flash', 'deepseek/deepseek-v3.2',
            'openai/gpt-oss-120b', 'openai/gpt-6.1-sol',
            'openai/gpt-6.1-sol-pro',
        }
        try:
            req_data = json.loads(body)
            req_model = req_data.get('model', '')
            if req_model not in ALLOWED_MODELS:
                self.send_response(403)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': f'Model "{req_model}" not allowed'
                }).encode())
                return
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error":"Invalid JSON"}')
            return

        try:
            r = requests.post(
                API_URL,
                headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json',
                },
                data=body,
                timeout=300,
            )
            self.send_response(r.status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                self.wfile.write(r.content)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass
        except requests.Timeout:
            try:
                self.send_response(504)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'AI моделът отне твърде дълго (timeout 300s). Опитай с по-кратък въпрос.'
                }).encode())
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass
        except requests.RequestException as e:
            try:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'AI API грешка: {e}'}).encode())
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass
        except Exception as e:
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e) or 'Unknown error'}).encode())
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Всеки request в отделен thread — браузърът праща паралелни заявки."""
    daemon_threads = True
    allow_reuse_address = True


if __name__ == '__main__':
    print()
    print('═' * 55)
    print(f'  Отвори:  http://localhost:{PORT}/index.html')
    print(f'  Спри:    Ctrl+C')
    print('═' * 55)
    print()
    server = ThreadedHTTPServer(('127.0.0.1', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nСпирам...')