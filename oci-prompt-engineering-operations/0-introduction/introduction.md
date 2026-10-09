# Prompt Engineering: Build an OCI Operations Command Center

## Introduction

Build a cloud operations dashboard by submitting a design brief and structured prompts to OCI Generative AI. Generate the application code, use validation feedback to repair it, ask the model to package it, and deploy the image to OCI Container Instances. Then use natural language to create and delete resources through a controlled OCI SDK tool layer.

**Authoring draft:** This workshop requires a live generation/deployment pilot, an approved comprehensive application ADR, and prepared Sandbox infrastructure before attendee release. Local starter checks do not establish application readiness.

**Estimated Workshop Time:** 120 minutes, with a separate 30-minute recovery allowance. Timing is an initial planning budget.

### Objectives

In this workshop, you will:

- Translate requirements into grounded prompts and a machine-readable file contract.
- Generate application files through an OCI API, inspect outputs, and refine prompts using feedback.
- Generate a Dockerfile, build an image, push to OCIR, and launch a Container Instance.
- Distinguish cloud identity, application user identity, and scoped memory.
- Validate persistent Oracle AgentMemory backed by Autonomous AI Database.
- Create, inspect, and delete resources through confirmed, limited operations.

### Prerequisites

- A facilitator-prepared Sandbox with the resources and outputs listed in the preparation lab.
- Basic familiarity with OCI compartments, Compute, networking, and command-line commands.
- Access to OCI Cloud Shell and the published workshop revision.
- An approved application specification and tested model configuration for the event.

## Task 1: Understand the two prompting workflows

1. Follow the build workflow: specification -> staged prompts -> files -> validation/repair -> image -> deployment.

1. Follow the runtime workflow: request -> clarification/proposal -> user confirmation -> validated OCI SDK action -> audit and refreshed resources.

    **Expected result:** You can explain where the model supplies content and where ordinary code validates or executes it. A model response does not itself create files or launch cloud resources.

1. Review the [working application brief](../files/starter/specs/app-brief.md). It defines the initial pilot target. The later comprehensive ADR will replace this brief with approved design details before release.

## Task 2: Review the lab journey

| Lab | Purpose | Planning allocation |
| --- | --- | --- |
| 1: Prepare | Verify API access and review inputs/specification | 15 minutes |
| 2: Generate | Create the app in stages and refine a prompt | 30 minutes |
| 3: Package and deploy | Generate Dockerfile, build, push, and launch | 25 minutes |
| 4: Validate | Test runtime identity, readiness, and memory | 15 minutes |
| 5: Operate | Create/list/delete owned Compute resources | 25 minutes |
| 6: Clean up | Verify removal and record learning outcomes | 10 minutes |

1. Identify the bootstrap infrastructure: hosting networking, database, IAM, Vault secrets, and registry repository.

1. Identify what you create: generated source files, a container image, one application Container Instance, and test Compute resources.

    **Observe:** Bootstrap infrastructure is prepared by the facilitator. The core app uses existing approved networking. Automatic VCN creation is an advanced extension.

## Troubleshooting

- If the facilitator has not supplied a published workshop revision and prepared environment, remain in the authoring/pilot workflow. Do not improvise tenancy-wide policies or paid infrastructure.
- If a required service is unavailable in the event region, the facilitator must select and retest the environment before the event.

## Completion checkpoint and recap

You understand the build/runtime workflows, learning objectives, and resource boundary. Continue to Lab 1. Consider which controls belong in the prompt and which must also be enforced by the application.

## Learn more

- [OCI Generative AI](https://docs.oracle.com/en-us/iaas/Content/generative-ai/home.htm)
- [Oracle AgentMemory](https://docs.oracle.com/en/database/oracle/agent-memory/26.8/guide/get-started.html)

## Acknowledgements

- **Authoring:** Workshop development team
- **Last Updated By/Date:** Workshop development team, October 2026
