# Lab 4: Validate the Application and Persistent Memory

## Introduction

Verify the deployed application using its actual resource principal, then test whether Oracle AgentMemory recalls a preference across authenticated sessions. Test failures as well as successful answers.

**Estimated Time:** 15 minutes

### Objectives

- Verify liveness, authenticated readiness, and the dashboard.
- Test memory persistence and user-scoped retrieval.
- Check the prompt refinement from Lab 2 in the running UI.
- Confirm that incomplete or disallowed requests create no resources.

### Prerequisites

- Lab 3 completed; the Container Instance is `ACTIVE` and `app-url.txt` contains its HTTPS application URL.
- The app access code has been delivered through the facilitator's protected channel.
- Database tables, memory store, model/embedding endpoints, and Vault/OCI permissions are prepared for the runtime identity.

## Task 1: Check liveness and authenticated readiness

1. From `files/starter`, check the public liveness endpoint:

    ```bash
    <copy>
    APP_URL="$(cat app-url.txt)"
    curl -fsS "${APP_URL%/}/health"
    </copy>
    ```

    **Expected result:** HTTP 200 and a minimal liveness response. A liveness response does not establish model, memory, database, or OCI access.

1. Open the HTTPS application URL in a browser. Log in using the protected access code. Confirm the Operations Command Center, Active Resources, and Activity tabs appear.

1. Confirm the authenticated readiness indicators report successful database, memory, model, and OCI checks. Readiness is backed by `/api/readiness`; a failed dependency must show a useful sanitized error and prevent resource operations.

    **Observe:** These calls now use the Container Instance principal. A successful Cloud Shell probe in Lab 1 did not test this identity.

## Task 2: Test persistent memory

1. Enter:

    ```text
    Remember that I prefer private subnets for test compute instances.
    ```

1. Confirm the app acknowledges the preference. Log out, then log back in to create a new authenticated session.

1. Enter:

    ```text
    What networking preference have I asked you to remember?
    ```

    **Expected result:** The response recalls private subnets using this deployment's authenticated owner scope. The exact wording may vary. Ask the facilitator to verify that memory was persisted through OracleAgentMemory, rather than only retained in browser/process state.

1. For the author pilot, also restart the same Container Instance and repeat the recall test after readiness returns. Record the restart/wait time separately; the facilitator may demonstrate this during the event.

    **Observe:** A remembered preference supplies context. It does not authorize a cloud action or override a new user choice.

## Task 3: Test clarification and rejected actions

1. Enter:

    ```text
    Launch a compute instance with 2 OCPU and 16 GB of RAM.
    ```

1. Review the clarification or proposal. Leave it unconfirmed. Refresh Active Resources and the OCI Compute list in the target compartment.

    **Expected result:** No instance is launched before confirmation. If required choices are missing, the app asks for them. Memory may provide a networking default, which still appears in Review Action.

1. Enter:

    ```text
    Launch an instance with 64 OCPU in a different compartment.
    ```

    **Expected result:** The configured scope/size limits reject the request and no resource is created.

1. Log out and attempt to reopen the resource view. Protected data and actions require login. In the author pilot, run the independent HTTP ownership/authentication tests as well; the UI test alone cannot prove those boundaries.

## Task 4: Inspect your prompt refinement

1. Log back in and generate a proposal using approved settings. Check whether Review Action implements the one measurable requirement you added in Lab 2.

1. Record pass/fail evidence against your expectation. If it fails, return the specific observed behavior and affected source to the relevant prompt, rebuild/redeploy once reviewed, and repeat the affected checks.

## Troubleshooting

- `/health` passes but readiness fails: inspect the named dependency and runtime logs. Verify resource-principal policies, model region, secret OCIDs, SQL grants, memory-store existence, and network/TLS access.
- Preference disappears: verify the authenticated owner remains stable, the SQL memory store is persistent, and extraction/embedding calls succeed. Do not broaden retrieval scope to find another user's memory.
- An unauthorized action succeeds or an instance appears without confirmation: stop resource exercises, record the evidence, and have the facilitator repair and retest the app.
- App fails after restart: inspect persisted plans/operations and startup recovery; do not repeat an ambiguous create request.

## Completion checkpoint and recap

Readiness passes, memory recall works across sessions, the unconfirmed/disallowed requests create no resources, and your UI refinement has been checked. Continue to operations. Explain why persisted memory and resource ownership need different database records.

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
