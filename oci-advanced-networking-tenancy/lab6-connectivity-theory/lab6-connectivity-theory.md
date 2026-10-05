# Lab 7: VPN, FastConnect, and Multicloud

## Introduction

This is a design discussion only. Do not provision VPN, FastConnect, or multicloud services for this lab.

**Time:** 25 minutes

## IPSec VPN

Use OCI Site-to-Site VPN for encrypted connectivity over the public internet. It is a strong fit for rapid deployment, branch connectivity, redundancy, and as a backup to private circuits. Plan two tunnels, dynamic BGP routing where available, non-overlapping CIDRs, redundant customer-premises equipment, and clear route preference/failover behavior. Account for internet performance variability and tunnel throughput when sizing the design.

## FastConnect

Use FastConnect when you need private, predictable connectivity into OCI through a provider or colocated connection. Design for redundancy: separate physical paths/providers or locations where possible, two BGP sessions, and route filtering. FastConnect is a connectivity service; it does not eliminate the need for VCN, DRG, firewall, DNS, and routing design.

## Multicloud interconnect

For OCI and another cloud, start with the application’s latency, throughput, availability, ownership, and data-governance requirements. OCI offers supported interconnect patterns with cloud providers; paired private circuits may be appropriate where available. Otherwise, VPN over public endpoints or provider-mediated connectivity can be a practical option.

Discuss these questions before implementation:

1. Which prefixes may cross the boundary, and which must never be advertised?
2. Where are DNS, identity, inspection, egress, and observability owned?
3. What is the active path, backup path, and tested failover time?
4. How will billing for circuits, data transfer, and redundant connections be controlled?

> Validate current regional availability, partner support, service limits, and pricing with the OCI documentation and your cloud/provider contacts before making a production decision.

## Recap

You have moved from VCN fundamentals to DRG local and remote peering, explicit transit routing, and a cross-VCN private load-balancer backend pool. The same design discipline applies when the next hop becomes a VPN, FastConnect virtual circuit, or multicloud edge.
