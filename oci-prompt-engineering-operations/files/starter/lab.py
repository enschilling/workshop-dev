#!/usr/bin/env python3
"""Visible OCI inference, file generation, and author checks; no command agent."""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parent
CONTRACT = json.loads((ROOT / "contract.json").read_text(encoding="utf-8"))
STAGES = CONTRACT["stages"]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def safe_target(root, relative):
    """Keep every model-supplied path inside the chosen generated directory."""
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError("File paths must be relative POSIX paths")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in {"..", "."} for part in relative.split("/")):
        raise ValueError("Absolute paths and traversal are rejected")
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if target == root or not target.is_relative_to(root):
        raise ValueError("File path escapes the generated directory")
    return target


def parse_files(raw, stage):
    if len(raw.encode("utf-8")) > CONTRACT["max_response_bytes"]:
        raise ValueError("Response exceeds the workshop byte limit")
    payload = json.loads(raw)
    if not isinstance(payload, dict) or set(payload) != {"files"}:
        raise ValueError('Expected exactly {"files": [...]}')
    entries = payload["files"]
    if not isinstance(entries, list):
        raise ValueError("files must be an array")
    result = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "content"}:
            raise ValueError("Each file must have path and content only")
        path, content = entry["path"], entry["content"]
        if not isinstance(path, str) or path not in STAGES[stage]:
            raise ValueError("Unexpected file for the selected stage")
        if path in result:
            raise ValueError("Duplicate file path")
        if not isinstance(content, str) or (not content.strip() and path != "app/__init__.py"):
            raise ValueError("File content must be a complete text string")
        if len(content.encode("utf-8")) > CONTRACT["max_file_bytes"] or "\x00" in content:
            raise ValueError("File content exceeds limits or contains a null byte")
        result[path] = content
    if set(result) != set(STAGES[stage]):
        raise ValueError("Response must include every file required by the stage")
    return result


def write_files(files, out, replace=False):
    # Prevalidate the entire response before making any write.
    targets = {name: safe_target(out, name) for name in files}
    for target in targets.values():
        if target.exists() and not replace:
            raise ValueError("Existing output requires --replace; choose a fresh directory for comparisons")
        if target.exists() and not target.is_file():
            raise ValueError("Output path is not a regular file")
    for name, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(files[name], encoding="utf-8", newline="\n")


def validate_config(cfg):
    for key in ("region", "compartment_id", "model_id"):
        if not isinstance(cfg.get(key), str) or not cfg[key].strip():
            raise ValueError(f"Set {key} in config.json using facilitator-provided values")
    if not re.fullmatch(r"[a-z]+-[a-z0-9-]+-\d+", cfg["region"]):
        raise ValueError("region must be an OCI region identifier")
    if not cfg["compartment_id"].startswith("ocid1.compartment."):
        raise ValueError("compartment_id must be a compartment OCID")
    if cfg.get("auth_mode") not in {"cloud_shell", "security_token", "api_key", "resource_principal"}:
        raise ValueError("Unsupported auth_mode")
    if type(cfg.get("max_tokens")) is not int or not 128 <= cfg["max_tokens"] <= 32768:
        raise ValueError("max_tokens must be an integer between 128 and 32768; check model limits")
    if type(cfg.get("temperature")) not in {int, float} or not 0 <= cfg["temperature"] <= 1:
        raise ValueError("temperature must be between 0 and 1")


