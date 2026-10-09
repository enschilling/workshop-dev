# Lab 1: Prepare the Environment and Test Model Access

## Introduction

Prepare a reproducible starter workspace, verify one inference request, and inspect the application specification. This prevents credential, model, or environment problems from being mistaken for prompt problems.

**Estimated Time:** 15 minutes

### Objectives

- Set up the API runner in Cloud Shell.
- Verify the selected model with the learner identity.
- Review the file contract and application requirements.
- Record the environment inputs needed for subsequent labs.

### Prerequisites

- Cloud Shell access and a facilitator-provided workshop commit/tag containing this folder. The authoring draft must first be committed and published by the workshop team.
- A tested GENERIC-format, on-demand model identifier, model region, and model compartment.
- Facilitator-prepared ADB/memory store, hosting and target compartments, subnets, NSGs, Vault secrets, private OCIR repository, and deployment quota/capacity.
- The [facilitator preparation contract](../facilitator/preparation.md) has been completed for this environment.

## Task 1: Download the pinned starter

1. Open **Cloud Shell** from the OCI Console. Confirm the session's region and architecture. For this draft, select the x86_64 Cloud Shell architecture using its architecture controls.

    ```bash
    <copy>
    uname -m
    python --version
    csruntimectl python list
    </copy>
    ```

    **Expected result:** Architecture is `x86_64`. Use `csruntimectl python set` with an available Python alias from the displayed list if Python is older than 3.11.

1. Download the repository and select the exact revision provided by the facilitator:

    ```bash
    <copy>
    read -r -p "Facilitator-provided workshop commit or tag: " WORKSHOP_REF
    git clone --filter=blob:none --sparse https://github.com/enschilling/workshop-dev.git prompt-workshop
    cd prompt-workshop
    git sparse-checkout set oci-prompt-engineering-operations
    git checkout "$WORKSHOP_REF"
    cd oci-prompt-engineering-operations/files/starter
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements-runner.txt
    </copy>
    ```

    **Expected result:** `lab.py`, `contract.json`, `prompts/`, and `specs/` exist. If the folder is absent at the supplied revision, ask the facilitator to correct the publication/ref; do not continue with another workshop's files.

## Task 2: Configure and probe inference

1. Copy and edit the non-secret model configuration:

    ```bash
    <copy>
    cp config.example.json config.json
    nano config.json
    </copy>
    ```

    Set `region`, `compartment_id`, and `model_id` from the event outputs. Keep `auth_mode` as `cloud_shell` for the standard Cloud Shell delegation-token profile. Set the profile/path if the facilitator specifies another existing profile. Do not copy tokens or keys into this JSON.

1. Validate locally, then make the live probe:

    ```bash
    <copy>
    python lab.py preflight
    python lab.py preflight --live
    </copy>
    ```

    **Expected result:** `Configuration valid` followed by `Live inference probe passed` and an OCI request ID. The live command submits one small billed inference request. It does not verify deployment quotas, memory, or the eventual Container Instance identity.

1. Record the model identifier, region, SDK version, and successful probe request ID in your workshop notes. Record identifiers only.

## Task 3: Inspect the design and outputs

1. Read `specs/app-brief.md`, `specs/sdk-reference.md`, `contract.json`, and `prompts/system.md`.

1. Identify where these requirements are enforced: missing-input clarification, explicit confirmation, owner/session scope, resource limits, memory retrieval scope, and secret handling.

1. Copy `deployment.example.json` to `deployment.json` and fill it with facilitator-provided configuration. Keep secret **OCIDs**, rather than secret values, in the file. Leave `image_url` empty until you push the image in Lab 3.

    **Observe:** The generation model identifier and AgentMemory adapter identifiers may differ. AgentMemory's OCI provider names use the adapter's `oci/` prefix.

## Troubleshooting

- `delegation_token_file` missing: verify the selected Cloud Shell profile and refresh the session. An API-key or authenticated security-token profile uses its matching `auth_mode`; changing the mode does not grant access.
- OCI `401`/`403`: verify identity, region, compartment, and the facilitator-prepared inference policies. Keep tokens and private keys out of error reports.
- Model/API incompatibility: the starter uses native GENERIC on-demand chat. Cohere-specific or dedicated-endpoint formats require a separately tested adapter.
- Package download fails: check Cloud Shell outbound networking and storage with the facilitator.

## Completion checkpoint and recap

Continue when the live probe passes, the approved specification is available, and all deployment inputs have been delivered. You have verified API access using the learner identity; the deployed resource principal will be tested separately.

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
