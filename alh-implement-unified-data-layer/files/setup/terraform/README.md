# Autonomous AI Lakehouse workshop environment

This Terraform configuration provisions the test environment for **Unify the Data Layer with Oracle Autonomous AI Lakehouse**.

It creates:

- One Oracle Autonomous AI Lakehouse using Oracle AI Database 26ai and the `LH` workload.
- One private OCI Object Storage bucket.
- Five structured CSV source extracts and three PDF project documents in the bucket.
- A dynamic group and least-privilege Object Storage read policy for the database resource principal.
- The `SEER_BRONZE`, `SEER_SILVER`, and `SEER_GOLD` schemas and all seeded tables referenced by Labs 1-3.
- A Database Actions user, `SEER_WORKSHOP` by default, with `DWROLE`, Data Transforms access, and permission to create the external table and Silver demonstration view.
- Oracle's public augmented `all-MiniLM-L12-v2` ONNX model, document embeddings, and an HNSW vector index.

## Requirements

- Terraform 1.5 or newer, or OCI Resource Manager.
- OCI provider 8.21.0 or newer.
- Permission to create Autonomous AI Database, Object Storage, dynamic-group, and policy resources.
- `oci`, `curl`, Python 3, and SQLcl (`sql`) in the Terraform execution environment. OCI Resource Manager has been used for this pattern, but the package must still be validated in the target tenancy.

## Apply

Copy `terraform.tfvars.example` to `terraform.tfvars`, provide the tenancy, compartment, and region values, and then run:

```text
terraform init
terraform plan
terraform apply
```

For OCI Resource Manager, use the generated `alh-unified-data-layer-stack.zip` package from the parent `setup` directory. Its Terraform files are at the archive root.

## Credentials

The requested attendee credentials appear as three non-sensitive Terraform outputs:

- `database_admin_password` - password for the fixed `ADMIN` database account
- `workshop_username` - attendee Database Actions username
- `workshop_user_password` - attendee Database Actions password

Run `terraform output` after apply. These values are intentionally plain text for ephemeral workshop testing. Terraform state also contains the generated passwords. Protect the state and destroy the environment when testing is complete.

## Data Studio external-table exercise

The stack does not create `SUPPLIER_TRANSFORM_EXT`. Participants create it through Database Actions using **Data Studio > Data Load > Link Data > Cloud Store**. Use the `object_storage_base_uri` output to create the cloud-store location with the `OCI$RESOURCE_PRINCIPAL` credential, then link `source-data/suppliers/supplier_extract.csv`.

The participant should include `FILE$NAME` and `SYSTIMESTAMP` in the Data Studio mapping. The linked table becomes the hands-on Bronze asset; `SUPPLIER_STANDARDIZED_DEMO` becomes the participant-created Silver result.

## Important implementation notes

- IAM policy propagation can take several minutes. Oracle notes that resource-principal membership and policy changes may be cached longer in some cases.
- The public ONNX download URL is an Oracle-published PAR URL and can be rotated. Override `embedding_model_download_uri` if the default no longer resolves.
- Terraform seeds pipeline-audit tables but does not create the visual `SEER_MEDALLION_PIPELINES` Data Transforms project. That project remains a separate environment-build item for the later operational-pipeline walkthrough.
- The bucket is private. Attendee access is through the Autonomous AI Lakehouse resource principal, not a user auth token.
