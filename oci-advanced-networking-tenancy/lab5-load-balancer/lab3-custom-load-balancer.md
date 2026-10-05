# Lab 3: Load Balancer Ingress

## Introduction

Deploy a private load balancer in the Hub VCN and distribute requests to the local Hub metadata app and the Remote metadata app. This validates the transit design with a shared ingress tier and backends in connected VCNs.

**Time:** 35 minutes

## Task 1: Create the private load balancer

In Region A, create a **private** flexible load balancer in `10.20.20.0/24`. Attach `advnet-<initials>-lb-nsg`, record its private frontend IP, and create:

* Backend set `metadata-backends`, policy **round robin**.
* HTTP health check on port `8080`, path `/`, interval 10 seconds, timeout 3 seconds, retries 3.
* HTTP listener on port `80` forwarding to `metadata-backends`.

## Task 2: Add and validate backends

Add `hub-1` and `remote-1` as port-8080 backends. Wait until both health states are **OK**.

Verify that the LB subnet routes `10.30.0.0/16` through DRG A; Remote routes `10.20.0.0/16` through DRG B; and the Remote app policy permits TCP 8080 from the LB NSG or, when cross-VCN NSG reference is unavailable, from the narrowly scoped LB subnet CIDR.

## Task 3: Test distribution

From `client-1`, run:

```bash
for i in {1..8}; do curl -s http://LB_PRIVATE_IP/ | grep -E 'hostname|displayName|privateIp'; done
```

Confirm that both `hub-1` and `remote-1` appear. The private frontend is reachable only from a network that has a route to Hub VCN.
