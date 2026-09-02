# Lab 2: Local Peering with a DRG

## Introduction

Connect the Client and Hub VCNs through a single DRG. Although a local peering gateway works for a two-VCN topology, this workshop uses a DRG because the same routing domain will later attach to a remote region and support transit.

**Time:** 45 minutes

## Task 1: Create the DRG and VCN attachments

In Region A, create `advnet-<initials>-drg-a`. Attach Hub VCN to the DRG and select `hub-private-rt` as the VCN route-table association. In `hub-private-rt`, add route `10.10.0.0/16 → Dynamic Routing Gateway`.

For this lab, use the Client VCN as the client-side test network but do not attach it to the DRG until Lab 4. Instead, create `client-1` in the Client VCN and `hub-1` in the Hub VCN; validate each app locally. This preserves the central lesson of Lab 4: a hub attachment does not automatically make an unrelated spoke a transit participant.

## Task 2: Deploy the metadata app to both instances

Create one small flexible Oracle Linux instance in each private app subnet. Provide NAT egress or another package source. Attach the appropriate app NSG. Pass [install-metadata-app.sh](../assets/metadata-app/install-metadata-app.sh) as cloud-init user data (select **Cloud-init script** in the console), or run it on each instance after connecting.

Set a distinct display name for each instance: `client-1` and `hub-1`. The app listens on TCP 8080 and returns its hostname, private address, OCI instance metadata, and request headers.

## Task 3: Test and record expected behavior

From each host, run:

```bash
curl --connect-timeout 5 http://127.0.0.1:8080/
```

Confirm that the page identifies the local host. From `client-1`, a request to `hub-1` on TCP 8080 should fail now: there is intentionally no Client-to-Hub network path. This is a useful baseline; do not “fix” it until Lab 4.

> A DRG attachment and a VCN route are both required for the Hub side. Security still applies after routing succeeds. If you later add a Client attachment, also verify imported routes in the DRG route tables.

**Checkpoint:** Record the two private IP addresses and a successful local `curl` response from each host.
