# Lab 3: Troubleshooting — Network Command Center

## Introduction

Turn the network you built into a network you can operate. You will explore its topology, analyze a **same-region** application path, introduce and repair a routing fault, then use flow logs to distinguish permitted from rejected traffic. The exercise mirrors a customer incident: an application request fails, and the engineer must find the failing layer without rebuilding the environment.

Use three kinds of evidence together. **Network Visualizer** explains the topology. **Network Path Analyzer (NPA)** evaluates network configuration. **Live HTTP requests and VCN Flow Logs** show actual traffic and the responding application. Each answers a different question.

**Estimated time:** 40–50 minutes, including log-ingestion waits.

### Objectives

* Explore VCNs, regional DRGs, attachments, and RPCs in topology views.
* Analyze Spoke-1 → Hub in Ashburn with NPA.
* Remove and restore one workshop route, recording the result.
* Capture actual ACCEPT and REJECT flows for TCP 8080.
* Validate cross-region reachability with configuration and application evidence.
* Interpret tool limitations and inter-region latency correctly.

### Prerequisites

* Completed **Labs 1 and 2**. The Spoke-1 metadata app can reach Hub and Remote-Spoke; you can access its shell through Bastion.
* The worksheet's private IPs, VNIC OCIDs, route tables, and NSG rules.
* Permissions to read the relevant network and compute resources and manage NPA tests, log groups, logs, and capture filters.
* **No Azure, second tenancy, or Network Firewall resources are required.**

### Administrator preflight for the network tools

Network Visualizer's documented permission is `Allow group <workshop-group> to read all-resources in tenancy`. Have the administrator approve that broader read scope, or have the facilitator demonstrate Task 1 using an authorized identity. Networking management permission in one compartment does not automatically satisfy Visualizer's access requirement. See [Network Visualizer permissions](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/network_visualizer.htm).

Before the event, ask the tenancy administrator to review the [current NPA permissions and limitations](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/path_analyzer.htm). Its documented example includes tenancy-level user and service permissions:

```text
Allow group <workshop-group> to manage vn-path-analyzer-test in tenancy
Allow any-user to inspect compartments in tenancy where all { request.principal.type = 'vnpa-service' }
Allow any-user to read instances in tenancy where all { request.principal.type = 'vnpa-service' }
Allow any-user to read virtual-network-family in tenancy where all { request.principal.type = 'vnpa-service' }
Allow any-user to read load-balancers in tenancy where all { request.principal.type = 'vnpa-service' }
Allow any-user to read network-security-group in tenancy where all { request.principal.type = 'vnpa-service' }
Allow any-user to read zpr-family in tenancy where all { request.principal.type = 'vnpa-service' }
```

These permissions allow the service to collect configuration; they do not give an attendee unrestricted network administration. The user's own visibility affects which entities appear in results. If policy changes are restricted by your organization, have the facilitator run NPA and share the results, while attendees perform the live tests and log analysis.

## Task 1: Network Visualizer — understand the topology

1. Confirm **Ashburn** and the working compartment. Open **Networking → Network Command Center → Network Visualizer**.
2. Use the regional network view to locate `advnet-drg-iad`, `advnet-hub-vcn`, and `advnet-spoke1-vcn`. Follow the attachments and inspect the VCN/subnet details available in the view.
3. Compare the map with the architecture from Lab 1. Find the Hub private subnet and Spoke-1 private subnet, and confirm the VCNs connect to the same DRG.

   ![Ashburn local topology used for the NPA exercise](../lab1-hub-and-spoke/images/lab1-architecture-local-hub-spoke.svg)

4. Locate the Ashburn RPC attachment and use its details to identify the peer. Switch to **Phoenix**, select the working compartment again, and inspect the Remote-Spoke VCN and `advnet-drg-phx` there. Region-scoped views may show the peer as a connection rather than render all remote resources.
5. Return to Ashburn. Record the two local VCN attachment names and which route table each private subnet uses.

**Observe:** the map establishes which components exist and how they connect. It does not prove that TCP 8080 is listening or that a request is allowed.

## Task 2: Network Path Analyzer — verify the same-region path

The primary analysis is **Spoke-1 → Hub within Ashburn**. Do not select Phoenix as the destination for this exercise.

