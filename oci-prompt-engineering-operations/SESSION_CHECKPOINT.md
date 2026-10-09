# Session Checkpoint - 2026-10-09

## Workshop

- Repository: `C:\Users\Eli\Documents\GitHub\workshop-dev`, branch `main`, origin `https://github.com/enschilling/workshop-dev.git`.
- Workshop: `oci-prompt-engineering-operations`.
- Active manifest: `workshops/sandbox/manifest.json` only.
- Current task: First authoring increment; local validation complete; live pilot pending.
- Overall status: Authoring draft. No comprehensive ADR or completed app is claimed.

## Environment and tooling

- Author host: Windows/PowerShell; Python 3.14.7.
- Local validation environment: OCI SDK 2.187.2 in a workspace virtual environment.
- Browser: agent-browser 0.26.0, dedicated headless preview session; viewport 1180x900.
- Learner target: Cloud Shell x86_64/Python 3.11+, native GENERIC on-demand inference, E4 Container Instance.
- WSL was unavailable to the default sandbox process. Git Bash is used for shell syntax checks.
- No model region, target compartment, live credentials, or reservation has been selected for this workshop.

## Scope and decisions

- Six labs: prepare, generate, package/deploy, validate, operate, cleanup.
- Reuse the repo's shared lab-folder/manifest/Redwood structure.
- Keep hosting and managed-resource compartments separate.
- Existing approved networking in the core path; automatic VCN creation is an advanced extension.
- A working brief supplies a pilot target; comprehensive ADR is the next design task.
- No app implementation/fallback artifact, bootstrap stack, or independently implemented app acceptance suite exists yet.

## Evidence

- All seven local tutorials resolve; no broken local links; instructional sections and assets checked.
- 23 runner boundary/OCI SDK contract tests pass; cloud client calls mocked.
- Offline plan fixture succeeds; full-app validation correctly fails on absent application files.
- Browser launcher, navigation, task expansion, and Copy controls verified; screenshots in validation/.
- Baseline assessment: 44-77/100, low confidence, no calibrated records, heuristic P50/P90 144/192 minutes.
- Evaluation record appended to `validation/evaluations.jsonl`.
- See `validation/REPORT.md` for limitations and live lab status.

## Resources and secrets

- No cloud resources created/deleted; no live model request made.
- No secrets collected or stored.
- Bootstrap output delivery, database/memory schema preparation, registry authentication, IAM, network, and quotas remain pilot prerequisites.

## Next actions

1. Approve the comprehensive app ADR and final interfaces/data model.
2. Implement bootstrap infrastructure and independent acceptance tests.
3. Choose a test environment and run the full generation/deployment/resource lifecycle pilot.
4. Record failures, fix the guide/prompts with evidence, publish tested recovery artifacts.
5. Calibrate event timing with a human pilot before claiming two-hour suitability.
