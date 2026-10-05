# OCI networking diagnostic app

Private, standard-library Python HTTP endpoint for the three Lab 1 hosts.

| Endpoint | Purpose |
| --- | --- |
| `/` | HTML identifying the responding instance, region, private IP, and request |
| `/json` | The same evidence in JSON |
| `/health` | Fast `ok` response independent of IMDS |

Save `install-metadata-app.sh` and upload it as the instance initialization script / cloud-init user data on Oracle Linux 9. The installer contains the application so no GitHub download is needed during bootstrap. It installs Python, opens TCP 8080 in active firewalld, starts an unprivileged systemd service, and retries a local health check while the service starts.

The host also needs outbound package connectivity and an OCI NSG/security-list rule for the intended source and port. Opening a host port does not grant network access by itself. Keep the endpoint on private IPs; it is a workshop diagnostic application with no authentication.

`metadata_app.py` is the same source embedded in the installer. Its IMDSv2 calls request only instance and VNIC metadata. The response selects display name, region and availability domain; it excludes tenancy/compartment/instance OCIDs and credentials. Outside OCI, the page remains usable with a metadata-unavailable indication. Request header values are escaped in HTML.

Check over Bastion:

```bash
sudo cloud-init status --wait
sudo systemctl status oci-metadata-app --no-pager
curl --fail http://127.0.0.1:8080/health
curl --fail http://127.0.0.1:8080/json
```

For local development, run `PORT=8080 python3 metadata_app.py` in a Bash-compatible shell or set the PORT environment variable in your shell. No additional Python packages are required.
