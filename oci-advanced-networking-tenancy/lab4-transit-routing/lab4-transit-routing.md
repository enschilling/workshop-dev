# Lab 4: Transit Routing

## Introduction

Make Region A a hub-and-spoke network. Client VCN will attach to DRG A and reach the Remote VCN via Hub/DRG A and the RPC. The route tables are the design: every CIDR must have a deliberate next hop on both sides of each traffic flow.

**Time:** 40 minutes

## Task 1: Attach Client VCN

Attach Client VCN to DRG A. In `client-private-rt`, add:

| Destination | Target |
| --- | --- |
| `10.20.0.0/16` | DRG A |
| `10.30.0.0/16` | DRG A |

In Hub VCN, ensure `hub-private-rt` has routes to both `10.10.0.0/16` and `10.30.0.0/16` through DRG A. In Remote VCN, add `10.10.0.0/16 → DRG B`. Associate the updated route tables with the private subnets, not just the VCN defaults.

## Task 2: Configure DRG transit policy

Open DRG A route tables and attachments. Use a route-table design that allows:

* Client VCN attachment to import the Hub and Remote VCN CIDRs.
* Hub VCN attachment to import Client and Remote VCN CIDRs.
* RPC attachment to import Client and Hub VCN CIDRs.

On DRG B, the RPC attachment must import the Client CIDR, and the Remote VCN attachment must import the Client CIDR through the RPC. If you use route distributions, inspect the resulting routes after the attachments are associated. An attachment must not import its own CIDR.

## Task 3: Validate the paths

From `client-1`, run:

```bash
curl --connect-timeout 10 http://HUB_1_PRIVATE_IP:8080/
curl --connect-timeout 10 http://REMOTE_1_PRIVATE_IP:8080/
```

Both requests should succeed. Use Network Path Analyzer for `client-1 → remote-1`, TCP 8080, and keep its result as your evidence. If a path fails, compare the source subnet route table, source DRG import route, RPC route, destination VCN route table, and app NSG.

> Transit routing is not a default consequence of peering. It is enabled only when the relevant VCN and DRG route tables permit it. Keep route domains and CIDRs narrowly scoped in production.

**Checkpoint:** Save a topology screenshot or Path Analyzer result showing Client-to-Remote TCP 8080 as reachable.
