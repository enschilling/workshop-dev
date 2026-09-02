#!/bin/bash
# Cloud-init user-data script for Oracle Linux. Requires outbound package access.
set -euo pipefail

dnf -y install python3
install -d -m 0755 /opt/oci-metadata-app
python3 - <<'PY'
from pathlib import Path
Path('/opt/oci-metadata-app/metadata_app.py').write_text('''from http.server import BaseHTTPRequestHandler, HTTPServer
import json, socket
from urllib.request import Request, urlopen

def metadata():
    try:
        return json.load(urlopen(Request("http://169.254.169.254/opc/v2/instance/", headers={"Authorization":"Bearer Oracle"}), timeout=2))
    except Exception as error:
        return {"metadataError": str(error)}

class App(BaseHTTPRequestHandler):
    def do_GET(self):
        md = metadata()
        data = {"hostname": socket.gethostname(), "privateIp": socket.gethostbyname(socket.gethostname()),
                "instance": {k: md.get(k) for k in ("displayName", "region", "availabilityDomain", "compartmentId") if md.get(k)},
                "request": {"clientAddress": self.client_address[0], "xForwardedFor": self.headers.get("X-Forwarded-For"), "host": self.headers.get("Host")}}
        body = ("<!doctype html><title>OCI Metadata App</title><style>body{font-family:system-ui;margin:3rem}pre{background:#f4f4f4;padding:1rem}</style><h1>OCI Advanced Networking metadata app</h1><pre>" + json.dumps(data, indent=2) + "</pre>").encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, fmt, *args): print(fmt % args)
HTTPServer(("0.0.0.0", 8080), App).serve_forever()
''')
PY
cat >/etc/systemd/system/oci-metadata-app.service <<'UNIT'
[Unit]
Description=OCI workshop metadata diagnostic app
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/oci-metadata-app/metadata_app.py
Restart=on-failure
User=nobody

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now oci-metadata-app
curl -fsS http://127.0.0.1:8080/ >/dev/null
