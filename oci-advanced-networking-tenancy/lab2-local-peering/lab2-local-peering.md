# Lab 2: Local Peering with a DRG

## Introduction

Connect the Client and Hub VCNs through a single DRG. Although a local peering gateway works for a two-VCN topology, this workshop uses a DRG because the same routing domain will later attach to a remote region and support transit.

**Time:** 45 minutes

## Task 1: Create the DRG and VCN attachments

In Region A, create `advnet-<initials>-drg-a`. Attach both the Client and Hub VCNs to the DRG. In `client-private-rt`, add `10.20.0.0/16 → Dynamic Routing Gateway`; in `hub-private-rt`, add `10.10.0.0/16 → Dynamic Routing Gateway`.

Open the DRG route-table and attachment views and confirm that the Client attachment imports the Hub CIDR and the Hub attachment imports the Client CIDR. An attachment must not import its own CIDR. This establishes the local DRG path that Lab 4 will later extend to the remote VCN.

## Task 2: Deploy the metadata app to both instances

Create one small flexible Oracle Linux instance in each private app subnet. Provide NAT egress or another package source. Attach the appropriate app NSG. Pass [install-metadata-app.sh](../assets/metadata-app/install-metadata-app.sh) as cloud-init user data (select **Cloud-init script** in the console), or run it on each instance after connecting.

Set a distinct display name for each instance: `client-1` and `hub-1`. The app listens on TCP 8080 and returns its hostname, private address, OCI instance metadata, and request headers.

## Task 3: Test and record expected behavior

From each host, run:

```bash
curl --connect-timeout 5 http://127.0.0.1:8080/
```

Confirm that the page identifies the local host. Then, from `client-1`, request `hub-1` on TCP 8080:

```bash
curl --connect-timeout 10 http://HUB_1_PRIVATE_IP:8080/
```

The response must identify `hub-1`.

> A DRG attachment and a VCN route are required on both sides. Security still applies after routing succeeds. Verify the imported routes in the DRG route tables before diagnosing the application.

**Checkpoint:** Record the two private IP addresses, successful local responses, and one successful Client-to-Hub response.
