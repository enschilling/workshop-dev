# Lab 2: Transit Routing

## Introduction

Use the facilitator-provided Remote VCN, DRGs, and remote peering connection to turn the Region A Hub VCN into a deliberate transit point. The Client VCN reaches Remote only when the VCN route tables and DRG import route tables allow it.

**Time:** 40 minutes

## Task 1: Verify the prebuilt baseline

Before making changes, verify that Client and Hub are attached to DRG A, Remote is attached to DRG B, and the DRGs' RPCs are **Peered**. Confirm the private app subnets use the dedicated `client-private-rt` and `hub-private-rt` route tables.

## Task 2: Configure VCN and DRG transit routes

In `client-private-rt`, add or verify these routes:

| Destination | Target |
| --- | --- |
| `10.20.0.0/16` | DRG A |
| `10.30.0.0/16` | DRG A |

In Hub VCN, ensure `hub-private-rt` has `10.10.0.0/16` and `10.30.0.0/16` through DRG A. In Remote VCN, ensure its private-subnet route table has `10.10.0.0/16 → DRG B`.

Configure the DRG route tables so Client imports Hub and Remote CIDRs; Hub imports Client and Remote CIDRs; and each RPC imports the required Client and Hub CIDRs. An attachment must not import its own CIDR.

## Task 3: Validate the paths

From `client-1`, request both application endpoints:

```bash
curl --connect-timeout 10 http://HUB_1_PRIVATE_IP:8080/
curl --connect-timeout 10 http://REMOTE_1_PRIVATE_IP:8080/
```

Both responses must identify the expected host. Run Network Path Analyzer for `client-1 → remote-1`, TCP 8080, and save the successful result.

> Transit routing is an explicit design choice. Keep imported routes and security rules limited to the CIDRs and ports that the shared-service use case requires.
