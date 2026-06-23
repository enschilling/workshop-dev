# Lab 5: Troubleshooting — Network Command Center

## Introduction

A network is only as good as your ability to diagnose it when something breaks. In this final build lab you use OCI's native, mostly non-destructive observability tools to validate — and deliberately break and re-diagnose — the topology assembled across Labs 1–4. You'll explore the whole topology visually, run hop-by-hop reachability analysis, watch the analyzer pinpoint a missing route, and read allow/deny records from flow logs.

This lab is also where the reachability checks deferred from Labs 1 and 2 are performed: rather than ping from VM to VM, you use **Network Path Analyzer (NPA)**, which evaluates routes and security rules directly — no need for every host to be online.

*Estimated Time:* 30 minutes

### The toolset

* **Network Visualizer** — a rendered topology map of VCNs, DRGs, attachments, RPCs, and the FastConnect/VPN to Azure.
* **Network Path Analyzer** — given a source and destination, it walks the route tables, security lists/NSGs, and gateways and reports whether the path is open, with the exact hop that blocks it if not.
* **VCN Flow Logs** — per-subnet ACCEPT/REJECT records for actual traffic.
* **Inter-Region Latency dashboard** — live latency between OCI regions (ties back to the Ashburn ↔ Phoenix RPC).

### Objectives

In this lab, you will:

* Visualize the full multi-region, multi-cloud topology
* Run an NPA reachability analysis across the backbone
* Break a route/rule on purpose and have NPA identify it
* Enable VCN Flow Logs and read ACCEPT/REJECT records
* View real-time inter-region latency
* Understand NPA's documented limitations

### Prerequisites

This lab assumes you have:

* Completed **Labs 1–4** (full backbone, Azure interconnect, firewall, bastion)
* Permissions for `read virtual-network-family`, `manage vcn-flow-logs` (logging), and `inspect` on the path-analysis resources

## Task 1: Network Visualizer — see the whole topology

1. Go to **Networking → Network Command Center → Network Visualizer**. Select the **`advnet-workshop`** compartment and **Ashburn**.

2. Examine the rendered map: the Hub and Spoke-1 VCNs, their DRG attachments to `advnet-drg-iad`, the **RPC** crossing to `advnet-drg-phx` / Remote-Spoke in Phoenix, and the **IPSec/FastConnect** attachment to Azure.

   ![Network Visualizer showing the multi-region topology](images/lab5-01-visualizer.png)

3. Switch the region to **Phoenix** to confirm the remote-spoke side of the RPC renders symmetrically.

## Task 2: Network Path Analyzer — validate the backbone

This performs the Lab 1 cross-region reachability validation analytically.

1. Go to **Networking → Network Command Center → Network Path Analyzer → Create Path Analysis**.

2. Configure a path from Spoke-1 to the Remote-Spoke host:

   * **Protocol:** ICMP (or TCP with a port)
   * **Source:** Spoke-1 VM (`10.1.0.x`), VCN `advnet-spoke1-vcn`
   * **Destination:** Remote-Spoke VM (`10.2.0.x`), VCN `advnet-remotespoke-vcn`

   ![Configure a path analysis between the two spokes](images/lab5-02-npa-config.png)

3. Run it. A healthy result shows every hop green: Spoke-1 route table → DRG-A → RPC → DRG-B → Remote-Spoke security list → destination. This confirms the Lab 1 local + remote peering is correctly configured.

   ![Successful hop-by-hop path analysis](images/lab5-03-npa-success.png)

4. *(Optional)* Run a second analysis to the **Azure** VM (`10.10.0.4`) to validate the Lab 2 routing and the cross-region DRG distribution for the Phoenix → Azure path.

## Task 3: Break something on purpose, then let NPA find it

1. On the **Remote-Spoke** route table, **remove** the `10.1.0.0/16 → advnet-drg-phx` rule (the return route to Spoke-1).

2. Re-run the Task 2 path analysis. NPA now reports a **failure** and names the cause precisely — a missing route rule on the return path — rather than leaving you to guess.

   ![NPA reporting the exact missing route rule](images/lab5-04-npa-failure.png)

3. **Restore** the route rule and re-run to confirm the path is green again. (Leaving the topology in a known-good state matters for the Lab 6 cleanup.)

   > This break/fix loop is the core value of NPA: it evaluates *configuration*, so it works even when hosts are unreachable or offline.

## Task 4: VCN Flow Logs — read ACCEPT/REJECT records

1. Go to **Observability & Management → Logging → Log Groups** and create a log group `advnet-log-group` in the `advnet-workshop` compartment.

2. Go to **Logging → Logs → Enable service log**, or from the subnet: open the Spoke-1 private subnet → **Create Flow Log**:

   * **Log group:** `advnet-log-group`
   * **Log name:** `advnet-spoke1-flowlog`

   ![Enable VCN Flow Logs on the Spoke-1 subnet](images/lab5-05-flowlog-enable.png)

3. Generate both **allowed** and **denied** traffic (for example, an allowed flow to the Remote-Spoke host, and a denied flow to a blocked port). Wait a few minutes for records to populate.

4. Open the log and read the records — each shows source/destination, ports, action (**ACCEPT** / **REJECT**), and bytes. This is the ground-truth complement to NPA's configuration analysis.

   ![Flow log records showing ACCEPT and REJECT actions](images/lab5-06-flowlog-records.png)

   > **Cost note:** flow logs incur logging storage cost above a threshold. Enable them for the exercise and disable in Lab 6.

## Task 5: Inter-Region Latency

1. Go to **Networking → Network Command Center → Inter-Region Latency**.

2. Locate the **Ashburn ↔ Phoenix** pair and read the live round-trip latency — the real-world cost of the cross-region RPC built in Lab 1, and a useful talking point for where to place latency-sensitive workloads.

   ![Inter-region latency dashboard for Ashburn and Phoenix](images/lab5-07-latency.png)

## Task 6: Know the limitations

Call these out explicitly so the audience trusts the tool where it's strong and verifies where it isn't:

* **No IPv6** support in Network Path Analyzer.
* **Intra-VCN routing and internet-gateway routing** aren't fully supported and can produce inaccurate NPA results — design analyses around **inter-VCN** and **on-prem-style** paths, where NPA is reliable.
* NPA analyzes **configuration**, not live device state; pair it with **Flow Logs** for ground truth.

## Lab Recap

You turned the topology from something you *built* into something you can *operate*:

* Visualized the multi-region, multi-cloud topology end-to-end
* Validated backbone reachability analytically with Network Path Analyzer
* Broke a route and had NPA pinpoint the exact cause, then restored it
* Enabled Flow Logs and read ACCEPT/REJECT ground truth
* Read live Ashburn ↔ Phoenix latency
* Learned where NPA is authoritative and where to verify

With the topology validated and returned to a known-good state, you're ready for the Lab 6 cleanup.

## Learn More

* [Network Visualizer](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/network_visualizer.htm)
* [Network Path Analyzer](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/path_analyzer.htm)
* [VCN Flow Logs](https://docs.oracle.com/en-us/iaas/Content/Network/Tasks/Vcn-flow-logs.htm)
* [Inter-Region Latency](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/latency.htm)

## Acknowledgements

* **Author** — Eli Schilling, Technical Engagement Services, Oracle
* **Contributors** — Oracle LiveLabs Platform Team
* **Last Updated By/Date** — Eli Schilling, June 2026