def client_and_models(cfg):
    import oci
    validate_config(cfg)
    mode = cfg["auth_mode"]
    if mode == "resource_principal":
        sdk_config = {"region": cfg["region"]}
        signer = oci.auth.signers.get_resource_principals_signer()
    else:
        sdk_config = oci.config.from_file(
            str(Path(cfg.get("oci_config_file", "~/.oci/config")).expanduser()),
            cfg.get("oci_profile", "DEFAULT"),
        )
        signer = None
        if mode == "cloud_shell":
            if not sdk_config.get("delegation_token_file"):
                raise ValueError("Selected OCI profile has no delegation_token_file; use the Cloud Shell profile")
            signer = oci.util.get_signer_from_authentication_type(sdk_config)
        elif mode == "security_token":
            token_path = sdk_config.get("security_token_file")
            if not token_path:
                raise ValueError("Selected OCI profile has no security_token_file; refresh the Cloud Shell session/profile")
            token = Path(token_path).expanduser().read_text(encoding="utf-8").strip()
            key = oci.signer.load_private_key_from_file(str(Path(sdk_config["key_file"]).expanduser()))
            signer = oci.auth.signers.SecurityTokenSigner(token, key)
        sdk_config["region"] = cfg["region"]
    kwargs = {
        "service_endpoint": f'https://inference.generativeai.{cfg["region"]}.oci.oraclecloud.com',
        "timeout": (10, 240),
        "retry_strategy": oci.retry.NoneRetryStrategy(),
    }
    if signer is not None:
        kwargs["signer"] = signer
    client = oci.generative_ai_inference.GenerativeAiInferenceClient(sdk_config, **kwargs)
    return client, oci.generative_ai_inference.models


def chat(cfg, system, prompt):
    client, models = client_and_models(cfg)
    request = models.GenericChatRequest(
        messages=[models.SystemMessage(content=[models.TextContent(text=system)]),
                  models.UserMessage(content=[models.TextContent(text=prompt)])],
        max_tokens=cfg["max_tokens"], temperature=cfg["temperature"], is_stream=False,
    )
    details = models.ChatDetails(
        compartment_id=cfg["compartment_id"],
        serving_mode=models.OnDemandServingMode(model_id=cfg["model_id"]),
        chat_request=request,
    )
    response = client.chat(details)
    choices = response.data.chat_response.choices
    if not choices:
        raise ValueError("Model returned no choices")
    choice = choices[0]
    finish = str(getattr(choice, "finish_reason", "")).upper()
    if finish in {"LENGTH", "MAX_TOKENS", "MAX_COMPLETION_TOKENS"}:
        raise ValueError("Model response was truncated; revise the stage or output budget")
    raw = "".join(item.text for item in choice.message.content if getattr(item, "text", None))
    if not raw.strip():
        raise ValueError("Model returned no text content")
    import oci
    return raw, {"request_id": response.headers.get("opc-request-id"),
                 "usage": oci.util.to_dict(getattr(response.data.chat_response, "usage", None)),
                 "finish_reason": finish}


def prompt_for(stage, out, repair=False):
    chunks = [(ROOT / "specs/app-brief.md").read_text(encoding="utf-8"),
              (ROOT / "specs/sdk-reference.md").read_text(encoding="utf-8"),
              (ROOT / f"prompts/{stage}.md").read_text(encoding="utf-8")]
    chunks.append("Return exactly these files: " + json.dumps(STAGES[stage]))
    for paths in STAGES.values():
        for relative in paths:
            target = safe_target(out, relative)
            if target.is_file():
                content = target.read_text(encoding="utf-8")
                if len(content.encode("utf-8")) > CONTRACT["max_file_bytes"]:
                    raise ValueError("Existing context file exceeds the byte limit")
                chunks.append(f"Existing file: {relative}\n{content}")
    if repair:
        report = Path(out) / "validation.json"
        if not report.exists():
            raise ValueError("Run validate before --repair")
        chunks += [(ROOT / "prompts/repair.md").read_text(encoding="utf-8"),
                   report.read_text(encoding="utf-8")]
    prompt = "\n\n".join(chunks)
    if len(prompt.encode("utf-8")) > 1500000:
        raise ValueError("Prompt context is too large; narrow the stage/context")
    return prompt


def generate(args):
    prompt = prompt_for(args.stage, args.out, args.repair)
    if args.fixture:
        raw = Path(args.fixture).read_text(encoding="utf-8")
        metadata = {"mode": "offline-fixture"}
    else:
        cfg = read_json(args.config)
        raw, metadata = chat(cfg, (ROOT / "prompts/system.md").read_text(encoding="utf-8"), prompt)
        metadata.update(mode="oci-inference", model_id=cfg["model_id"], region=cfg["region"])
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = ROOT / ".runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (run_dir / "response.txt").write_text(raw, encoding="utf-8")
    metadata.update(stage=args.stage, repair=args.repair, output_directory=str(Path(args.out).resolve()))
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    files = parse_files(raw, args.stage)
    write_files(files, args.out, args.replace)
    print(f"Wrote {len(files)} file(s); stage={args.stage}; mode={metadata['mode']}")
    print(f"Run evidence: {run_dir}")
    return 0


