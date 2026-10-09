# Working application brief: Operations Command Center

Status: pilot design input. This brief supplies a generation target; the comprehensive app ADR will be approved separately. Implement these contracts consistently across generation stages.

## Stack and files

Use Python 3.11, FastAPI, Jinja2, plain JavaScript/CSS, the OCI Python SDK, python-oracledb, and oracleagentmemory. One application process listens on 0.0.0.0:8080. Follow contract.json exactly. Use absolute Python imports under app. Imports must have no network calls or database initialization side effects.

Use OCI SDK 2.187.2 and oracleagentmemory 26.8.0 as pilot dependency candidates. Resolve compatible FastAPI, Uvicorn, Jinja2, python-oracledb, and transitive dependencies during the author pilot, then lock them before attendee release. Include multipart support if using form-based login. Never invent library APIs; use the supplied SDK reference and report unresolved compatibility questions in architecture.json.

## Configuration and identity

Read these environment variables in Settings: OCI_REGION, TARGET_COMPARTMENT_ID, COMPUTE_SUBNET_ID, WORKSHOP_OWNER_ID, WORKSHOP_SESSION_ID, MODEL_COMPARTMENT_ID, MODEL_REGION, MODEL_ID, MEMORY_MODEL_ID, EMBEDDING_MODEL_ID, DB_USER, DB_DSN, DB_SECRET_OCID, APP_AUTH_SECRET_OCID, MEMORY_STORE_ID.

Each attendee gets one dedicated deployment and one server-configured owner. Fetch the app access code and DB password from the named Vault secrets through the resource principal. A login exchanges the app access code for an opaque, expiring server-side session cookie (HttpOnly, Secure, SameSite), checked on every protected API route. Reject unauthenticated requests. Derive ownership from the server session and Settings; never accept owner_id from a browser request or model response. Do not put secret values in logs, environment files, HTML, images, or model prompts. Serve the app behind a facilitator-prepared HTTPS endpoint.

The host compartment and managed-resource compartment are separate. The runtime principal has no resource-deletion authority over the host compartment. All Compute tools restrict operations to the configured target compartment and region.

## Interfaces

- config.py exports Settings and load_settings().
- planner.py exports Planner(settings, tools, memory, store). plan(text, owner_id, session_id) returns a serializable result: kind (clarification or proposal), message, and plan_id when a proposal is stored.
- oci_tools.py exports OciTools(settings). list_resources(owner_id, session_id), discover_options(), launch_compute(parameters, retry_token), and terminate_compute(instance_id, preserve_boot_volume=False). The executor validates every parameter before an SDK call.
- memory.py exports MemoryService(settings). recall(owner_id, query), remember(owner_id, user_text, assistant_text), and close(). Use user-scoped OracleAgentMemory retrieval and a pre-created memory store with SchemaPolicy.REQUIRE_EXISTING.
- store.py exports Store(settings). Persist plans, confirmations, operations, ownership records, and opaque sessions in relational tables. Publish explicit method signatures in architecture.json before generating implementation files.
- main.py exports a FastAPI instance named app and binds the interfaces above during application startup. Close database pools on shutdown.

## HTTP and UI contracts

Public GET /health returns 200 with a minimal liveness response and no resource details. Protected GET /api/readiness checks database, memory, model, and read-only OCI access and returns 200 only when required dependencies pass; otherwise 503 with sanitized diagnostics. Readiness must not create billable resources.

Use GET / for login/dashboard, POST /api/login, POST /api/logout, POST /api/chat with {text}, GET /api/resources, GET /api/plans/{plan_id}, POST /api/plans/{plan_id}/confirm, and GET /api/operations/{operation_id}. Publish request and response types in architecture.json. Bind confirmations to the authenticated owner, exact stored plan, version, expiry, and one-time consumption. Protect state-changing routes against CSRF and duplicate submissions.

