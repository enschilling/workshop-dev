# Lab 3: Remote Peering

## Introduction

Extend the DRG topology to Region B. The remote VCN will host the third metadata app, then become a remote backend in Lab 5.

**Time:** 35 minutes

## Task 1: Create Region B network and DRG

Switch to Region B. Create `advnet-<initials>-remote-vcn` (`10.30.0.0/16`) and a private app subnet (`10.30.10.0/24`). Create a NAT Gateway if the instance needs outbound package installation, and add its default route to the private subnet route table. Create `advnet-<initials>-drg-b` and attach Remote VCN. Add `10.20.0.0/16 → DRG` in the Remote VCN route table and `10.30.0.0/16 → DRG` in `hub-private-rt` in Region A.

## Task 2: Establish the remote peering connection

Create an RPC on each DRG. In the console, peer the Region A RPC to the Region B RPC using the requested peer region and peer RPC OCID. Wait until both RPCs show **Peered**.

Use the DRG route distribution/route-table views to ensure that each VCN attachment can import the other VCN CIDR through the RPC. If you use custom DRG route tables, add explicit static routes or import distributions for `10.20.0.0/16` and `10.30.0.0/16`; do not rely on defaults you have not inspected.

## Task 3: Deploy and test remote-1

Create `remote-1` in the Remote VCN private app subnet, attach the app NSG, and deploy [install-metadata-app.sh](../assets/metadata-app/install-metadata-app.sh). Test locally, then from `hub-1`:

```bash
curl --connect-timeout 10 http://REMOTE_1_PRIVATE_IP:8080/
```

The response must identify `remote-1`. If it fails, check the source VCN route table, both DRG attachments/RPC, the destination VCN route table, and the app NSG—in that order.

**Checkpoint:** Record the RPC OCIDs, the Remote VCN attachment OCID, and one successful Hub-to-Remote response.