1. Open **Network Command Center → Network Path Analyzer** and select **Create Path Analysis** (or create a saved test in the console's current layout).
2. Configure:

   | Field | Value |
   | --- | --- |
   | Name | `advnet-spoke1-to-hub-8080` |
   | Source | Spoke-1 primary VNIC/private IP |
   | Destination | Hub primary VNIC/private IP |
   | Protocol | TCP |
   | Destination port | 8080 |
   | Bidirectional analysis | Enabled |

3. Save and run the analysis. Wait for the work request to finish; open the result and inspect the forward and return paths.
4. Match the reported entities to your worksheet: source VNIC/security rules, Spoke-1 subnet route to the DRG, Ashburn DRG attachments and routes, Hub destination security, and the return route. Use the console's status and explanation rather than relying on a particular icon color.
5. On Spoke-1 through Bastion, run the same real request, substituting Hub's actual IP:

   ```bash
   HUB_IP='<hub-private-ip>'
   curl --fail --connect-timeout 5 --max-time 15 "http://$HUB_IP:8080/"
   ```

6. Record the NPA result alongside the responding Hub hostname. If analysis passes while `curl` fails, inspect application service/host-firewall state. NPA does not send packets or inspect the host's running web process.

**Expected result:** a reachable same-region configuration and a successful live Hub HTTP response. If the analysis is incomplete, first verify permissions and the selected endpoint/VNIC; do not treat missing visibility as evidence that a route is absent.

## Task 3: Introduce a routing fault, diagnose it, and restore it

Use only your own workshop route. Keep the worksheet and a copy of its destination, target type, and target open before editing.

1. Open the **Hub private subnet's** associated route table. Record the rule **`10.1.0.0/16 → advnet-drg-iad`**.
2. Remove **only that rule**. Leave NAT, Service Gateway, Remote-Spoke, and any unrelated routes untouched. You are removing the Hub's return route to Spoke-1, rather than disconnecting the Bastion from Spoke-1.
3. Run a **new analysis** of the saved test from Task 2 with bidirectional checking. Inspect the failed/changed return path and its diagnostic explanation. A fallback NAT default is not the intended private return route.
4. Start a new `curl` request from Spoke-1. Record its timeout or failure with the same maximum-time settings as Task 2.
5. Restore the recorded rule with destination **`10.1.0.0/16`**, target type **Dynamic Routing Gateway**, target **`advnet-drg-iad`**.
6. Re-run NPA and the live HTTP request. Confirm the restored route is visible in the correct table and the page responds again.

**Checkpoint:** save before/fault/after results, the exact changed rule, and the successful recovery request. Do not move to the next task while the route is still missing.

**Discussion:** why does the TCP request need a return route? Why can the source subnet look correct while the application still times out?

## Task 4: VCN Flow Logs — produce ACCEPT and REJECT evidence

This task observes traffic at the **Hub destination**, including rejected requests. The narrowly scoped Lab 1 NSG rules let you isolate the Spoke-1 TCP 8080 permission without changing other workshop access.

### Enable capture

1. In Ashburn, create log group **`advnet-log-group`** in the working compartment under **Observability & Management → Logging → Log Groups**.
2. Open **Networking → Network Command Center → Flow Logs** (or the Hub private subnet's logging/monitoring view) and enable flow logs for the **Hub private subnet**. Select that subnet as the enablement point and the new log group as the destination.
3. Create/select capture filter **`advnet-hub-http-capture`**. For the short lab, use **100% sampling** and capture **both accepted and rejected traffic**. If your console offers source/destination/protocol filtering, scope it to Spoke-1's `/32`, Hub's `/32`, and TCP 8080. Record the filter and log OCIDs.
4. Name the log **`advnet-hub-flowlog`**, complete enablement, and verify logging is active. See the [Flow Logs setup guidance](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/vcn-flow-logs.htm) if the console offers a different enablement layout.

### Generate permitted requests

5. From the Spoke-1 shell, create several short-lived HTTP connections:

   ```bash
   for attempt in 1 2 3 4 5; do
     curl --fail --connect-timeout 5 --max-time 15 "http://$HUB_IP:8080/health"
     sleep 1
   done
   ```

6. Wait for log delivery, then search the log within the test time range. Identify the Hub destination IP, Spoke-1 source IP, destination port 8080, and action **ACCEPT**. Flow logs aggregate flows and arrive asynchronously; they are not one line per HTTP request.

### Introduce a security fault

7. Record the Hub application NSG's ingress rule **TCP 8080 from `10.1.0.0/16`**. Check that no attached security list or second NSG also permits this source/port; additive allow rules would mask the exercise.
8. Remove only that Hub NSG rule. Preserve the Bastion rules on **Spoke-1**, other Hub ingress rules, and all routes.
9. From Spoke-1, run a **new** TCP connection using the same `curl` command. It should fail. Re-run NPA if desired; its security explanation should differ from the routing fault in Task 3.
10. Wait for ingestion and find the Hub flow record with the matching endpoints/port and action **REJECT**. See [VCN flow-log field definitions](https://docs.oracle.com/en-us/iaas/Content/Logging/Reference/details_for_vcn_flow_logs.htm).
11. Restore the exact stateful Hub NSG rule from step 7. Start another request and verify `ok` from `/health`. Confirm the network is back in its working state.

**Interpretation:** ACCEPT confirms a network-policy decision, not application success. An ACCEPT with a failed HTTP request can still indicate a stopped web process or host firewall issue. REJECT identifies a network-security rejection; distinguish it from a missing route, a refused TCP connection, or missing log coverage.

If records are missing, inspect the enablement point, capture-filter scope/sampling, region, log time window, destination VNIC, and actual traffic generation before changing network rules.

## Task 5: Verify the cross-region path and view latency

1. Inspect both RPCs and confirm **Peered**. Review the source/return subnet routes and the DRG tables for VCN and RPC attachments from Lab 1.
2. From Spoke-1, make a live request to the Remote-Spoke:

   ```bash
   REMOTE_IP='<remote-spoke-private-ip>'
   curl --fail --connect-timeout 5 --max-time 15 "http://$REMOTE_IP:8080/"
   ```

3. Read the responding hostname and region. Save this result as the cross-region application proof.
4. NPA across a **cross-region RPC** can return **Indeterminate**. Do not expect a complete successful Ashburn-to-Phoenix analysis. Investigate each region's routes/security locally and use the live test to validate the complete path. Cross-tenancy LPG analysis has a similar limitation in Optional Lab 4.
5. Open **Network Command Center → Inter-Region Latency** and locate the **Ashburn ↔ Phoenix** pair. Record the displayed value, units, and timestamp. It is a regional network measurement, not the exact latency or response time of your application request.

### Tool limitations to carry into production

* NPA evaluates configuration, not running applications or host firewalls.
* Cross-region RPC and cross-tenancy LPG paths can be Indeterminate.
* IPv6, some private-IP next hops, intra-VCN routing, and internet-gateway paths have documented limitations.
* Visibility and results depend on permissions and supported configurations.

Consult the [current NPA caveats](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/path_analyzer.htm) before selecting a production diagnostic method.

## Lab Recap and checkpoint

You combined topology, configuration, and traffic evidence. The same-region analysis and break/fix exercise show how to diagnose a missing return route. The flow-log exercise separates a security rejection from an application problem. Cross-region reachability is proven through an actual request and the responding remote host.

Save the topology view, NPA before/fault/after results, ACCEPT/REJECT records, successful local and remote application responses, and restored route/NSG rules. Confirm all deliberately changed rules are restored. Continue with an optional extension or **Cleanup**; no optional lab is required to complete the core workshop.

## Learn More

* [Network Visualizer](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/network_visualizer.htm)
* [Network Path Analyzer](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/path_analyzer.htm)
* [VCN Flow Logs](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/vcn-flow-logs.htm)
* [Flow-log field definitions](https://docs.oracle.com/en-us/iaas/Content/Logging/Reference/details_for_vcn_flow_logs.htm)
* [Inter-Region Latency](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/inter_region_latency.htm)

## Acknowledgements

* **Author** — Eli Schilling, Technical Engagement Services, Oracle
* **Contributors** — Oracle LiveLabs Platform Team
* **Last Updated By/Date** — Eli Schilling, October 2026
