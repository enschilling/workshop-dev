# Lab 4: Secure Access — OCI Bastion

## Introduction

The test VMs you built have **no public IP addresses** — by design. In this lab you provide audited, time-bound, just-in-time access to those private hosts using the **OCI Bastion** service: no self-managed jump box, no public IPs, no standing SSH exposure. You create a Bastion in Spoke-1 and use it three ways — a **Managed SSH** session, an **SSH port-forwarding** session, and **RDP over SSH** to a graphical desktop.

*Estimated Time:* 30 minutes

### About OCI Bastion

Bastion provides restricted, temporary SSH access to resources that have private IPs. Key facts that shape this lab:

* **Three session types:** *Managed SSH* (to Linux hosts running the Cloud Agent Bastion plugin), *SSH port-forwarding* (tunnel to a specific host:port), and *Dynamic port-forwarding (SOCKS5)*.
* **VCN-bound:** a Bastion is attached to one VCN and can only reach targets in that VCN. This is why the Bastion lives in **Spoke-1** and targets the **Spoke-1** host.
* **Time-bound:** sessions last up to **3 hours**, then expire automatically.
* **Allowlisted and audited:** access is scoped to a CIDR allowlist, governed by IAM, and every session is recorded in the **Audit** log.

### Objectives

In this lab, you will:

* Create a Bastion with a private endpoint in Spoke-1
* Open a **Managed SSH** session to the Spoke-1 Linux VM
* Open an **SSH port-forwarding** session to a service port
* Connect to a graphical desktop via **RDP over SSH** (XRDP on Oracle Linux)
* Review the session in the Audit log

### Prerequisites

This lab assumes you have:

* Completed **Lab 1**, with a Spoke-1 test VM (private IP, no public IP) and its SSH key pair
* Permissions equivalent to `manage bastion-family`, plus `read instance-agent-plugins`
* An SSH client locally; an RDP client (for Task 4)

## Task 1: Prepare the target and create the Bastion

1. **Enable the Bastion plugin on the target VM.** Managed SSH requires the **Cloud Agent → Bastion** plugin. Open the Spoke-1 VM (`advnet-spoke1-vm`) → **Oracle Cloud Agent** tab → toggle **Bastion** to **Enabled**. Allow a few minutes for the plugin to report **Running**.

   ![Enable the Bastion Cloud Agent plugin on the target VM](images/lab4-01-agent-plugin.png)

2. **Service Gateway route (if needed).** The Cloud Agent reaches the Bastion service over the Oracle Services Network. Confirm the Spoke-1 private subnet route table has a **Service Gateway** route for *All <region> Services* (added in Lab 1, Task 2).

3. **Create the Bastion.** Go to **Identity & Security → Bastion → Create Bastion**:

   * **Name:** `advnet-bastion`
   * **Compartment:** `advnet-workshop`
   * **Target Virtual Cloud Network:** `advnet-spoke1-vcn`
   * **Target Subnet:** `advnet-spoke1-private`
   * **CIDR Block Allowlist:** your workstation's public IP as a `/32` (look it up; do **not** use `0.0.0.0/0`)

   ![Create Bastion with a scoped CIDR allowlist](images/lab4-02-create-bastion.png)

4. Click **Create Bastion** and wait for **Active**.

## Task 2: Managed SSH session

1. Open `advnet-bastion → Create Session`:

   * **Session type:** **Managed SSH session**
   * **Compute instance:** `advnet-spoke1-vm`
   * **Username:** `opc` (Oracle Linux default)
   * **Add SSH key:** paste the **public** key matching the private key you saved in Lab 1

   ![Create a Managed SSH session](images/lab4-03-managed-ssh.png)

2. After the session becomes **Active**, click the **⋮** menu → **Copy SSH command**. Run it locally:

   ```
   ssh -i <your-private-key> -o ProxyCommand="ssh -i <your-private-key> -W %h:%p -p 22 ocid1.bastionsession...@host.bastion.<region>.oci.oraclecloud.com" opc@10.1.0.x
   ```

   You land on the Spoke-1 host's shell — with no public IP anywhere in the path.

