# Consolidation and documentation QA — October 4, 2026

## Canonical workshop

`oci-advanced-networking` is the active workshop. Its tenancy manifest contains Introduction, three core labs, three optional extensions, and Cleanup. The sibling `oci-advanced-networking-tenancy` is retained as a historical source and was not modified during consolidation.

| Final section | Source and treatment |
| --- | --- |
| Lab 1: OCI Hub-and-Spoke | Original Lab 1 retained and expanded; address-plan table format and two actual screenshots merged from the tenancy workshop |
| Lab 2: OCI Bastion | Original Lab 4 renumbered; target endpoint security, application verification, and tunnel detail added |
| Lab 3: Network Command Center | Original Lab 5 renumbered; core prerequisites and same-region NPA analysis corrected |
| Optional Lab 4 | Tenancy workshop cross-tenancy LPG lab; high-level challenge with requestor and acceptor policies |
| Optional Lab 5 | Original Lab 2 renumbered; useful VPN/FastConnect/multicloud theory incorporated and outdated technical claims corrected |
| Optional Lab 6 | Original firewall steps replaced by a detailed introduction and one task linking to workshop 3872; source firewall manifest/introduction reviewed |
| Cleanup | Missing manifest target created, with dependency order and optional-resource scopes |

## Verification performed

* Parsed the final manifest and resolved all eight tutorial targets.
* Checked task numbering and local Markdown file/image references; no missing references.
* Preserved two actual screenshots and five SVG architecture diagrams, with descriptive alternative text. All seven image assets are at most 1180 pixels on either dimension.
* Visually inspected both screenshots and rasterized all five diagrams for layout review. Retained vector sources and updated titles, labels, endpoint placeholders, lab numbers, and the overview's core/optional distinction.
* Opened the actual Oracle LiveLabs viewer locally over HTTP. Navigated all eight sections and expanded task content. Confirmed all referenced image assets load, including lazy-loaded screenshots. No captured browser console errors.
* Moved the Azure HTML cloud-init sample to a downloadable YAML asset after discovering that the shared viewer's highlighting rendered HTML headings inside an inline YAML code block.
* Opened the live firewall destination and confirmed workshop 3872's title, six-lab outline, and catalog duration of five hours. The local source introduction estimates 3–5 hours; the guide explains this and recommends reserving five hours.
* Syntax-checked the Oracle Linux bootstrap with `bash -n` in WSL.
* Ran the diagnostic app locally: `/health`, `/json`, and `/` returned HTTP 200. Confirmed metadata-unavailable fallback outside OCI and HTML escaping of a supplied forwarded header.
* Confirmed that the installer embeds exactly the same Python source as the standalone app.

## Material technical corrections

* NPA's primary exercise is Spoke-1 ↔ Hub **within Ashburn**. Cross-region RPC and cross-tenancy LPG paths can be Indeterminate; live HTTP requests verify the complete RPC path. See [NPA caveats](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/path_analyzer.htm).
* Added documented NPA user/service IAM preflight and the broader read permission required by [Network Visualizer](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/network_visualizer.htm), with a facilitator demonstration option.
* Replaced broad all-protocol ingress with targeted TCP 8080 app NSGs and Bastion endpoint `/32` rules, allowing a meaningful ACCEPT/REJECT exercise.
* Supplied actual application bootstrap, host-firewall handling, readiness retry, and private endpoint verification.
* Corrected Audit language: Bastion API activity does not constitute shell/desktop session-content recording.
* Removed fixed public endpoint addresses and published demo VPN secrets. Azure [current route-based VpnGw AZ SKUs support IKEv1 and IKEv2](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-gateway-settings); the guide chooses IKEv2 explicitly.
* Added the missing Azure ExpressRoute gateway-to-circuit association and removed the unsupported suggestion that firewall hairpinning circumvents managed interconnect traffic restrictions.

## Validation boundary

This pass consolidates documentation and validates rendering, local asset integrity, bootstrap syntax, and the diagnostic app locally. **It does not re-execute the consolidated OCI/Azure provisioning flow.** Prior screenshots come from the earlier tenancy exercise, with a different resource naming/address plan; their captions identify the reusable console choice/status only.

Before the customer event, perform a targeted rehearsal of Lab 1 instance cloud-init, Lab 2 Managed SSH, and Lab 3 NPA IAM plus flow-log capture in the actual customer environment. The optional XRDP package path and multicloud gateway/circuit procedures also need live rehearsal if included in the agenda. Quotas, approved IAM scopes, network access, and provisioning waits remain environment-specific.

## Resource and cleanup status

No OCI, Azure, or customer-tenancy resources were created, changed, or deleted in this consolidation pass. Cleanup instructions were reviewed as documentation. Local preview and diagnostic servers were used only for QA.
