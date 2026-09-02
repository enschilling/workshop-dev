#!/usr/bin/env python3
"""Tiny diagnostic HTTP app for the OCI Advanced Networking workshop."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import socket
from urllib.request import Request, urlopen


def instance_metadata():
    request = Request(
        "http://169.254.169.254/opc/v2/instance/",
        headers={"Authorization": "Bearer Oracle"},
    )
    try:
        with urlopen(request, timeout=2) as response:
            return json.load(response)
    except Exception as error:
        return {"metadataError": str(error)}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        metadata = instance_metadata()
        payload = {
            "hostname": socket.gethostname(),
            "privateIp": socket.gethostbyname(socket.gethostname()),
            "instance": {
                key: metadata.get(key)
                for key in ("displayName", "id", "region", "availabilityDomain", "compartmentId")
                if metadata.get(key)
            },
            "request": {
                "clientAddress": self.client_address[0],
                "xForwardedFor": self.headers.get("X-Forwarded-For"),
                "host": self.headers.get("Host"),
            },
        }
        body = ("<!doctype html><html><head><title>OCI Metadata App</title>"
                "<style>body{font-family:system-ui;margin:3rem;max-width:60rem}pre{background:#f4f4f4;padding:1rem;overflow:auto}</style>"
                "</head><body><h1>OCI Advanced Networking metadata app</h1><pre>" +
                json.dumps(payload, indent=2) + "</pre></body></html>").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


HTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), Handler).serve_forever()
