# Metadata test app

`metadata_app.py` is a dependency-free diagnostic endpoint for the three workshop instances. It listens on TCP 8080 and renders hostname, private IP, selected OCI instance metadata, and request headers. A backend response therefore proves which instance answered a peering or load-balancer request.

`install-metadata-app.sh` is self-contained cloud-init user data: it installs Python, writes the app, configures a systemd service, and verifies the local endpoint. Use the same script for all three test instances.
