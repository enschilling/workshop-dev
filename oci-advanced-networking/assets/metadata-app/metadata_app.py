#!/usr/bin/env python3
"""Private diagnostic endpoint for the OCI Advanced Networking workshop."""
import html
import json
import os
import socket
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen

_CACHE = {"time": 0, "instance": {}, "vnics": [], "status": "unavailable"}


def metadata():
    if time.monotonic() - _CACHE["time"] < 30:
        return _CACHE
    try:
        results = []
        for endpoint in ("instance/", "vnics/"):
            request = Request(
                "http://169.254.169.254/opc/v2/" + endpoint,
                headers={"Authorization": "Bearer Oracle"},
            )
            with urlopen(request, timeout=2) as response:
                results.append(json.load(response))
        _CACHE.update(instance=results[0], vnics=results[1], status="available")
    except Exception:
        _CACHE.update(instance={}, vnics=[], status="unavailable")
    _CACHE["time"] = time.monotonic()
    return _CACHE


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.partition("?")[0]
        if path == "/health":
            self.respond(200, "text/plain", b"ok\n")
            return
        if path not in ("/", "/json"):
            self.respond(404, "text/plain", b"not found\n")
            return
        md = metadata()
        instance = md["instance"]
        try:
            private_ip = md["vnics"][0]["privateIp"]
        except (IndexError, KeyError, TypeError):
            try:
                private_ip = socket.gethostbyname(socket.gethostname())
            except OSError:
                private_ip = "unavailable"
        payload = {
            "hostname": socket.gethostname(),
            "privateIp": private_ip,
            "instance": {
                key: instance.get(key)
                for key in ("displayName", "region", "availabilityDomain")
                if instance.get(key)
            },
            "metadataStatus": md["status"],
            "request": {
                "clientAddress": self.client_address[0],
                "xForwardedFor": self.headers.get("X-Forwarded-For"),
                "host": self.headers.get("Host"),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if path == "/json":
            self.respond(200, "application/json", json.dumps(payload, indent=2).encode())
            return
        name = html.escape(str(instance.get("displayName") or payload["hostname"]))
        region = html.escape(str(instance.get("region") or "Metadata unavailable"))
        ip = html.escape(str(private_ip))
        details = html.escape(json.dumps(payload, indent=2))
        page = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OCI Networking Diagnostic</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;margin:0;background:#f4f6f8;color:#172b3a}
main{max-width:850px;margin:48px auto;padding:0 24px}
.label{font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:#52616b}
h1{font-size:30px;line-height:1.2;margin:12px 0 24px}
.cards{display:flex;gap:16px;flex-wrap:wrap}
.card{background:white;border:1px solid #dce3e7;border-radius:10px;padding:18px;flex:1;min-width:180px}
.card span{display:block;color:#52616b;font-size:13px;margin-bottom:5px}
pre{background:#172b3a;color:#e5f2f7;border-radius:10px;padding:20px;overflow:auto;font-size:13px}
a{color:#006d77}footer{color:#52616b;font-size:13px}
</style></head><body><main><div class="label">OCI Advanced Networking</div>
<h1>""" + name + """</h1><div class="cards"><div class="card"><span>Responding region</span>
""" + region + """</div><div class="card"><span>Private IP</span>""" + ip + """</div></div>
<h2>Request evidence</h2><pre>""" + details + """</pre>
<footer>Private workshop diagnostic endpoint. <a href="/json">JSON</a> ·
<a href="/health">Health check</a>. Forwarded headers are observations, not trusted identity.</footer>
</main></body></html>"""
        self.respond(200, "text/html", page.encode())

    def respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), Handler).serve_forever()