## Task 3: SSH port-forwarding session

Use this to reach a specific service port on the private host (for example, a local web app on `:8080`).

1. Create another session:

   * **Session type:** **SSH port forwarding session**
   * **IP address / instance:** `advnet-spoke1-vm` (`10.1.0.x`)
   * **Port:** the target port (e.g. `8080`)

2. Run the generated command, which binds a local port to the remote service:

   ```
   ssh -i <key> -N -L 8080:10.1.0.x:8080 -p 22 <session-ocid>@host.bastion.<region>.oci.oraclecloud.com
   ```

   Browse to `http://localhost:8080`. Traffic is tunneled through the Bastion to the private host.

   ![SSH port-forwarding session reaching a private service](images/lab4-04-port-forward.png)

## Task 4: RDP over SSH (graphical desktop)

To avoid Windows licensing cost, this lab installs **XRDP** on the Oracle Linux host and tunnels RDP (port 3389) through a Bastion port-forwarding session. *(A small Windows VM is the alternative if you specifically need a Windows desktop.)*

1. **Install a desktop + XRDP on the target** (over your Managed SSH session from Task 2):

   ```
   sudo dnf groupinstall -y "Server with GUI"
   sudo dnf install -y epel-release && sudo dnf install -y xrdp
   sudo systemctl enable --now xrdp
   sudo firewall-cmd --add-port=3389/tcp --permanent && sudo firewall-cmd --reload
   sudo passwd opc   # set a password for the RDP login
   ```

2. **Create a port-forwarding session to 3389:**

   * **Session type:** SSH port forwarding session
   * **IP address:** `10.1.0.x` · **Port:** `3389`

3. Run the generated command, mapping a local port (e.g. 3389) to the host's 3389:

   ```
   ssh -i <key> -N -L 3389:10.1.0.x:3389 -p 22 <session-ocid>@host.bastion.<region>.oci.oraclecloud.com
   ```

4. Open your **RDP client** and connect to **`localhost:3389`**. Log in as `opc` with the password you set. You get a full graphical desktop on the private host — over RDP, tunneled through SSH, through the Bastion.

   ![RDP client connected to the private host through the Bastion tunnel](images/lab4-05-rdp.png)

## Task 5: Review the Audit log

1. Go to **Observability & Management → Audit**, filter to the Bastion resource, and locate the **CreateSession** / connection events.

2. Note the recorded principal, source, and timestamp — every Bastion session is captured, which is the compliance story for just-in-time access.

   ![Bastion session recorded in the Audit log](images/lab4-06-audit.png)

## Lab Recap

You provided secure, audited access to private hosts with no public IPs:

* A Bastion in Spoke-1 with a scoped CIDR allowlist
* A **Managed SSH** session (via the Cloud Agent Bastion plugin)
* An **SSH port-forwarding** session to a service port
* **RDP over SSH** to a graphical desktop (XRDP on Oracle Linux)
* The session captured in the Audit log

Sessions expire automatically within three hours — access is temporary by construction.

## Learn More

* [OCI Bastion overview](https://docs.oracle.com/en-us/iaas/Content/Bastion/Concepts/bastionoverview.htm)
* [Managing bastion sessions](https://docs.oracle.com/en-us/iaas/Content/Bastion/Tasks/managingsessions.htm)
* [Connecting to sessions (SSH, port forwarding)](https://docs.oracle.com/en-us/iaas/Content/Bastion/Tasks/connectingtosessions.htm)

## Acknowledgements

* **Author** — Eli Schilling, Technical Engagement Services, Oracle
* **Contributors** — Oracle LiveLabs Platform Team
* **Last Updated By/Date** — Eli Schilling, June 2026
