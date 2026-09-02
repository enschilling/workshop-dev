# Cleanup

## Introduction

Remove all resources tagged `workshop=oci-advanced-networking` in reverse dependency order. Deleting a VCN or DRG before its dependent resources will fail. Confirm that no shared or pre-existing resource has the workshop tag before deletion.

## Cleanup order

1. Delete the private load balancer after recording its final backend state.
2. Terminate `client-1`, `hub-1`, and `remote-1`; release any reserved public IP addresses not used elsewhere.
3. Delete the remote peering connections, then detach Remote VCN and Client/Hub VCN attachments from their DRGs.
4. Delete both DRGs only after their attachments and RPCs are gone.
5. Delete NSGs, then route tables after removing route rules and subnet associations.
6. Delete NAT and Internet Gateways, then subnets and VCNs in Region B and Region A.

## Verify

In each region, filter Networking, Compute, and Load Balancer resources by the workshop tag/prefix. Confirm that no workshop resource remains and that any billable load-balancer capacity has been released.

> Do not delete a gateway, DRG, VCN, or security policy that existed before the workshop or is shared with another workload.
