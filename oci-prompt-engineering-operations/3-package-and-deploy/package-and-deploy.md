# Lab 3: Generate the Dockerfile and Deploy the Container

## Introduction

Ask the model to package the application, verify dependencies inside the image, push it to a private OCIR repository, and launch a Container Instance using a reviewed request.

**Estimated Time:** 25 minutes

### Objectives

- Generate and inspect the Dockerfile and build exclusions.
- Build a native x86_64 image and verify application imports.
- Push an immutable image to OCIR.
- Review and submit a Container Instance request.

### Prerequisites

- Lab 2 completed; Cloud Shell remains in `files/starter`.
- Facilitator-prepared E4 Container Instance quota/capacity, hosting subnet/NSG, private repository, learner push authentication, and resource-principal policies.
- Application SQL objects/memory store are prepared from the approved design. The authoring draft's bootstrap stack and independent acceptance suite are pending release gates.
- A facilitator-prepared HTTPS endpoint/routing method for this deployment.

## Task 1: Generate and inspect packaging

1. Generate the package stage and check the full file set:

    ```bash
    <copy>
    python lab.py generate --stage package
    python lab.py validate
    </copy>
    ```

1. Read `.generated/Dockerfile` and `.generated/.dockerignore`. Confirm the app starts on `0.0.0.0:8080`, runs as a non-root user, and excludes credentials and local run artifacts. Confirm no secret is passed through build arguments or image layers.

    **Expected result:** The full syntax/completeness check passes. Source review and the independent acceptance suite remain required; a passing check is not authorization to deploy faulty behavior.

## Task 2: Build and smoke-test

1. Confirm `uname -m` returns `x86_64`, then use the repository path supplied by the facilitator:

    ```bash
    <copy>
    read -r -p "Full OCIR repository path, without tag: " IMAGE_REPO
    IMAGE_TAG="${IMAGE_REPO}:$(date -u +%Y%m%dT%H%M%SZ)"
    podman build --format docker --platform linux/amd64 --tag "$IMAGE_TAG" .generated
    podman run --rm --entrypoint python "$IMAGE_TAG" -c 'from app.main import app; from app.oci_tools import OciTools; from app.memory import MemoryService; from app.store import Store; print("Imports passed")'
    </copy>
    ```

    **Expected result:** The build succeeds and the import smoke test prints `Imports passed`. Imports must not contact OCI or initialize SQL. A dependency error is useful feedback for the tools/package prompts.

1. Run the facilitator's independently authored application acceptance suite against the built artifact before event release. During the author pilot, record the pending suite as a deployment gate rather than claiming acceptance.

## Task 3: Push and record the digest

1. Log in interactively, using the facilitator-provided username and an OCIR auth token as the password. Keep the token out of command history and workshop notes:

    ```bash
    <copy>
    REGISTRY_DOMAIN="${IMAGE_REPO%%/*}"
    podman login "$REGISTRY_DOMAIN"
    podman push --digestfile .runs/image-digest.txt "$IMAGE_TAG"
    printf '%s@%s\n' "$IMAGE_REPO" "$(cat .runs/image-digest.txt)"
    </copy>
    ```

    **Expected result:** The push succeeds and the final line is a fully qualified image URL ending in `@sha256:...`. This digest identifies the image you will deploy.

1. Paste that URL into `image_url` in `deployment.json`. Confirm the host/target compartments, model settings, subnets, NSGs, owner/session identifiers, and secret OCIDs match the event outputs.

## Task 4: Review and launch

1. Render the request and inspect it:

    ```bash
    <copy>
    python lab.py render-deployment
    python -m json.tool container-instance.json
    </copy>
    ```

    **Expected result:** A JSON request is written; no cloud resource has been created. It enables the resource principal and defines an explicit HTTP liveness check. Keep existing output for review or use another `--out` filename when regenerating.

1. Confirm the expected cost/quota allocation: one E4 Container Instance at the configured 1 OCPU/8 GB pilot size. Submit the reviewed request in the configured resource region:

    ```bash
    <copy>
    RESOURCE_REGION="$(python -c 'import json; print(json.load(open("deployment.json"))["region"])')"
    oci container-instances container-instance create --region "$RESOURCE_REGION" --from-json file://container-instance.json > container-instance-result.json
    CONTAINER_INSTANCE_ID="$(python -c 'import json; print(json.load(open("container-instance-result.json"))["data"]["id"])')"
    oci container-instances container-instance get --region "$RESOURCE_REGION" --container-instance-id "$CONTAINER_INSTANCE_ID" --query 'data."lifecycle-state"' --raw-output
    </copy>
    ```

1. Record the Container Instance OCID, image digest, and create work-request ID if returned. Check status until `ACTIVE`; retain errors/logs if it fails. Do not repeat create to address an ambiguous response without checking for an existing instance first.

1. Obtain the configured HTTPS application URL using the facilitator's routing procedure and record it in `app-url.txt`. A private VNIC does not automatically give a browser-reachable URL. If the front door is absent, the deployment is not ready for Lab 4.

    **Observe:** Container Instance `ACTIVE`, liveness, and authenticated dependency readiness are different checks.

## Troubleshooting

- Build/import failure: return sanitized dependency diagnostics to the relevant prompt, review replacements, and rebuild. Do not include secrets in repair input.
- `QuotaExceeded`/capacity failure: use the exact region/shape/compartment and ask the facilitator to resolve the event allocation. Do not switch architectures without rebuilding and retesting dependencies.
- Private image pull fails: check image digest, repository read policy, dynamic-group membership, and VNIC reachability.
- App unreachable: check front-door routing, NSG/port, listen address, container logs, and `/health`.

## Completion checkpoint and recap

The image is pushed and digest-pinned, exactly one Container Instance is `ACTIVE`, and the HTTPS application URL is available. Continue to runtime validation. Explain why image push credentials and the runtime resource principal are separate.

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
