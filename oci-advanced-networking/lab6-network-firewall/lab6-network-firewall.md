# Optional Lab 6: OCI Network Firewall Common Use Cases

## Introduction

Peering provides a route between networks; it does not inspect the traffic on that route. A security architecture must decide which flows require inspection, where that inspection occurs, and how both directions of a connection traverse the intended policy enforcement point.

This optional extension takes you to **OCI Network Firewall Common Use Cases**, a dedicated Oracle LiveLabs workshop. OCI Network Firewall is a managed next-generation firewall and intrusion detection and prevention service powered by Palo Alto Networks. The workshop teaches firewall deployment, policy configuration, routing to place a firewall in the traffic path, and testing with traffic and logs.

**Estimated time:** 3–5 hours in the source workshop introduction; the live catalog lists **5 hours**. Reserve a five-hour block plus provisioning and cleanup for the full linked workshop. This is a separate workshop agenda, rather than a short configuration task on the core networking topology.

### Why take this extension?

The core workshop establishes reachability and secure administrative access. The firewall workshop adds policy enforcement for east-west traffic between applications and north-south traffic entering or leaving the network. Its exercises make the distinction observable: a route can exist, while a firewall rule deliberately permits, inspects, or denies a connection.

The customer discussion is about inspection placement and ownership. A shared-services team may manage policy centrally, while application teams retain control of their workloads. Choosing a single central inspection point or multiple firewalls depends on routing, availability, throughput, isolation, and compliance requirements. A DRG or LPG connection alone does not force traffic through a firewall. Plan symmetric forward and return paths before applying inspection policy.

### Objectives

In the linked workshop, you will learn to:

* Deploy VCNs, subnets, route tables, security lists, and private compute endpoints.
* Create firewall policies and deploy OCI Network Firewall instances.
* Adjust VCN routing to introduce inspection into selected paths.
* Test allowed and blocked flows and interpret firewall logs.
* Explore SSL decryption and intrusion detection with the required supporting configuration.

### What the linked workshop covers

The following sequence comes from the **OCI Network Firewall Common Use Cases** workshop manifest. Its labs depend on the constructs created in earlier labs.

| Linked lab | Topic | What you will explore |
| --- | --- | --- |
| 1 | OCI Network Firewall deployment | Dedicated firewall subnet, initial routing, and firewall deployment |
| 2 | East-West Traffic Inspection | Private application subnets, test hosts, routing, policy, and logs |
| 3 | Inspect outbound Internet traffic | NAT gateway, egress routes, firewall policy, and traffic tests |
| 4 | Inspect outbound traffic to OCI Services | Service gateway routing and policy for Oracle services |
| 5 | Inspect inbound Internet traffic | Ingress firewall, application load balancer, web endpoint, and routes |
| 6 | SSL Decryption and Intrusion Detection | Vault and certificate configuration, TLS handling, and detection tests |

### Prerequisites and preparation

* Administrative OCI access, or equivalent permissions to provision the networking, compute, firewall, and supporting resources required by the linked guide.
* Basic OCI networking knowledge. The core Labs 1–3 provide useful preparation.
* A working compartment for the linked workshop. Its guide refers to a **LAB** compartment and expects the same compartment to be used throughout its dependent labs.
* Sufficient quotas and budget for the firewall and other billable resources. Review the live workshop prerequisites and current service pricing before provisioning.

Follow the linked workshop's own names, address plan, setup, and lab order. Start with its introduction and login/setup instructions. Do not assume that the three-VCN topology from this workshop can substitute for the resources it asks you to build. Use a separate compartment or inventory so that the two cleanup scopes remain clear.

### Discussion prompts

Before entering the workshop, choose one customer flow to trace: application-to-application, outbound internet, OCI service access, or inbound HTTPS. Identify the source, destination, inspected path, return path, policy owner, and evidence that will demonstrate the firewall is actually in the path.

After completing the linked exercises, discuss how those patterns would apply to the Hub VCN and to the cross-tenancy shared-services challenge. Include failure handling and unintended bypass routes in the design review.

## Task 1: Open the live workshop

[Launch OCI Network Firewall Common Use Cases on Oracle LiveLabs](https://livelabs.oracle.com/ords/r/dbpm/livelabs/view-workshop?wid=3872)

## Learn More

* [OCI Network Firewall documentation](https://docs.oracle.com/en-us/iaas/Content/network-firewall/home.htm)

## Acknowledgements

* **Linked workshop author** — Radu Nistor, Principal Cloud Architect, OCI Networking
* **Workshop integration** — Eli Schilling, Technical Engagement Services, Oracle
* **Last Updated By/Date** — Eli Schilling, October 2026
