# Introduction: Shared Services and Cross-Tenancy Peering

## About this Workshop

This specialized tenancy variant focuses on a centrally managed shared-services VCN. It fits a network-security team or managed services provider that needs private, governed access between a customer or stakeholder VCN and shared inspection, logging, or management services.

The required path uses the networking foundation, explicit transit routing, and a private load balancer. The optional final lab adds same-region cross-tenancy local peering with Local Peering Gateways (LPGs) and the coordinated IAM policies required by both tenancies.

## Important baseline

This is a shortened advanced path. Before Lab 2, the facilitator must prebuild the Remote VCN, both DRGs, the Remote VCN DRG attachment, and the Ashburn-to-Phoenix RPC described in the standard workshop's original Labs 2 and 3. Use the original CIDRs: Client `10.10.0.0/16`, Hub `10.20.0.0/16`, and Remote `10.30.0.0/16`.

The optional cross-tenancy lab is intentionally separate from the DRG/RPC topology. It uses two non-overlapping VCNs in the **same OCI region**, one in each tenancy, and an LPG on each VCN.

## Lab path

| Lab | Outcome | Estimate |
| --- | --- | --- |
| 1 | VCN, subnet, gateway, route-table, and security-policy foundation | 45 min |
| 2 | Explicit hub-and-spoke transit routing over the prebuilt DRG/RPC baseline | 40 min |
| 3 | Private load balancer with local and remote backends | 35 min |
| Optional 4 | Same-region cross-tenancy LPG peering for a shared-services use case | 45 min |
| Cleanup | Remove workshop and optional-lab resources | 20 min |

## Prerequisites

* A compartment where the attendee can manage virtual networks, DRGs, load balancers, and instances.
* The prebuilt remote-peering baseline stated above.
* For Optional Lab 4, two participating tenancy administrators, their tenancy OCIDs, the requestor network-admin group OCID, and authority to create root-compartment IAM policies in both tenancies.
* The same OCI region subscribed in both participating tenancies for local peering.

> A peered VCN is not automatically a security transit service. Traffic steering through a firewall or other inspection service needs its own deliberate route, return-path, and policy design.
