# Lab 2: Secure Access — OCI Bastion

## Introduction

The hosts from Lab 1 have **no public IP addresses**. You will use **OCI Bastion** to reach the Spoke-1 host through a time-bound Managed SSH session, then tunnel a browser connection to its private diagnostic web page. From the Spoke-1 shell you will make actual HTTP requests to the Hub and Remote-Spoke, proving that local and cross-region peering carry application traffic.

The customer scenario is an engineer who needs temporary access to troubleshoot a private application. IAM controls who can create a session, the Bastion's client CIDR allowlist controls where the engineer can connect from, and the target's network and host rules control the permitted destination. Optional RDP-over-SSH extends the same pattern to a graphical desktop.

**Estimated time:** 35–45 minutes for Tasks 1–3 and 5; add 20–30 minutes or more for the optional graphical desktop.

### About OCI Bastion

Bastion supports Managed SSH, fixed-port forwarding, and dynamic SOCKS5 forwarding. A Managed SSH target requires a supported Linux image, SSH server, Oracle Cloud Agent, and a running Bastion plugin. Fixed-port forwarding does not require that plugin. A Bastion is associated with one VCN and cannot directly target a host in another VCN; the session in this lab targets **Spoke-1**. See the [Bastion overview](https://docs.oracle.com/en-us/iaas/Content/Bastion/Concepts/bastionoverview.htm).

### Objectives

* Create a Bastion with a narrowly scoped client CIDR allowlist.
* Permit its private endpoint to reach the Spoke-1 host.
* Use Managed SSH to check bootstrap, the diagnostic service, and live peering.
* Tunnel TCP 8080 to the workstation and view the private application.
* Optionally tunnel RDP and review Bastion API activity in Audit.

### Prerequisites

* Completed Lab 1, including the three private IPs and application NSGs.
* A local SSH client and the private key corresponding to the public key placed on Spoke-1.
* Bastion, networking, instance-read, instance-agent-plugin-read, and work-request permissions from the Introduction.
* The public egress IP of your workstation. If connected through a corporate VPN or proxy, use the address OCI will see.

## Task 1: Prepare Spoke-1 and create the Bastion

1. Switch to **Ashburn** and confirm the working compartment.
2. Open `advnet-spoke1-vm → Oracle Cloud Agent`. Enable the **Bastion** plugin if needed and wait for **Running**. Do not proceed with Managed SSH while it is stopped or still starting.
3. Confirm the Spoke-1 private subnet's route table retains its regional **Service Gateway** route and NAT default. Verify outbound access is permitted; the agent must be able to contact its service endpoints.
4. Open **Identity & Security → Bastion** and select **Create Bastion**. Use:

   | Field | Value |
   | --- | --- |
   | Name | `advnet-bastion` |
   | Compartment | Your working compartment |
   | Target VCN | `advnet-spoke1-vcn` |
   | Target subnet | Spoke-1 private subnet, `10.1.0.0/24` |
   | Client CIDR allowlist | Your workstation's public egress IP followed by `/32` |
   | Session TTL | Use a duration long enough for the lab, within the console's permitted range |

5. Create the Bastion and wait for **Active**. Record its OCID and **private endpoint IP address** from the details page. This endpoint IP and the workstation's public IP have different roles; do not interchange them.
6. In `advnet-spoke1-app-nsg`, add the following **stateful ingress** rules. Use the endpoint's actual address with `/32`:

   | Source | Protocol / destination port | Purpose |
   | --- | --- | --- |
   | `<bastion-private-endpoint-ip>/32` | TCP / 22 | Managed SSH |
   | `<bastion-private-endpoint-ip>/32` | TCP / 8080 | Private web port-forwarding |

7. Confirm that NSG is attached to the Spoke-1 primary VNIC. Keep default SSH host-firewall access and the application's TCP 8080 host-firewall rule from bootstrap.

**Expected result:** an Active Bastion, a Running plugin, an allowlisted workstation, and target rules permitting the Bastion endpoint on the two required ports.

## Task 2: Use Managed SSH and verify the live application paths

1. Open `advnet-bastion` and select **Create Session**:

   | Field | Value |
   | --- | --- |
   | Session type | Managed SSH session |
   | Target instance | `advnet-spoke1-vm` |
   | Username | `opc` |
   | SSH key | Your public key |

2. Wait for **Active**. Use the session's actions menu to **Copy SSH command**. Paste the command into a local terminal, replace its private-key placeholder with your local key path, and retain the generated hostname, session OCID, and proxy options.
3. Connect. On Unix-like clients, restrict the key file to the owner with `chmod 600 <private-key>` if needed. On Windows OpenSSH, keep the key in an owner-accessible location and correct its ACL if OpenSSH reports an overly permissive key.
4. On the **Spoke-1 shell**, verify bootstrap and the application:

   ```bash
   sudo cloud-init status --wait
   sudo systemctl status oci-metadata-app --no-pager
   curl --fail --max-time 10 http://127.0.0.1:8080/health
   curl --fail --max-time 10 http://127.0.0.1:8080/
   ```

   **Expected:** cloud-init completes, the service is active, the health endpoint returns `ok`, and the page identifies Spoke-1. If it fails, inspect:

   ```bash
   sudo tail -n 80 /var/log/cloud-init-output.log
   sudo journalctl -u oci-metadata-app -n 50 --no-pager
   sudo ss -lntp | grep ':8080'
   ```

   A failed package download usually points to outbound routes, security, DNS, or repositories. Fix the underlying issue before reinstalling or creating a replacement VM.

5. Set worksheet values in the **Spoke-1 shell**. Replace both placeholders with actual private IPs:

   ```bash
   HUB_IP='<hub-private-ip>'
   REMOTE_IP='<remote-spoke-private-ip>'
   curl --fail --connect-timeout 5 --max-time 15 "http://$HUB_IP:8080/"
   curl --fail --connect-timeout 5 --max-time 15 "http://$REMOTE_IP:8080/"
   ```

6. Read the responding hostname and region in each HTML response. The first proves **same-region Spoke-1 → Hub** traffic through the Ashburn DRG; the second proves **cross-region Spoke-1 → Remote-Spoke** traffic through the RPC. TCP responses exercise the return path too.
7. Record source, destination, port, responding hostname/region, and result. Save the successful tests for Lab 3. Do not run these private-IP commands from a workstation without private connectivity; run them on Spoke-1 through Bastion.

### If SSH or a peer application fails

| Symptom | First checks |
| --- | --- |
| Bastion connection times out | Session state/expiry, workstation egress IP and allowlist, local outbound TCP 22 |
| Session cannot reach the host | Bastion endpoint `/32` rule, VNIC NSG association, host SSH service, plugin status |
| `curl` reports connection refused | Correct destination IP, service listening on 8080, bootstrap/service logs |
| Local page works but peer request times out | Both subnet routes, DRG incoming-attachment table and outgoing attachment, RPC state for Phoenix, target NSG and host firewall |
| Only one endpoint responds | Check the failed endpoint's region, route table and bootstrap separately |

If a remote host's bootstrap needs investigation, create a temporary Bastion **in that host's own VCN**, with the corresponding endpoint security rule. A Spoke-1 Bastion session cannot directly target the other VCN. Add temporary resources to your cleanup inventory.

## Task 3: Tunnel the private web page to your workstation

1. Create a second Bastion session with type **SSH port forwarding**, target **Spoke-1's private IP**, destination port **8080**, and your public key.
2. Wait for Active and copy the generated SSH command. Replace the private-key path. Set its local bind to `127.0.0.1:18080` while retaining the target IP, port, and generated session endpoint. The command has this shape; use the console's actual values:

   ```bash
   ssh -i <private-key-path> -N \
     -L 127.0.0.1:18080:<spoke1-private-ip>:8080 \
     -p 22 <session-ocid>@<generated-bastion-hostname>
   ```

3. Keep that terminal running. Open **`http://127.0.0.1:18080`** in your local browser.
4. Verify the page identifies **Spoke-1**, although the browser is using localhost. The application request's client address reflects the Bastion path rather than a new public IP on the instance.
5. Stop the SSH tunnel with **Ctrl+C** and refresh. The page should no longer load. Restart while the session is Active if you need it for the next tasks.

**Observe:** the same private service is accessible through two distinct paths: another workload's DRG/RPC route, and your workstation's Bastion tunnel. Neither requires a public IP on the target.

## Task 4: Optional RDP over SSH — graphical desktop

This exercise preserves the original workshop's RDP use case. It is optional because a desktop requires more memory, package installation time, and compatible packages. Use a facilitator-approved **x86 Oracle Linux 9** host with adequate resources; if the core Spoke-1 host is A1 or too small, use a separate private x86 host **in Spoke-1**, record its IP, and apply the same endpoint rules. Include it in cleanup.

1. Connect to the approved target through Managed SSH. Review disk and memory capacity. Install a desktop and enable the Oracle Linux EPEL repository:

   ```bash
   sudo dnf group install -y "Server with GUI"
   sudo dnf install -y oracle-epel-release-el9
   sudo dnf info xrdp xorgxrdp
   ```

   Confirm both packages are available for your image and architecture before proceeding. If they are unavailable, use a supported Windows/RDP target in the same VCN with the facilitator, or skip this extension.

2. Install and start XRDP, and create a dedicated desktop user:

   ```bash
   sudo dnf install -y xrdp xorgxrdp
   sudo useradd -m labdesktop
   sudo passwd labdesktop
   sudo systemctl enable --now xrdp
   sudo firewall-cmd --add-port=3389/tcp
   sudo firewall-cmd --permanent --add-port=3389/tcp
   ```

   Set the password interactively. Do not place it in your notes. Verify the service and listening port with `systemctl status xrdp` and `ss -lntp`. Leave SELinux enabled; inspect service logs if startup fails.

3. Add stateful **TCP 3389 ingress from the Bastion endpoint `/32`** to the target's NSG. Do not expose RDP to the public internet.
4. Create a Bastion **SSH port-forwarding session** to the desktop target's private IP, port **3389**. Run the generated command with local bind `127.0.0.1:13389`:

   ```bash
   ssh -i <private-key-path> -N \
     -L 127.0.0.1:13389:<desktop-private-ip>:3389 \
     -p 22 <session-ocid>@<generated-bastion-hostname>
   ```

5. Open your RDP client, connect to **`127.0.0.1:13389`**, and log in as `labdesktop`. On Windows: `mstsc /v:127.0.0.1:13389`.
6. Close the desktop session and stop the tunnel. Record the extra host and RDP rule if you created them.

## Task 5: Review Audit and end the sessions

1. Open **Observability & Management → Audit** in Ashburn. Select the working compartment and a time range covering session creation.
2. Find Bastion-related API events such as **CreateSession**. Record the initiating principal, resource, timestamp, and operation outcome.
3. Explain what this proves: who requested a session and when. OCI Audit API events are **not a recording of shell commands or desktop contents**.
4. Stop local tunnels and delete the test sessions when finished, or retain one active Managed SSH session briefly for Lab 3. Sessions expire at their configured TTL; recreate an expired session rather than changing instance exposure.

## Lab Recap and checkpoint

You accessed a private host through Managed SSH, verified its web service, proved local and cross-region HTTP reachability, and opened the page through a workstation tunnel. The optional desktop exercise demonstrates that the same tunnel can carry RDP.

Save the Bastion OCID/endpoint IP, the endpoint security rules, session types, three endpoint test results, and the Audit API event. Keep the Spoke-1 SSH method available for Lab 3's live traffic tests.

## Learn More

* [OCI Bastion overview](https://docs.oracle.com/en-us/iaas/Content/Bastion/Concepts/bastionoverview.htm)
* [Managing Bastion sessions](https://docs.oracle.com/en-us/iaas/Content/Bastion/Tasks/managingsessions.htm)
* [Connecting to sessions](https://docs.oracle.com/en-us/iaas/Content/Bastion/Tasks/connectingtosessions.htm)

## Acknowledgements

* **Author** — Eli Schilling, Technical Engagement Services, Oracle
* **Contributors** — Oracle LiveLabs Platform Team
* **Last Updated By/Date** — Eli Schilling, October 2026
