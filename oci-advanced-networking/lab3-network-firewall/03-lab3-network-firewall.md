# Lab 3: Centralized Inspection — OCI Network Firewall

## Introduction

In this lab you insert a single managed **OCI Network Firewall** (a Palo Alto Networks-powered, next-generation firewall) into the Hub VCN and steer traffic through it with routing. One firewall in the hub inspects both **north-south** traffic (to and from the internet) and **east-west** traffic (between spokes) — there is no need for a firewall in every VCN.

This answers a common design question directly: *do I need a firewall per VCN, or just the hub?* **Just the hub.** The OCI Network Firewall is highly available and horizontally scalable, so a single instance in the Hub VCN is the recommended pattern. You centralize policy there and use **routing** to insert it into the relevant paths — the same approach the OCI Core Landing Zone uses.

*Estimated Time:* 40 minutes

### The key idea: insertion by routing, with symmetry

A network firewall doesn't intercept traffic by magic — you *route* traffic to its private IP, it inspects, and it forwards the packet on. The two non-negotiables:

* **Symmetric routing.** Forward and return traffic for a flow must traverse the *same* firewall. Asymmetric paths cause the firewall to see only half a conversation and drop it.
* **NAT route tables accept only private-IP targets.** You cannot point a NAT gateway's route table at the DRG or firewall. Internet-egress inspection is therefore achieved by routing spoke traffic to the **firewall's private IP** first; the firewall subnet's own route table then uses the NAT gateway as its next hop.

### Objectives

In this lab, you will:

* Create a dedicated firewall subnet in the Hub VCN
* Build a firewall policy with an IDPS profile and a sample FQDN-filter rule
* Deploy the OCI Network Firewall with a fixed private IP
* Insert it into the **north-south** path (spoke → internet)
* Insert it into the **east-west** path (Spoke-1 ⇄ Remote-Spoke)
* Demonstrate and log a **deny**

### Prerequisites

This lab assumes you have:

* Completed **Lab 1** (hub-and-spoke backbone with the DRG and test VMs)
* Permissions equivalent to `manage network-firewall-family` plus the networking permissions from Lab 1
* The Hub VCN `advnet-hub-vcn` (`10.0.0.0/16`) with its NAT and internet gateways

> **Cost callout:** the Network Firewall instance has an hourly charge (the first 10 TB processed is free). Provision it for the lab and delete it in Lab 6.

## Task 1: Create the firewall subnet

The firewall needs its own subnet in the Hub VCN, separate from the workload and public subnets.

1. In **Ashburn**, open `advnet-hub-vcn → Subnets → Create Subnet`:

   * **Name:** `advnet-hub-fw-subnet`
   * **CIDR Block:** `10.0.2.0/24`
   * **Subnet Access:** Private Subnet
   * **Route Table:** create/assign a dedicated route table `advnet-hub-fw-rt` (you populate it in Task 4)

   ![Create the firewall subnet in the Hub VCN](images/lab3-01-fw-subnet.png)

## Task 2: Create the firewall policy

The policy is created independently of the firewall instance, then attached. It holds the security rules, the IDPS (intrusion detection/prevention) profile, and any URL/FQDN filtering.

1. Go to **Networking → Network Firewall → Network Firewall Policies → Create Network Firewall Policy**:

   * **Name:** `advnet-fw-policy`
   * **Compartment:** `advnet-workshop`

