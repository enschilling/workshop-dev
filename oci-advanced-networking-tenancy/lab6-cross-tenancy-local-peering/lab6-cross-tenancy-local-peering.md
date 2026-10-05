# Lab 6: Cross-Tenancy Local Peering for Shared Services

## Introduction

This optional lab connects a centrally managed shared-services VCN to a customer or stakeholder VCN in a different OCI tenancy. A network-security or managed-services team can use the pattern to provide private access to shared inspection, logging, management, or application services.

The two VCNs must be in the **same OCI region** and have non-overlapping CIDRs. This lab uses Local Peering Gateways (LPGs), not DRGs or remote peering connections.

**Time:** 45 minutes

## Task 1: Agree on the peering contract

Designate one administrator as the **requestor** and the other as the **acceptor**. Record and exchange only the values required for peering:

| Party | Share with the other administrator |
| --- | --- |
| Requestor | Requestor tenancy OCID, requestor network-admin group OCID, VCN CIDR, and LPG OCID after creation |
| Acceptor | Acceptor tenancy OCID, VCN CIDR, and LPG OCID after creation |

Use separate non-overlapping CIDRs, for example Shared Services `10.40.0.0/16` and Customer `10.50.0.0/16`. Limit the routes and security rules to the application or inspection subnets that need to communicate.

## Task 2: Create the IAM policies in both tenancies

Create these policies in the **root compartment** of the corresponding tenancy. Replace every placeholder before saving. The requestor group must also have ordinary permission in its own compartment to create LPGs and update its route and security rules.

### Requestor tenancy policy

```text
Define tenancy Acceptor as <acceptor_tenancy_ocid>
Allow group <requestor_network_admin_group> to manage local-peering-gateways in compartment <requestor_network_compartment>
Allow group <requestor_network_admin_group> to manage route-tables in compartment <requestor_network_compartment>
Allow group <requestor_network_admin_group> to manage network-security-groups in compartment <requestor_network_compartment>
Allow group <requestor_network_admin_group> to manage security-lists in compartment <requestor_network_compartment>
Allow group <requestor_network_admin_group> to manage local-peering-from in compartment <requestor_network_compartment>
Endorse group <requestor_network_admin_group> to manage local-peering-to in tenancy Acceptor
Endorse group <requestor_network_admin_group> to associate local-peering-gateways in compartment <requestor_network_compartment> with local-peering-gateways in tenancy Acceptor
```

### Acceptor tenancy policy

```text
Define tenancy Requestor as <requestor_tenancy_ocid>
Define group requestor_network_admin_group as <requestor_network_admin_group_ocid>
Admit group requestor_network_admin_group of tenancy Requestor to manage local-peering-to in compartment <acceptor_network_compartment>
Admit group requestor_network_admin_group of tenancy Requestor to associate local-peering-gateways in tenancy Requestor with local-peering-gateways in compartment <acceptor_network_compartment>
```

> The `Define`, `Endorse`, and `Admit` statements are a coordinated agreement: neither tenancy can create the cross-tenancy peering on its own. The acceptor policy must be attached at the root compartment, not only inside the acceptor network compartment.

## Task 3: Create and connect the LPGs

1. In each tenancy, open the VCN and create one LPG. Use names such as `shared-services-lpg` and `customer-lpg`.
2. The acceptor gives the requestor the acceptor LPG OCID and acceptor tenancy OCID.
3. The requestor opens its LPG, selects **Establish Peering Connection**, supplies the acceptor tenancy OCID and LPG OCID, and waits for the connection to become **Peered**.

## Task 4: Configure routing and security

On each participating workload subnet, add a route to the other VCN CIDR with the local LPG as the target:

| Tenancy | Destination | Target |
| --- | --- | --- |
| Shared-services | Customer VCN CIDR | Shared-services LPG |
| Customer | Shared-services VCN CIDR | Customer LPG |

Add narrowly scoped NSG or security-list rules for only the intended traffic. For the metadata app example, permit TCP 8080 from the peer workload CIDR. Test with a private-IP `curl` from the customer workload to the shared-service endpoint.

## Discussion: central security services

LPG peering supplies private VCN-to-VCN connectivity; it does not automatically force traffic through a firewall. To use a central security VCN as a transit or inspection point, design explicit subnet routes, symmetric return paths, and firewall policies, then validate each intended flow. Do not allow a customer VCN to use the shared-services VCN as an unintended path to the public internet.

**Checkpoint:** Save the two LPG OCIDs, both tenancy OCIDs, the approved policy text, route-table evidence, and one successful private connectivity test.
