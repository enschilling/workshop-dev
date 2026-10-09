# Facilitator preparation

This is the preparation contract for the Sandbox draft. A repeatable bootstrap stack will be implemented after the comprehensive application ADR is approved. Do not run an attendee event from this document alone.

## Environment to prepare

Provide one host deployment and a managed-resource compartment per attendee. Keep the compartments distinct. Select one tested region for the Compute/Container Instances resources; record a separate model region when required. The first draft targets x86_64 builds and CI.Standard.E4.Flex, subject to actual region, quota, and capacity.

- An existing hosting subnet and NSG, with access to a facilitator-managed HTTPS front door, OCI APIs, OCIR, model endpoints, and ADB.
- An approved Compute subnet, image and shape allowlist, and quota/capacity for two test instances up to 2 OCPU/16 GB each.
- Quota/capacity for one E4 Container Instance at 1 OCPU/8 GB per attendee.
- A private OCIR repository per attendee and tested learner push authentication.
- A Container Instances dynamic group, private-image read permission, model/embedding/Vault access, and narrowly scoped Compute/network-use permissions. Attendees do not create IAM policies.
- An Autonomous AI Database at a compatible version, memory store initialized by its owner, application SQL objects, runtime grants, and tested TLS/network connectivity.
- Vault secrets for the runtime database credential and application access code. Provide their OCIDs, never their values in config files.
- Stable non-personal owner/session/memory identifiers and protected bootstrap-output delivery.
- A facilitator-approved repository commit for downloading the starter kit.

Container Instance membership can use a rule such as `ALL {resource.type='computecontainerinstance', resource.compartment.id = '<hosting-compartment-ocid>'}`. Use the official [policy reference](https://docs.oracle.com/en-us/iaas/Content/container-instances/permissions/policy-reference.htm) to construct the final policies. Do not give the runtime principal tenancy-wide manage access. Compartment-scoped IAM is the outer boundary; the application still enforces ownership within it.

## Inputs delivered to attendees

| Input | Use | Handling |
| --- | --- | --- |
| Workshop commit/ref | Download reproducible starter content | Public or authenticated repository access |
| Model region/compartment/model identifier | config.json | Non-secret identifiers |
| Hosting/target compartment, AD, subnets, NSGs | deployment.json | Non-secret identifiers |
| OCIR repository path and login username | Image push | Non-secret; auth token entered interactively |
| Model and embedding adapter identifiers | Runtime memory | Non-secret, tested oci/ model names |
| DB user/DSN, memory-store identifier | Runtime database | Non-secret configuration |
| DB/app-auth secret OCIDs | Runtime Vault reads | OCIDs only |
| App access code | HTTPS login | Protected delivery; never in source or run records |

## Pilot checks

Test using the actual learner identity, then the actual Container Instance identity. Record status, request IDs, image digest, architecture, model identifiers, package versions, database version, repair counts, and timings.

1. Download the pinned starter revision in Cloud Shell; validate session authentication and generic on-demand inference.
2. Verify package/base-image access, native x86_64 build, registry push, and private image pull.
3. Finalize and run generated schema preparation through the schema owner; prove runtime has only required SQL grants.
4. Generate all stages, independently review source, and run the app acceptance suite.
5. Deploy and verify /health, authenticated /api/readiness, HTTPS, session authentication, and OCI access.
6. Verify AgentMemory extraction/search/persistence with resource-principal adapters and cross-owner rejection.
7. Create, list, and delete an owned instance; confirm duplicate submission does not duplicate resources.
8. Validate failure paths: quota, capacity, unavailable model, invalid owner, expired plan, failed inventory lookup.
9. Verify cleanup of instances and their created boot volumes; preserve bootstrap resources.

## Recovery and event readiness

Set a maximum of two attendee repair attempts before facilitator intervention. A tested generated source checkpoint and a digest-pinned image must be published after the benchmark; this increment contains neither. Record fallback use distinctly from successful generation.

Keep automatic VCN creation outside the core path until IAM, routes, gateways, CIDR choices, cleanup ordering, and user confirmation are approved and tested.

Use the workshop-validation skill's scoped Sandbox assessment and append-only evaluation history. Static scores cannot override unresolved live gates. Calibrate the 120-minute core allocation plus 30-minute allowance with a human pilot before selecting an event slot.
