# Lab 5: Create, Inspect, and Delete Owned Resources

## Introduction

Exercise the complete operations flow: clarify a request, review a concrete plan, confirm it, observe asynchronous provisioning, and delete only the resources you created through this app.

**Estimated Time:** 25 minutes

### Objectives

- Launch a permitted Compute instance after explicit confirmation.
- Verify ownership records, live state, and activity history.
- Use both button-driven and natural-language deletion through the same confirmation path.
- Verify the app preserves unrelated resources.

### Prerequisites

- Lab 4 passed, including readiness and no-create-before-confirmation checks.
- Target compartment, approved subnet/image/shape, and quota/capacity for test instances are supplied by the facilitator.
- The event's permitted cost envelope includes one or two test instances up to 2 OCPU/16 GB and their boot volumes for this exercise.
- The author pilot has passed independent confirmation, ownership, and retry tests before attendee release.

## Task 1: Clarify and review a creation request

1. Enter:

    ```text
    Launch one compute instance with 2 OCPU and 16 GB of RAM for this workshop.
    ```

1. Answer the app's questions using the facilitator-approved configuration. If memory suggests a networking preference, verify that the chosen subnet and public-IP behavior satisfy it.

1. Review the proposed region, compartment, shape, image, subnet/IP choice, instance name, resource limits, and boot-volume behavior.

    **Expected result:** A concrete Review Action proposal appears. Nothing has been launched. If the configured subnet is unavailable or unauthorized, the app stops and reports the failed prerequisite; it does not invent a VCN or treat the failed lookup as an empty inventory.

1. Click **Confirm** once. Record the operation ID and subsequent instance OCID.

    **Observe:** The response acknowledges a tracked operation. Success requires the eventual lifecycle result, not merely an accepted API request.

## Task 2: Observe live resources and audit

1. Follow the operation until the instance is `RUNNING` or a terminal failure is displayed. Refresh Active Resources.

1. In the OCI Console, select the same region and target compartment. Open the created instance and compare its shape, memory, network, name, and workshop tags with the approved plan.

1. In Activity, inspect the confirmation, operation status, resource OCID, and sanitized request/error details. Refresh the completed plan: it should resolve to the same operation and must not permit another create.

    **Expected result:** One tracked instance matches one confirmed plan. Retry/duplicate-submission behavior must also be proved by the author acceptance suite. Tags support verification; they do not independently authorize deletion.

## Task 3: Delete using Active Resources

1. Click **Delete** on the created instance. Inspect the exact OCID in Review Action before confirming.

1. Confirm, observe `TERMINATING`, then verify `TERMINATED` in both the application and OCI. Verify that its created boot volume follows the agreed cleanup behavior.

    **Expected result:** The button creates a proposal and follows the same owner/scope/confirmation checks as chat. It does not directly terminate the instance.

## Task 4: Delete using natural language

1. Create one more permitted test instance using the same reviewed flow. Keep within the maximum of two active instances; delete earlier resources before adding more.

1. Enter:

    ```text
    Delete all compute instances that I have created through this workshop app.
    ```

1. Review the exact selected OCIDs and count. Verify every selected resource belongs to this deployment's authenticated owner/session and target compartment. Confirm only after the selection matches your recorded resource inventory.

1. Wait for termination and refresh the application and OCI Console. Compare the inventory of pre-existing resources recorded by the facilitator.

    **Expected result:** Only this app's tracked, live-verified owner/session resources are selected. Hosting infrastructure, foreign/pre-existing instances, and display-name matches are excluded. The author pilot must test rejection with a foreign resource OCID independently.

## Troubleshooting

- Capacity/quota failure: preserve the operation/request ID and error. Use a facilitator-approved alternative only after a new plan is reviewed. Do not keep retrying creates.
- Pending operation after restart: let the app reconcile the recorded operation against OCI. Ask the facilitator to inspect the cloud state before creating a replacement.
- Stale Active Resources: refresh against OCI and inspect the cache timestamp; a cached row is not proof of current state.
- Unexpected resource selected for deletion: cancel the proposal and stop the exercise until ownership logic is fixed and independently retested.
- Boot volume remains: verify the termination options and whether the volume belongs to this operation. Remove only the created volume through the approved cleanup procedure.

## Completion checkpoint and recap

You completed creation, live verification, both deletion paths, and audit review. Record operation/instance IDs and verify zero owned active test instances before cleanup. Identify which part of 'delete my instances' depends on application identity rather than OCI identity.

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