UI tabs: Operations Command Center, Active Resources, and Activity. Show current region/compartment, dependency readiness, operation progress, and the model actually used. Review Action displays exact resource IDs or creation parameters. Confirm is an explicit user action. The Delete button creates the same deletion proposal as chat and does not bypass confirmation. Render model text and resource names safely; use textContent or escaped templates.

## Compute workflow

Core tools: discover available Compute shapes, images, and approved subnets; list owned instances; launch one instance; terminate selected owned instances. Keep a maximum of two non-terminated Compute instances per deployment. Cap requests at 2 OCPU and 16 GB. Allow only facilitator-approved shapes/images and the configured Compute subnet. Validate actual shape/image compatibility and capacity failures. Public/private intent should be resolved against real subnet and IP behavior; do not claim a private subnet can assign a public IP.

If required choices are missing, return a clarification without launching anything. If no authorized network is available, offer the advanced networking exercise and stop the core operation. An authorization error is a failed lookup, not an empty inventory. Automatic VCN/subnet creation is outside this core brief.

Before every action, validate an immutable stored plan and show the user the concrete configuration. Validate the plan again immediately before execution. Perform cloud work asynchronously relative to HTTP requests; record a durable operation and poll OCI lifecycle state. Display provisioning, running, terminating, terminated, and failed states accurately. Never equate an accepted request with successful completion.

Use an OCI retry token for creation, coupled with a unique database operation key. Retried confirmation must return the same operation, not launch a second instance. Account for process restart, multiple requests, and the non-atomic boundary between SQL transactions and cloud APIs. Do not blindly retry ambiguous resource creates.

Use server-generated tags workshop=prompt-engineering, owner=<owner>, session=<session>. Persist returned OCIDs and provenance in SQL. Resolve 'my instances' from server ownership records, then verify live compartment, region, and tags before termination. Tag matches alone do not authorize deletion. Never use display-name matching to establish ownership. Exclude the app hosting infrastructure and any pre-existing learner resources.

Track boot volumes associated with created Compute instances. Terminate with the agreed boot-volume cleanup behavior and verify it; preserve unrelated volumes. Record every confirmation, attempted action, result, OCI request/work-request ID when available, and failure without secrets.

## Database and memory

Use separate logical tables for resource ownership/cache, plans, operations, confirmations, sessions, and audit. Parameterize SQL. Provide table definitions in architecture.json for facilitator schema preparation. The runtime account gets the required grants and does not connect as ADMIN or create schemas at startup.

Use the same Autonomous AI Database for AgentMemory's managed store and relational application data. Read current resource state from OCI; cache it with a refresh timestamp. Memory is context, not authorization or the authoritative inventory. OCI-hosted LLM and embedding adapters use the resource-principal signer with the configured model region and compartment. MEMORY_MODEL_ID and EMBEDDING_MODEL_ID use the adapter's oci/ identifiers.

Extract durable preferences such as preferred networking or display-name prefixes. Treat remembered preferences as defaults which the user can correct. Store scoped thread messages, retrieve only the authenticated owner's memories, and demonstrate persistence after a new session/container restart. Never derive authorization from remembered text.

## Acceptance targets for the author pilot

1. A request for 2 OCPU/16 GB asks for missing choices and creates nothing before confirmation.
2. Repeated Confirm produces one operation and one instance.
3. Active Resources refreshes against OCI and shows the created instance.
4. A new authenticated session recalls an explicitly stored preference.
5. An unauthenticated request and a browser-supplied owner override are rejected.
6. 'Delete all my compute instances' selects only this owner/session's tracked resources; foreign/pre-existing resources are excluded.
7. Deletion via button and chat follows the same exact-ID confirmation and ownership checks.
8. Quota/capacity/model/network failures produce a useful error and a durable audit record.
9. Resource tags, owner records, confirmations, and operations survive a container restart.
10. Cleanup verifies instance and associated boot-volume removal, preserving the bootstrap infrastructure.

Generated self-tests cannot establish these acceptance targets by themselves. The facilitator will provide independent tests after the comprehensive ADR is approved.