def validate(out, stage=None):
    errors = []
    paths = STAGES[stage] if stage else [p for group in STAGES.values() for p in group]
    for relative in paths:
        path = safe_target(out, relative)
        if not path.is_file():
            errors.append({"file": relative, "error": "Required file is missing"})
            continue
        text = path.read_text(encoding="utf-8")
        try:
            if relative.endswith(".py"):
                ast.parse(text, filename=relative)
            elif relative.endswith(".json"):
                json.loads(text)
        except (SyntaxError, json.JSONDecodeError) as exc:
            errors.append({"file": relative, "error": str(exc)})
    report = {"scope": stage or "all", "passed": not errors, "errors": errors,
              "limitations": ["File completeness and Python/JSON syntax only; code has not been executed.",
                              "Application acceptance, dependencies, identity, IAM, memory, and cloud behavior require a pilot."]}
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


def deployment_request(cfg):
    required = [key for key in read_json(ROOT / "deployment.example.json")
                if key not in {"nsg_ids", "assign_public_ip"}]
    for key in required:
        if cfg.get(key) is None or cfg.get(key) == "":
            raise ValueError(f"Set deployment field {key}")
    for key in ("hosting_compartment_id", "target_compartment_id", "model_compartment_id"):
        if not cfg[key].startswith("ocid1.compartment."):
            raise ValueError(f"Invalid {key}")
    if cfg["hosting_compartment_id"] == cfg["target_compartment_id"]:
        raise ValueError("Keep hosting and managed-resource compartments separate")
    for key in ("hosting_subnet_id", "compute_subnet_id"):
        if not cfg[key].startswith("ocid1.subnet."):
            raise ValueError(f"Invalid {key}")
    for key in ("db_secret_ocid", "app_auth_secret_ocid"):
        if not cfg[key].startswith("ocid1.vaultsecret."):
            raise ValueError(f"Invalid {key}; supply a secret OCID, never a password")
    for key in ("owner_id", "session_id", "memory_store_id"):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", cfg[key]):
            raise ValueError(f"Use a short non-personal identifier for {key}")
    if cfg["container_shape"] != "CI.Standard.E4.Flex":
        raise ValueError("This draft targets E4/x86; pilot other shapes before changing the contract")
    if type(cfg["container_ocpus"]) not in {int, float} or not 1 <= cfg["container_ocpus"] <= 2:
        raise ValueError("Container pilot supports 1-2 OCPUs")
    if type(cfg["container_memory_gbs"]) not in {int, float} or not 8 <= cfg["container_memory_gbs"] <= 16:
        raise ValueError("Container pilot supports 8-16 GB")
    if type(cfg.get("assign_public_ip")) is not bool:
        raise ValueError("assign_public_ip must be a boolean")
    if not isinstance(cfg.get("nsg_ids"), list) or not cfg["nsg_ids"] or any(
        not isinstance(item, str) or not item.startswith("ocid1.networksecuritygroup.") for item in cfg["nsg_ids"]
    ):
        raise ValueError("Provide at least one facilitator-prepared network security group")
    image = cfg["image_url"]
    if not re.fullmatch(r"[a-z0-9.-]+/[^\s@]+@sha256:[a-f0-9]{64}", image):
        raise ValueError("image_url must be a fully qualified image pinned by sha256 digest")
    environment = {
        "OCI_REGION": cfg["region"], "TARGET_COMPARTMENT_ID": cfg["target_compartment_id"],
        "COMPUTE_SUBNET_ID": cfg["compute_subnet_id"], "WORKSHOP_OWNER_ID": cfg["owner_id"],
        "WORKSHOP_SESSION_ID": cfg["session_id"], "MODEL_COMPARTMENT_ID": cfg["model_compartment_id"],
        "MODEL_REGION": cfg["model_region"], "MODEL_ID": cfg["model_id"],
        "MEMORY_MODEL_ID": cfg["memory_model_id"], "EMBEDDING_MODEL_ID": cfg["embedding_model_id"],
        "DB_USER": cfg["db_user"], "DB_DSN": cfg["db_dsn"], "DB_SECRET_OCID": cfg["db_secret_ocid"],
        "APP_AUTH_SECRET_OCID": cfg["app_auth_secret_ocid"], "MEMORY_STORE_ID": cfg["memory_store_id"],
    }
    return {
        "availabilityDomain": cfg["availability_domain"], "compartmentId": cfg["hosting_compartment_id"],
        "displayName": f"prompt-lab-{cfg['session_id']}", "shape": cfg["container_shape"],
        "shapeConfig": {"ocpus": cfg["container_ocpus"], "memoryInGBs": cfg["container_memory_gbs"]},
        "containerRestartPolicy": "ALWAYS",
        "freeformTags": {"workshop": "prompt-engineering", "session": cfg["session_id"]},
        "vnics": [{"subnetId": cfg["hosting_subnet_id"], "nsgIds": cfg["nsg_ids"],
                   "isPublicIpAssigned": cfg["assign_public_ip"]}],
        "containers": [{"displayName": "operations-command-center", "imageUrl": image,
                        "isResourcePrincipalDisabled": False, "environmentVariables": environment,
                        "healthChecks": [{"healthCheckType": "HTTP", "name": "liveness", "path": "/health",
                                          "port": 8080, "initialDelayInSeconds": 30, "intervalInSeconds": 30,
                                          "timeoutInSeconds": 10, "failureThreshold": 3, "successThreshold": 1}]}],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pre = sub.add_parser("preflight", help="Validate configuration; --live makes one billed model call")
    pre.add_argument("--config", default="config.json")
    pre.add_argument("--live", action="store_true")
    gen = sub.add_parser("generate")
    gen.add_argument("--stage", choices=STAGES, required=True)
    gen.add_argument("--config", default="config.json")
    gen.add_argument("--out", default=".generated")
    gen.add_argument("--fixture", help="Offline response file; no cloud request")
    gen.add_argument("--replace", action="store_true")
    gen.add_argument("--repair", action="store_true")
    val = sub.add_parser("validate")
    val.add_argument("--out", default=".generated")
    val.add_argument("--stage", choices=STAGES)
    dep = sub.add_parser("render-deployment", help="Write a request only; does not create cloud resources")
    dep.add_argument("--config", default="deployment.json")
    dep.add_argument("--out", default="container-instance.json")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            return generate(args)
        if args.command == "validate":
            return validate(args.out, args.stage)
        if args.command == "render-deployment":
            request = deployment_request(read_json(args.config))
            target = Path(args.out)
            if target.exists():
                raise ValueError("Deployment output already exists; review it or choose another --out path")
            target.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
            print(f"Wrote {target}; review it before running OCI create")
            return 0
        cfg = read_json(args.config)
        validate_config(cfg)
        print("Configuration valid. This does not check IAM, model availability, quotas, or networking.")
        if args.live:
            probe_cfg = dict(cfg, max_tokens=256)
            raw, metadata = chat(probe_cfg, "Return the exact word READY.", "Reply READY.")
            if raw.strip() != "READY":
                raise ValueError("Endpoint responded, but did not return the expected READY probe")
            print("Live inference probe passed; request_id=" + str(metadata["request_id"]))
        return 0
    except Exception as exc:
        if hasattr(exc, "status") and hasattr(exc, "code"):
            print(f"OCI request failed: status={exc.status} code={exc.code} request_id={getattr(exc, 'request_id', None)}", file=sys.stderr)
        elif isinstance(exc, (ValueError, OSError, ImportError)):
            print(f"Error: {exc}", file=sys.stderr)
        else:
            print(f"Error: {type(exc).__name__}; inspect SDK compatibility without sharing credentials", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
