# Authoring validation report

Date: 2026-10-09. Scope: **Sandbox draft only**. Mode: static content assessment plus local runner/SDK tests and browser rendering. This is not an end-to-end OCI validation.

## Verified

| Boundary | Evidence | Result |
| --- | --- | --- |
| LiveLabs structure | Sandbox manifest resolves introduction plus six local labs; standard Redwood launcher | Pass |
| Instructional design | Each local tutorial has objectives, prerequisites, numbered tasks, expected results, observation, troubleshooting, checkpoint, and acknowledgements | Pass |
| Local content/assets | Manifest paths, Markdown links, prompt/contract/starter references, balanced code fences | Pass; zero broken local links |
| Runner boundaries | 23 unittest cases including complete responses, rejected paths, duplicate files, size limits, explicit overwrite, no code execution, and deployment limits | Pass |
| OCI request contracts | Tests use installed OCI SDK 2.187.2 with mocked inference; deployment field names checked against actual SDK models | Pass locally; no endpoint invoked |
| Offline generation | Plan fixture writes architecture.json; stage validation passes; full app validation correctly exits 1 for missing app files | Pass; deliberately incomplete fixture |
| Learner shell syntax | 18 selected-manifest Bash blocks parsed with bash -n | Pass; no learner commands executed |
| Browser to content | Launcher fetches manifest and Markdown; introduction and Lab 2 render; navigation/expand/copy controls present | Pass; no page/console errors observed |

The browser preview used a local HTTP server and a dedicated headless agent-browser session. Screenshots are [introduction](introduction-preview.png) and [generation lab](generation-preview.png), each 1180x900, containing application content without browser chrome or secrets. No instructional screenshots of unbuilt cloud/application states were fabricated.

## Preliminary assessment

The workshop-validation skill's deterministic baseline is [44-77/100](baseline/WORKSHOP_ASSESSMENT.md), with low confidence and zero comparable calibrated records. Its document heuristic estimates P50 144 minutes and P90 192 minutes. These are estimates, not observed attendee times.

The stated 120 minutes is a lab allocation; the additional 30-minute allowance does not cover the heuristic P90. A two-hour event is not supported by this evidence. A half-day pilot is possible after the live gates are resolved; event suitability is not yet confirmed. The scorer flags elevated IAM/cloud dependencies. Those are facilitator preparation requirements in the Sandbox path, and the required bootstrap implementation is still pending.

## Live gates and lab status

| Lab | Content/local status | Live status |
| --- | --- | --- |
| 1: Prepare | Draft and local configuration/probe code checked | Learner inference/profile/permissions untested |
| 2: Generate | Prompts, contract, parsing/writing, repair context checked | Complete app generation/behavior untested |
| 3: Deploy | Draft, shell syntax, request fields checked | Image build/push/pull and Container Instance untested |
| 4: Validate | Runtime/memory/negative checks specified | Resource-principal, SQL, model/embedding, HTTPS untested |
| 5: Operate | Lifecycle/confirmation/ownership checks specified | Create/delete/idempotency/boot-volume behavior untested |
| 6: Clean up | Exact-ID cleanup and evidence checks specified | Cleanup command/lifecycle untested |

Required next work: approved comprehensive app ADR, bootstrap stack, independent app acceptance suite, repeated generation benchmark, tested recovery source/image, complete OCI pilot, and human timing calibration. See [authoring gates](../AUTHORING.md).

## Resource and cleanup status

No OCI cloud resources were created or deleted. No cloud endpoint was invoked by this authoring run. Local SDK installation and offline fixtures were used only for validation. Repository publication and live Sandbox provisioning remain separate subsequent steps.

## Tooling notes

The Windows sandbox account stopped launching processes with error 1909 during browser initialization. Approved local execution outside that sandbox completed the runner tests and browser preview. This was an authoring-host limitation, not evidence of a Cloud Shell or OCI failure.

The initial shell parser used a Windows filename with a Linux Bash executable. It was corrected to pass snippets over stdin and select Git Bash on Windows. Learner instructions were not executed as a workaround.