2. Open the policy and add the building blocks:

   * **Lists → Applications/Services:** confirm built-in services (or add custom ports) you intend to reference.
   * **Lists → URL Lists / FQDN Lists:** create an FQDN list (for example, a list containing a domain you'll block in Task 6).
   * **Security Rules → Create Security Rule:** add a permissive baseline rule that **inspects** traffic between the workshop CIDRs (action: *Inspect* with IDPS), so you can see allowed traffic in the logs before adding a deny.

   ![Firewall policy with security rule and IDPS profile](images/lab3-02-fw-policy.png)

3. *(Optional)* Enable an **IDPS** profile (action mode) and note that **TLS inspection** requires a decryption profile and certificate — out of scope here but worth mentioning to the audience.

## Task 3: Deploy the Network Firewall

1. Go to **Networking → Network Firewall → Network Firewalls → Create Network Firewall**:

   * **Name:** `advnet-nfw`
   * **Compartment:** `advnet-workshop`
   * **Network Firewall Policy:** `advnet-fw-policy`
   * **Virtual Cloud Network:** `advnet-hub-vcn`
   * **Subnet:** `advnet-hub-fw-subnet`
   * **(Optional) Assign an IPv4 address:** pick a fixed private IP in the firewall subnet, for example `10.0.2.10` — record it; every route rule in Task 4 points here.

   ![Create the Network Firewall instance](images/lab3-03-create-nfw.png)

2. Click **Create** and wait for the firewall to reach **Active**. Note its assigned **private IP** (referred to below as `FW_IP`).

## Task 4: North-south insertion (spoke → internet, inspected)

Goal: a Spoke-1 host's outbound internet traffic is inspected by the firewall, then NAT'd out.

1. **Spoke-1 egress → firewall.** On the Spoke-1 private route table, point the default route at the firewall via the DRG path into the hub. Practically, route `0.0.0.0/0` to the DRG so it lands in the hub, where the hub's ingress routing (next step) sends it to the firewall.

2. **Hub VCN ingress → firewall.** On the Hub VCN, set the **route table associated with the DRG attachment (ingress route table)** so that traffic destined for the internet (`0.0.0.0/0`) and inter-spoke ranges is sent to **`FW_IP`** (target type: Private IP).

3. **Firewall subnet → NAT.** On `advnet-hub-fw-rt` (the firewall subnet's route table), route `0.0.0.0/0` to the **NAT gateway**. This is the step that respects the "NAT route tables accept only private-IP targets" rule — the firewall (a private IP) is the hop *before* NAT, not the NAT's target.

   | Route table | Destination | Target |
   |-------------|-------------|--------|
   | Spoke-1 private | `0.0.0.0/0` | DRG `advnet-drg-iad` |
   | Hub DRG-ingress | `0.0.0.0/0` | Private IP `FW_IP` |
   | Hub firewall subnet | `0.0.0.0/0` | NAT gateway |

   ![North-south routing through the firewall to NAT](images/lab3-04-north-south.png)

4. **Verify.** From the Spoke-1 VM, generate outbound traffic (for example `curl https://example.com`). Confirm the flow appears in the firewall's **traffic logs**.

## Task 5: East-west insertion (Spoke-1 ⇄ Remote-Spoke, inspected)

Goal: traffic between the two spokes is forced through the hub firewall rather than going DRG-to-DRG directly.

1. On the **Hub DRG-ingress route table**, add rules sending the spoke CIDRs to **`FW_IP`**:

   | Destination | Target |
   |-------------|--------|
   | `10.1.0.0/16` (Spoke-1) | Private IP `FW_IP` |
   | `10.2.0.0/16` (Remote-Spoke) | Private IP `FW_IP` |

2. On the **firewall subnet route table**, add return routes back to the DRG so inspected traffic continues to its destination:

   | Destination | Target |
   |-------------|--------|
   | `10.1.0.0/16` | DRG `advnet-drg-iad` |
   | `10.2.0.0/16` | DRG `advnet-drg-iad` |

   The packet walk for Spoke-1 → Remote-Spoke becomes: Spoke-1 → DRG → **hub firewall (inspect)** → DRG → RPC → Phoenix DRG → Remote-Spoke. Return traffic hairpins through the same firewall, preserving **symmetry**.

   ![East-west routing hairpinning through the hub firewall](images/lab3-05-east-west.png)

3. **Verify** with a flow between the Spoke-1 and Remote-Spoke VMs and read the firewall logs.

## Task 6: Demonstrate a deny

1. In `advnet-fw-policy`, add a **security rule** with action **Deny** — for example, block the FQDN list created in Task 2, or block a specific inter-spoke port.

2. Re-run the corresponding traffic test and confirm it now **fails**, and that the **REJECT** is recorded in the firewall logs. This proves the firewall is genuinely in-path and inspecting, not bypassed.

   ![Firewall deny rule and the matching log entry](images/lab3-06-deny-log.png)

## Lab Recap

You centralized inspection in the hub:

* A dedicated firewall subnet (`10.0.2.0/24`) in the Hub VCN
* A firewall policy with an inspect rule, an IDPS profile, and an FQDN list
* A deployed Network Firewall with a fixed private IP
* **North-south** insertion (spoke → firewall → NAT) honoring the private-IP-target rule
* **East-west** insertion (spoke ⇄ spoke hairpinned through the hub firewall) with symmetric routing
* A logged **deny** proving traffic is inspected

One firewall, in the hub, inspecting the whole topology — no per-spoke appliances.

## Learn More

* [OCI Network Firewall overview](https://docs.oracle.com/en-us/iaas/Content/network-firewall/overview.htm)
* [Creating a network firewall policy](https://docs.oracle.com/en-us/iaas/Content/network-firewall/managing-policy.htm)
* [Routing traffic to the firewall](https://docs.oracle.com/en-us/iaas/Content/network-firewall/route-rules.htm)
* [OCI Core Landing Zone](https://github.com/oci-landing-zones)

## Acknowledgements

* **Author** — Eli Schilling, Technical Engagement Services, Oracle
* **Contributors** — Oracle LiveLabs Platform Team
* **Last Updated By/Date** — Eli Schilling, June 2026
