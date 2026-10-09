# Prompt Engineering: Build an OCI Operations Command Center

Status: **Authoring draft, 2026-10-09.** The local prompt runner and content can be checked offline. Model inference, generated application behavior, AgentMemory authentication, and OCI deployment require a live pilot before attendee release.

Attendees call OCI Generative AI through a transparent Python runner to generate a Python operations dashboard, repair it from validation feedback, generate its Dockerfile, and deploy it to OCI Container Instances. The application uses a resource principal and Oracle AgentMemory with Autonomous AI Database.

## Start here

- [Sandbox workshop](workshops/sandbox/index.html)
- [Workshop overview](0-introduction/introduction.md)
- [Authoring and release gates](AUTHORING.md)
- [Facilitator preparation](facilitator/preparation.md)
- [Authoring validation results](validation/REPORT.md)
- [Working application brief](files/starter/specs/app-brief.md)
- [API runner](files/starter/lab.py)

The comprehensive application ADR is a subsequent design task. The working brief records interfaces and acceptance expectations for the first pilot; it is not an approved implementation ADR.

## Layout

```text
oci-prompt-engineering-operations/
  0-introduction/
  1-prepare/
  2-generate-application/
  3-package-and-deploy/
  4-validate-application/
  5-operate-resources/
  6-clean-up/
  workshops/sandbox/{index.html,manifest.json}
  files/starter/{lab.py,config.example.json,deployment.example.json,...}
  facilitator/
  validation/
```

Lab folders are shared content. The manifest uses paths relative to `workshops/sandbox/`. The Redwood launcher follows the existing repository convention. Only the Sandbox draft is assessed; no Tenancy variant is claimed.

## Offline author checks

From `files/starter`, using Python 3.11 or later:

```bash
python -m unittest discover -s tests -v
python lab.py generate --stage plan --fixture fixtures/plan-response.json --out .offline-demo
python lab.py validate --out .offline-demo
```

The last command reports incomplete application files and exits with status 1. This is the expected result: the fixture demonstrates response parsing and file writing, and contains only a plan. It does not emulate model generation or supply a fallback application.

From the workshop root:

```bash
python validation/check_workshop.py
python validation/check_shell.py
```

Author checks cover manifest paths, local links, instructional sections, code fence balance, and referenced starter assets. They do not prove the cloud workflow.

## Duration and scope

The initial lab allocation is 120 minutes, plus 30 minutes of facilitation/recovery allowance. This is a planning budget, not an observed completion time. Bootstrap networking, IAM, database schemas, secrets, and registry repositories must be prepared before the event. Automatic VCN creation is reserved for an advanced extension.
