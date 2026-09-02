# Lab 1: Networking Recap

## Introduction

Create the Region A foundation and confirm the difference between route selection and packet permission. Route tables decide the next hop; security lists and NSGs permit traffic. You will use an NSG for the application policy and leave the default security list minimal.

**Time:** 45 minutes

## Task 1: Plan the address space

In your worksheet, reserve these non-overlapping CIDRs. Do not overlap them with your on-premises or corporate network if you expect to extend the design later.

| Network | Region | CIDR | Purpose |
| --- | --- | --- | --- |
| Client VCN | A | `10.10.0.0/16` | Client test instance |
| Hub VCN | A | `10.20.0.0/16` | Hub test instance and load balancer |
| Remote VCN | B | `10.30.0.0/16` | Remote test instance |

Create `advnet-<initials>-client-vcn` in Region A with CIDR `10.10.0.0/16`. Create a private subnet `10.10.10.0/24` and a public management subnet `10.10.0.0/24`. Create `advnet-<initials>-hub-vcn` with CIDR `10.20.0.0/16`, a private app subnet `10.20.10.0/24`, and a private load-balancer subnet `10.20.20.0/24`.

> Use regional subnets. Disable public IPv4 assignment on all private subnets. The management subnet is optional if you use OCI Bastion or Cloud Shell for access.

## Task 2: Create gateways and route tables

For each Region A VCN, create an Internet Gateway. Create a NAT Gateway only if private instances require outbound package installation. Associate the private app subnets with a route table containing `0.0.0.0/0 → NAT Gateway`. Keep the default route table free of future DRG routes; create dedicated route tables named `client-private-rt` and `hub-private-rt`.

At this stage, do **not** add a route between the two VCNs. That is the experiment for Lab 2.

## Task 3: Define security controls

Create `advnet-<initials>-app-nsg` in each VCN and add only the rules below. Attach the NSG to each instance in the next labs.

| Direction | Protocol/port | Source/destination | Purpose |
| --- | --- | --- | --- |
| Ingress | TCP 8080 | `10.10.0.0/16`, `10.20.0.0/16`, `10.30.0.0/16` | Metadata app |
| Ingress | TCP 22 | Your management CIDR or Bastion NSG | Administration |
| Egress | All | `0.0.0.0/0` | Updates and return traffic |

For the future load balancer, create `advnet-<initials>-lb-nsg`: permit TCP 80 from the Client VCN and the Remote VCN, and permit TCP 8080 egress to the three application CIDRs. Add an additional app-NSG ingress rule permitting TCP 8080 **from the LB NSG**. Referencing the NSG, rather than an IP range, keeps the backend policy tied to the load balancer identity.

## Task 4: Verify the foundation

Use the VCN route-table and security-rule views to verify:

1. Private subnets have a NAT default route only when outbound access is needed.
2. No route currently exists between Client and Hub CIDRs.
3. App NSGs permit port 8080 only from workshop CIDRs and the load-balancer NSG.

**Checkpoint:** Save the VCN, subnet, route-table, NSG, and gateway OCIDs. Do not proceed until Region A has two non-overlapping VCNs and the security policy exists.
