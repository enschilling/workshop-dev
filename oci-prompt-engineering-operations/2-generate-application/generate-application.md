# Lab 2: Generate and Refine the Application

## Introduction

Use a design brief, API examples, and an explicit file contract to generate a complete application in stages. Inspect the outputs and use concrete validation feedback to improve the prompts.

**Estimated Time:** 30 minutes

### Objectives

- Generate a reviewed architecture plan and application source through the OCI API.
- Compare a controlled prompt refinement against its baseline.
- Repair incomplete or invalid outputs with evidence.
- Distinguish syntax validation from behavioral acceptance.

### Prerequisites

- Lab 1 completed, including successful live inference.
- Cloud Shell is in `files/starter` with `.venv` activated and `config.json` populated.
- The comprehensive ADR/brief and pilot model configuration have been approved for the event.

## Task 1: Generate and review the plan

1. Submit the plan stage:

    ```bash
    <copy>
    python lab.py generate --stage plan
    python lab.py validate --stage plan
    python -m json.tool .generated/architecture.json
    </copy>
    ```

    **Expected result:** `architecture.json` maps requirements to interfaces, HTTP contracts, SQL objects, and acceptance checks. The runner saves the prompt, raw response, and metadata under `.runs/`.

1. Review unresolved questions and interface signatures with the facilitator before generating code. Compare each acceptance target to the plan. Resolve inconsistencies in the specification/prompt and regenerate with `--replace` if needed.

    **Observe:** A JSON response can be structurally correct while proposing the wrong design. Do not use parse success as design approval.

## Task 2: Generate application stages

1. Generate the API, OCI/memory/store tools, and UI in sequence. Validate each stage before proceeding:

    ```bash
    <copy>
    python lab.py generate --stage api
    python lab.py validate --stage api
    python lab.py generate --stage tools
    python lab.py validate --stage tools
    python lab.py generate --stage ui
    python lab.py validate --stage ui
    </copy>
    ```

    Run the next command only after reviewing the preceding result. These are separate model calls. Existing generated files and the reviewed plan are included as context. The runner never executes returned code or cloud commands.

1. Inspect the files under `.generated/app/` and `requirements.txt`. Trace one request through the planner, stored proposal, confirmation, ownership checks, OCI tool, and audit record. Confirm the reviewed interfaces are consistent across files.

    **Expected result:** Every path required by the selected stages exists, Python syntax checks pass, and the source implements the design requirements. Dependency/import and app behavior checks occur later.

## Task 3: Perform a controlled prompt experiment

1. Preserve the UI baseline and prompt:

    ```bash
    <copy>
    cp .generated/app/templates/index.html .runs/ui-baseline.html
    cp prompts/ui.md .runs/ui-prompt-baseline.md
    nano prompts/ui.md
    </copy>
    ```

1. Add one measurable requirement, such as: "Show the exact selected resource IDs in Review Action and label Confirm with the number of instances affected." Keep backend interfaces and controls unchanged.

1. Regenerate and compare:

    ```bash
    <copy>
    python lab.py generate --stage ui --replace
    python lab.py validate --stage ui
    diff -u .runs/ui-baseline.html .generated/app/templates/index.html
    </copy>
    ```

    **Expected result:** A visible source change addresses the added requirement. `diff` exits with status 1 when files differ; that is normal. Check JavaScript as well when the behavior is implemented there.

1. Record the prompt change, expected behavior, observed change, and any regression. Model sampling and updated context can also affect results; one comparison does not isolate causality. Verify the behavior in the deployed UI in Lab 4.

## Task 4: Repair with feedback

1. If a stage fails syntax/completeness validation, read `.generated/validation.json`, then request complete replacements for that stage:

    ```bash
    <copy>
    python lab.py generate --stage api --repair --replace
    python lab.py validate --stage api
    </copy>
    ```

    Substitute the affected stage for `api`. `--repair` includes the validation report; it does not run a self-directed repair loop. Limit the event path to two repair attempts, then use the facilitator's tested recovery checkpoint when available.

1. If the response is truncated or malformed before files are written, inspect its `.runs/` response and revise the prompt/output budget within the model's documented limits. The runner rejects Markdown-wrapped JSON and unexpected paths. Do not paste fragments together without checking the whole file.

    **Observe:** The local validator checks files and Python/JSON syntax. It does not test imports, SQL, authentication, ownership, or real OCI behavior.

## Troubleshooting

- Existing output requires `--replace`: inspect the existing stage before overwriting it; use a fresh output directory for an independent run.
- Interface mismatch: fix the reviewed plan/prompt and regenerate affected stages together. Do not silently change one side of an API contract.
- Invalid/extra paths: retain `contract.json` and ask for exactly the requested files.
- Missing future-stage files in a full validation report: use `--stage` until packaging is complete.

## Completion checkpoint and recap

All application stages pass local checks, interface/source review is complete, and your prompt experiment is recorded. Continue to packaging. Identify a requirement that passed syntax checks but still needs a behavioral test.

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
