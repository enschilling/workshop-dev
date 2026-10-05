# OCI Advanced Networking

This is the canonical workshop folder for ongoing development. The customer path builds a private OCI hub-and-spoke, adds Bastion access, and troubleshoots it with Network Command Center.

Launch the LiveLabs viewer through [workshops/tenancy/index.html](workshops/tenancy/index.html); its [manifest](workshops/tenancy/manifest.json) defines the sequence:

1. OCI Hub-and-Spoke: local and remote VCN peering.
2. Secure Access: OCI Bastion.
3. Troubleshooting: Network Command Center.
4. Optional cross-tenancy local peering challenge.
5. Optional OCI–Azure multicloud connectivity.
6. Optional referral to OCI Network Firewall Common Use Cases, LiveLabs workshop 3872.
7. Cleanup.

Labs 1–3 are independent of the optional extensions. Read the Introduction for timing, IAM, resource ownership, and the common address plan.

Consolidation retains this workshop's detailed material and diagrams and incorporates the sibling tenancy workshop's address-planning format, two sanitized screenshots, diagnostic app, connectivity discussion, and cross-tenancy IAM challenge. The sibling `oci-advanced-networking-tenancy` folder is retained as a historical source; edit this folder going forward.

The original lab directories were renamed to match their new sequence. Network Path Analyzer exercises use the same-region Ashburn path; RPC paths are verified with routes, peering status, and live application traffic. The dedicated firewall procedure lives in the linked specialist workshop.

For a local preview, serve the repository over HTTP and open the viewer rather than using a `file://` URL. The LiveLabs viewer also requires access to Oracle's shared JavaScript and CSS assets.
