# Introduction

## About this Workshop

Build a working OCI network in stages: establish the VCN foundation, connect two VCNs through a DRG, extend the topology to a second region, enable controlled transitive routing, and publish the application through a private load balancer. Every test workload serves the same small metadata page, so each routing change has an obvious, verifiable result.

This is a **Tenancy-only** workshop. It assumes the attendee can create networking and compute resources in a chosen compartment. It does not use a managed sandbox.

## Target topology

```text
Region A
  Client VCN (10.10.0.0/16) -- DRG -- Hub VCN (10.20.0.0/16)
                                           |
                                      Private LB :80
                                           |
Region B                              remote DRG peering
  Remote VCN (10.30.0.0/16) ------------ DRG
```

Three small Oracle Linux instances run the metadata app: `client-1` in Client VCN, `hub-1` in Hub VCN, and `remote-1` in Remote VCN. The Client VCN is intentionally attached to the DRG only in Lab 4, so attendees can observe the difference between ordinary attachment routing and explicit transit design.

| Lab | Outcome | Estimate |
| --- | --- | --- |
| 1 | Core VCN, subnet, gateway, route, security list, and NSG configuration | 45 min |
| 2 | Same-region DRG connectivity and two app instances | 45 min |
| 3 | Cross-region remote peering and a third app instance | 35 min |
| 4 | Hub-and-spoke transit routing | 40 min |
| 5 | Private load balancer with local and remote backends | 35 min |
| 6 (Optional) | Same-region cross-tenancy local peering for a shared-services VCN | 45 min |
| 7 | VPN, FastConnect, and multicloud design discussion | 25 min |
| Cleanup | Remove all workshop resources | 20 min |

## Prerequisites

* Access to two OCI regions and a compartment where you can manage virtual networks, DRGs, remote peering connections, load balancers, and instances.
* An SSH key pair and a workstation with SSH and `curl`.
* Sufficient service limits for three flexible compute instances and one flexible load balancer. Use the smallest available shapes suitable for your tenancy.
* Permission to use the selected region subscriptions. The workshop uses billable resources; complete Cleanup when finished.

Use one naming prefix, for example `advnet-<initials>-`, and apply the free-form tag `workshop=oci-advanced-networking` to every resource. Record OCIDs and private IP addresses as you go.

## Objectives

After this workshop, you can:

* Select the correct OCI routing, gateway, security-list, and NSG controls for a traffic path.
* Build local and remote VCN connectivity through DRG v2.
* Configure DRG route tables and VCN route tables for deliberate transit routing.
* Use health checks and security rules to place backends from locally and remotely connected VCNs behind a private load balancer.
* Explain when to use IPSec VPN, FastConnect, and OCI multicloud interconnect patterns.

> The labs deliberately use a **private** load balancer. If you change it to public, you must add an internet gateway, public subnet routing, and appropriately narrow ingress rules; those changes are outside this workshop.

## Learn More

* [Networking overview](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/overview.htm)
* [Dynamic Routing Gateways](https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/managingDRGs.htm)
* [Load Balancer documentation](https://docs.oracle.com/en-us/iaas/Content/Balance/Concepts/balanceoverview.htm)

## Acknowledgements

* **Author** — Oracle
* **Last Updated** — August 2026
