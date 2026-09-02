# Lab 5: Load Balancer Ingress

## Introduction

Deploy a private load balancer in the Hub VCN and distribute HTTP requests to local and remote metadata apps. This proves that VCN/DRG/RPC routing supports a frontend in one VCN and a backend in another region when the path and policy are complete.

**Time:** 35 minutes

## Task 1: Create the private load balancer

In Region A, create a **private** flexible load balancer in `10.20.20.0/24`. Attach `advnet-<initials>-lb-nsg`, reserve sufficient minimum and maximum bandwidth for the exercise, and record the private frontend IP. Create:

* Backend set `metadata-backends`, policy **round robin**.
* HTTP health check on port `8080`, path `/`, interval 10 seconds, timeout 3 seconds, retries 3.
* HTTP listener on port `80` forwarding to `metadata-backends`.

## Task 2: Add local and remote backends

Add `hub-1` and `remote-1` as backend servers on port `8080`. Wait until both health states are **OK**. Do not mark a backend as healthy by bypassing the health check: resolve the failed path or policy.

The following checks are normally required:

| Check | Expected setting |
| --- | --- |
| LB subnet route | `10.30.0.0/16 → DRG A` |
| DRG/RPC imports | Hub/LB subnet can reach Remote VCN and return route exists |
| Remote VCN route | `10.20.0.0/16 → DRG B` |
| Remote app NSG | TCP 8080 allowed from LB NSG or narrowly scoped LB subnet CIDR |
| Hub app NSG | TCP 8080 allowed from LB NSG |

If the console does not allow an NSG reference across the needed scope, use the load-balancer subnet CIDR (`10.20.20.0/24`) as the app ingress source, document the exception, and keep it limited to TCP 8080.

## Task 3: Test distribution

From `client-1`, repeat the following request. The `X-Forwarded-For`/remote-address fields and instance details make the traffic path visible.

```bash
for i in {1..8}; do curl -s http://LB_PRIVATE_IP/ | grep -E 'hostname|displayName|privateIp'; done
```

Confirm responses alternate between `hub-1` and `remote-1`. A private frontend means this test must originate from a network with a route to the Hub VCN; it is not reachable from the public internet.

**Checkpoint:** Capture the two healthy backend states and successful responses from both servers through the listener.
