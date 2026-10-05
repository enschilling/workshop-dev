# Cleanup

## Introduction

Remove the resources you created in both OCI regions and, if applicable, the second tenancy or Azure subscription. Work in dependency order and use your worksheet to confirm ownership before deleting each resource. A workshop tag alone is not sufficient in a shared customer environment.

**Estimated time:** 20–30 minutes for the core path, plus asynchronous deletion. Optional circuits, gateways, firewall resources, or additional hosts can take longer.

### Prerequisites

* Your resource inventory, private IPs, compartment and region records, and any optional-lab inventory.
* Permission to delete the resources you own.
* Completion of evidence collection. Confirm Lab 3's temporary route and NSG changes were restored before capturing the final working topology.

## Task 1: Establish the exact cleanup scope

1. List the resources created by your attendee identity in **Ashburn** and **Phoenix**. Match names, OCIDs, workshop/attendee tags, and your worksheet.
2. Include wizard-created subnets, route tables, security lists, and gateways even when their generated names do not use `advnet-`.
3. Record extra resources from troubleshooting: temporary Bastions, extra sessions, RDP hosts, additional boot volumes, and capture filters.
4. Separate shared customer infrastructure from attendee resources. Do not delete the working compartment, existing policies, pre-existing gateways, or another attendee's resources.
5. If you completed Optional Lab 4, coordinate the second-tenancy scope with its administrator. If you completed Optional Lab 5 or 6, complete those extensions' cleanup before removing their underlying network dependencies.

## Task 2: Remove optional extensions you provisioned

### Cross-tenancy LPG challenge

1. In each tenancy, remove only the workload route rules pointing to the challenge LPG and the peer-specific security rules you added.
2. Delete the challenge LPG in each VCN. Confirm the peer no longer has an active peering relationship.
3. Have each administrator remove only the challenge-specific `Define`, `Endorse`, `Admit`, and related permission statements. If they share a policy with other statements, edit that policy rather than deleting the whole policy.
4. Delete any challenge-only hosts, volumes, and VCNs you created. Preserve a reused core Hub VCN until Task 5.

### OCI–Azure extension

1. Stop tests and capture the final transport/route evidence. Remove the Azure destinations and peer-specific ingress rules from the OCI subnet tables/NSGs.
2. Delete the workshop's Azure VPN connections and ExpressRoute VNet gateway connection, as applicable.
3. Delete the OCI IPSec connection and its tunnel attachments, then the workshop CPE object. Delete the workshop FastConnect virtual circuit if one was created.
4. Deprovision the provider-backed ExpressRoute circuit, confirm its provider state permits deletion, then delete it. Verify both OCI and Azure circuit objects are gone; deleting only the VNet connection does not stop circuit billing.
5. Delete the workshop's Azure gateways, local network gateways, gateway public IPs, VM, disks, NICs, NSGs, VNet, and any explicit egress resources.
6. You can delete `advnet-workshop-rg` as a group **only after confirming it contains exclusively your disposable workshop resources and the circuit has been deprovisioned**. In a shared resource group, delete only the individual owned resources.

### Linked Network Firewall workshop

Use the linked workshop's inventory and service deletion procedures for its firewalls, policies, load balancers, certificates/Vault resources, logs, hosts, and network resources. Its scope is separate from this core topology. Do not delete shared certificates, secrets, Vaults, or policies merely because they were referenced by a lab.

## Task 3: End sessions and remove observability resources

1. Stop local SSH/port-forwarding processes and close RDP sessions.
2. In Ashburn, delete your Bastion sessions and `advnet-bastion`. Repeat in Phoenix or the Hub VCN if you created temporary Bastions there. Wait for asynchronous deletion to complete.
3. Delete saved NPA test `advnet-spoke1-to-hub-8080` and any additional attendee tests.
4. Disable/delete the Hub flow-log configuration and its log. Delete the attendee capture filter once no configuration references it.
5. Delete `advnet-log-group` only when it contains exclusively your logs and you no longer need them. Preserve shared logs or log groups. Service Audit history is not a workshop-owned log to delete.

## Task 4: Terminate compute and remove volumes

1. In **Ashburn**, verify and terminate `advnet-hub-vm` and `advnet-spoke1-vm`, plus any additional RDP host you created.
2. In **Phoenix**, verify and terminate `advnet-remotespoke-vm`.
3. For disposable lab hosts, select deletion of their boot volumes during termination. If a volume must be retained, record why and its ongoing cost.
4. Wait for termination and inspect **Boot Volumes** and **Block Volumes** in both regions for any detached lab volumes or backups. Delete only the recorded attendee-owned volumes/backups.

## Task 5: Remove peering, regional DRGs, and VCNs

1. Record final RPC ownership in both regions. Delete your `advnet-rpc-iad` and `advnet-rpc-phx`. Refresh the peer views as the connection is removed.
2. Confirm there are no remaining workshop IPSec/FastConnect attachments from Optional Lab 5. Delete the VCN attachments: Hub and Spoke-1 in Ashburn, Remote-Spoke in Phoenix.
3. Wait for detachments, then delete `advnet-drg-iad` and `advnet-drg-phx`. Remove attendee-created custom DRG route tables/distributions if they block deletion; do not touch shared DRGs.
4. Open each attendee VCN and use its **Delete VCN** workflow. Review the listed dependencies before approving the deletion. The workflow can remove disposable subnets, route tables, security lists, and gateways once VNICs and attachments are gone.
5. If deletion is blocked, inspect the named dependency. Common causes include an instance/VNIC, Bastion endpoint, LPG, load balancer, firewall, or a gateway reference from an active route. Resolve that specific owned dependency and retry the existing deletion; do not create a replacement VCN.
6. If removing components manually, remove relevant route references before deleting Internet/NAT/Service gateways. Delete subnets, custom route tables/security lists/NSGs, and remaining owned VCN dependencies, then the VCN itself. Respect default-resource restrictions shown by the console.

## Task 6: Verify completion

1. In both **Ashburn** and **Phoenix**, filter compute, volumes, VCNs, DRGs, RPCs, Bastions, and logging by your compartment/ownership inventory. Check failed or pending deletion work requests before declaring success.
2. If you used a second tenancy, obtain confirmation from its administrator. If you used Azure, verify gateways, VM disks, and circuits in that subscription, not just OCI.
3. Remove lab-only local desktop credentials/files according to your organization's policy. Keep sanitized architecture and test evidence; never retain shared keys or private-key material in the workshop report.
4. Record the final state for every resource in the worksheet as **deleted**, **retained with owner/reason**, or **deletion pending with work-request reference**.

**Completion:** no unaccounted attendee-created billable resources remain. Preserve any intentionally retained shared resources and identify their owner explicitly.

## Acknowledgements

* **Author** — Eli Schilling, Technical Engagement Services, Oracle
* **Last Updated By/Date** — Eli Schilling, October 2026
