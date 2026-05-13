# Cleanup: Remove Workshop Resources

## Introduction

In this cleanup lab, you will remove the temporary resources created during the OCI Tagging Masterclass. Cleanup is especially important if you created compute instances, block volumes, budgets, IAM test users, events rules, functions, or resource schedules in a shared tenancy.

**Estimated Time:** 15-20 minutes

### Objectives

In this lab, you will:

- Terminate the compute instance created for bulk tagging.
- Delete block volumes and Object Storage buckets created for the workshop.
- Delete budget alert rules and budgets created for the workshop.
- Delete Events rules, Resource Scheduler schedules, Functions applications, IAM policies, dynamic groups, and test IAM users.
- Retire workshop tag defaults and tag definitions if they are no longer needed.

### Prerequisites

This lab assumes you have:

- Completed the previous labs.
- Administrative access to the workshop compartment and IAM resources.
- The names or OCIDs of the resources you created.

## Task 1: Delete Compute, Block Volume, and Object Storage Resources

1. Navigate to **Compute > Instances** and terminate any workshop test instances, such as `LabCompute1` or non-compliant instances created in Lab 6.

2. Navigate to **Block Storage > Block Volumes** and delete workshop volumes, such as `LabVolume1` and `LabVolume2`.

3. Navigate to **Object Storage > Buckets** and delete workshop buckets, such as `tag-test-bucket`, `tag-test-bucket-cli`, or any bucket name that starts with `lab-tagging-bucket`.

4. If you prefer CLI cleanup, use commands like:

    ```bash
    <copy>
    oci compute instance terminate --instance-id <instance_ocid> --force
    oci bv volume delete --volume-id <volume_ocid> --force
    oci os bucket delete --namespace-name <object_storage_namespace> --bucket-name <bucket_name> --empty --force
    </copy>
    ```

## Task 2: Delete Budgets and Alert Rules

1. Navigate to **Billing & Cost Management > Budgets** in your home region.

2. Open each workshop budget and delete its alert rules.

3. Delete the workshop budget.

    ```bash
    <copy>
    oci budgets budget alert-rule delete --budget-id <budget_ocid> --alert-rule-id <alert_rule_ocid> --force
    oci budgets budget budget delete --budget-id <budget_ocid> --force
    </copy>
    ```

## Task 3: Delete Automation Resources

If you completed Labs 5 or 6, remove the automation resources in this order:

1. Delete Resource Scheduler schedules such as `daily-tag-default-update`.
2. Delete Events rules such as `enforce-tags-on-instance-launch`.
3. Delete functions such as `tag-update`, `scheduled-tag-scan`, and `event-tag-check`.
4. Delete Functions applications such as `tag-update-app` and `tag-enforcement-app`.
5. Delete IAM policies such as `TagManagementPolicy` or `TagAutoUpdatePolicy`.
6. Delete dynamic groups such as `FunctionsTagManagement`.

## Task 4: Delete IAM Test Users and Groups

1. Delete test users created for tag-based access control, such as `tagtestuser`.
2. Delete test groups such as `TagTestUsers`.
3. Delete tag-based access control policies such as `TagDeleteRestrictionDenyPolicy`.

## Task 5: Retire Tag Defaults and Tag Definitions

Only remove tags if they were created solely for this workshop and are not used by other teams or resources.

1. Navigate to **Identity & Security > Compartments**, open your workshop compartment, and select **Tag Defaults**.
2. Delete tag defaults such as `LLTagNamespace.Environment` or `LLTagNamespace.ExpirationDate`.
3. Navigate to **Governance & Administration > Tag Namespaces** and open `LLTagNamespace`.
4. Retire tag definitions such as `CostCenter`, `Environment`, and `ExpirationDate` if they are no longer needed.
5. Retire the `LLTagNamespace` namespace if all of its tag definitions have been retired.

## Learn More

- [Deleting tag defaults](https://docs.oracle.com/en-us/iaas/Content/Tagging/Tasks/managingtagdefaults.htm)
- [Deleting buckets](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/managingbuckets.htm)
- [Deleting budgets](https://docs.oracle.com/en-us/iaas/Content/Billing/Tasks/delete-budget.htm)
- [Deleting functions](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsdeleting.htm)


## Acknowledgements

- **Author** - Wynne Yang
- **Contributors** - Daniel Hart, Deion Locklear, Eli Schilling, Wynne Yang
- **Last Updated By/Date** - Published February, 2026
