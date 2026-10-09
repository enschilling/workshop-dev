# Lab 6: Clean Up and Review the Workshop

## Introduction

Verify that created resources are removed, preserve the facilitator's bootstrap infrastructure, and summarize the prompting techniques you tested.

**Estimated Time:** 10 minutes

### Objectives

- Verify test instance and associated boot-volume cleanup.
- Delete the exact application Container Instance created in Lab 3.
- Record what was generated, repaired, deployed, and validated.
- Distinguish workshop-created resources from shared/prepared infrastructure.

### Prerequisites

- Resource IDs and deployment output from Labs 3 and 5.
- The event cleanup policy from the facilitator.
- Cloud Shell is in `files/starter`; the OCI session is still authenticated.

## Task 1: Verify managed-resource cleanup

1. Use Active Resources and the OCI Console to verify that all Compute instances created through this deployment are terminated. Compare exact recorded OCIDs, region, and target compartment.

1. Verify removal of the boot volumes created with those instances according to the approved termination behavior. If a volume remains, confirm its provenance before following the facilitator's exact-ID cleanup procedure.

1. Preserve pre-existing instances, hosting networking, ADB, IAM, Vault secrets, and shared registry/bootstrap resources. Their cleanup is owned by the facilitator unless the event specifically assigns it to you.

    **Expected result:** Zero owned active Compute instances and no unintended created boot-volume residue. Save sanitized inventory evidence before deleting the app.

    **Observe:** An empty application cache is not cleanup evidence. Reconcile your recorded resource IDs against live OCI state.

## Task 2: Delete the application Container Instance

1. Derive the exact Container Instance ID from your own Lab 3 output and inspect the resource:

    ```bash
    <copy>
    RESOURCE_REGION="$(python -c 'import json; print(json.load(open("deployment.json"))["region"])')"
    CONTAINER_INSTANCE_ID="$(python -c 'import json; print(json.load(open("container-instance-result.json"))["data"]["id"])')"
    oci container-instances container-instance get --region "$RESOURCE_REGION" --container-instance-id "$CONTAINER_INSTANCE_ID" --query 'data.{name:"display-name",id:id,state:"lifecycle-state",tags:"freeform-tags"}'
    </copy>
    ```

1. Confirm the displayed name, session tag, OCID, and region match the application you created. Delete that exact resource; leave the CLI's confirmation prompt enabled:

    ```bash
    <copy>
    oci container-instances container-instance delete --region "$RESOURCE_REGION" --container-instance-id "$CONTAINER_INSTANCE_ID" --wait-for-state SUCCEEDED --max-wait-seconds 600 > container-instance-delete.json
    </copy>
    ```

    **Expected result:** The delete work request completes successfully. Verify in the OCI Console that the Container Instance is deleted. If the client times out, inspect the work request before retrying.

1. Log out of the registry:

    ```bash
    <copy>
    podman logout "$REGISTRY_DOMAIN"
    </copy>
    ```

    If the shell variables were lost, obtain the registry domain from the facilitator's repository path first. The facilitator removes workshop image versions/repositories and revokes temporary tokens according to the event policy.

## Task 3: Record evidence and recap

1. Complete the [learner evidence worksheet](../files/starter/evidence.md) with identifiers and results, excluding tokens, credentials, and secret values.

1. Discuss:

    - Which prompt constraint improved the generated app, and what evidence supports that observation?
    - Which problems required better SDK context rather than a longer prompt?
    - Which checks could syntax validation establish, and which required the deployed app?
    - Why do resource-principal access, authenticated user scope, and memory scope need separate controls?
    - How would you extend the app to create networking while preserving limits and cleanup ordering?

1. Compare your generation/repair/deployment/wait times with the planning allocation. Record facilitator interventions and any recovery artifact used.

## Troubleshooting

- Cleanup state is uncertain: reconcile the exact recorded IDs with OCI and work requests before retrying deletes.
- Resources appear missing: check region, compartment, and identity before treating absence as successful cleanup.
- The Sandbox reservation expires first: have the facilitator verify reservation cleanup; do not report manual cleanup as passed without evidence.

## Completion checkpoint and recap

Record cleanup as verified, partially verified, or pending, with exact remaining IDs when needed. The workshop is complete when created resources are accounted for, the application Container Instance is deleted, and the evidence worksheet records the actual outcomes.

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
