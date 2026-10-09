"""Boundary tests for generated file writes and the reviewed deployment request."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab


def plan_response(content='{"interfaces": []}'):
    return json.dumps({"files": [{"path": "architecture.json", "content": content}]})


def deployment_config():
    cfg = lab.read_json(lab.ROOT / "deployment.example.json")
    cfg.update(region="us-ashburn-1", hosting_compartment_id="ocid1.compartment.oc1..host",
               target_compartment_id="ocid1.compartment.oc1..target", availability_domain="test:AD-1",
               hosting_subnet_id="ocid1.subnet.oc1..host", compute_subnet_id="ocid1.subnet.oc1..compute",
               nsg_ids=["ocid1.networksecuritygroup.oc1..test"], owner_id="learner01", session_id="pilot01",
               image_url="ocir.us-ashburn-1.oci.oraclecloud.com/testns/app@sha256:" + "a" * 64,
               model_compartment_id="ocid1.compartment.oc1..model", model_region="us-chicago-1",
               model_id="test-model", memory_model_id="oci/test-memory", embedding_model_id="oci/test-embed",
               db_user="APP_USER", db_dsn="test-dsn", db_secret_ocid="ocid1.vaultsecret.oc1..db",
               app_auth_secret_ocid="ocid1.vaultsecret.oc1..auth", memory_store_id="PILOT01")
    return cfg


class FileBoundaryTests(unittest.TestCase):
    def test_valid_complete_response(self):
        self.assertEqual(lab.parse_files(plan_response(), "plan"), {"architecture.json": '{"interfaces": []}'})

    def test_markdown_wrapping_rejected(self):
        with self.assertRaises(ValueError):
            lab.parse_files("```json\n" + plan_response() + "\n```", "plan")

    def test_extra_metadata_rejected(self):
        with self.assertRaises(ValueError):
            lab.parse_files('{"files": [], "command": "run me"}', "plan")

    def test_unexpected_file_rejected(self):
        for path in ("../config.json", "/tmp/file", "C:/file", "app\\main.py", "config.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                lab.parse_files(json.dumps({"files": [{"path": path, "content": "text"}]}), "plan")

    def test_duplicate_file_rejected(self):
        entry = {"path": "architecture.json", "content": "{}"}
        with self.assertRaises(ValueError):
            lab.parse_files(json.dumps({"files": [entry, entry]}), "plan")

    def test_missing_file_rejected(self):
        with self.assertRaises(ValueError):
            lab.parse_files('{"files": []}', "plan")

    def test_empty_and_nontext_content_rejected(self):
        for content in ("", "  ", None, {}, "bad\u0000text"):
            with self.subTest(content=content), self.assertRaises(ValueError):
                lab.parse_files(json.dumps({"files": [{"path": "architecture.json", "content": content}]}), "plan")

    def test_oversized_file_rejected(self):
        with self.assertRaises(ValueError):
            lab.parse_files(plan_response("x" * (lab.CONTRACT["max_file_bytes"] + 1)), "plan")

    def test_safe_target_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in ("../outside", "/absolute", "C:/absolute", "./file", "app/../file", "file\\name"):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    lab.safe_target(tmp, path)

    def test_existing_outputs_require_explicit_replace(self):
        with tempfile.TemporaryDirectory() as tmp:
            lab.write_files({"architecture.json": "original"}, tmp)
            with self.assertRaises(ValueError):
                lab.write_files({"new.json": "new", "architecture.json": "changed"}, tmp)
            self.assertFalse((Path(tmp) / "new.json").exists())
            self.assertEqual((Path(tmp) / "architecture.json").read_text(), "original")
            lab.write_files({"architecture.json": "changed"}, tmp, replace=True)
            self.assertEqual((Path(tmp) / "architecture.json").read_text(), "changed")

    def test_validation_never_executes_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "execution-marker"
            files = {path: ("" if path == "app/__init__.py" else f"from pathlib import Path\nPath({str(marker)!r}).touch()\n")
                     for path in lab.STAGES["api"]}
            lab.write_files(files, tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lab.validate(tmp, "api"), 0)
            self.assertFalse(marker.exists())

    def test_syntax_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            lab.write_files({path: "def broken(:" for path in lab.STAGES["api"]}, tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lab.validate(tmp, "api"), 1)
            report = lab.read_json(Path(tmp) / "validation.json")
            self.assertFalse(report["passed"])
            self.assertEqual(len(report["errors"]), 4)

    def test_plan_fixture_is_not_a_complete_app(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = lab.parse_files((lab.ROOT / "fixtures/plan-response.json").read_text(), "plan")
            lab.write_files(files, tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(lab.validate(tmp, "plan"), 0)
                self.assertEqual(lab.validate(tmp), 1)


class DeploymentBoundaryTests(unittest.TestCase):
    def test_request_uses_secret_ids_and_principal(self):
        cfg = deployment_config()
        request = lab.deployment_request(cfg)
        container = request["containers"][0]
        self.assertFalse(container["isResourcePrincipalDisabled"])
        self.assertEqual(container["healthChecks"][0]["path"], "/health")
        self.assertEqual(container["environmentVariables"]["DB_SECRET_OCID"], cfg["db_secret_ocid"])
        self.assertNotIn("DB_PASSWORD", container["environmentVariables"])

    def test_empty_template_is_rejected(self):
        with self.assertRaises(ValueError):
            lab.deployment_request(lab.read_json(lab.ROOT / "deployment.example.json"))

    def test_shared_compartment_is_rejected(self):
        cfg = deployment_config()
        cfg["target_compartment_id"] = cfg["hosting_compartment_id"]
        with self.assertRaises(ValueError):
            lab.deployment_request(cfg)

    def test_mutable_image_is_rejected(self):
        cfg = deployment_config()
        cfg["image_url"] = "registry.example/ns/app:latest"
        with self.assertRaises(ValueError):
            lab.deployment_request(cfg)

    def test_secret_value_is_rejected(self):
        cfg = deployment_config()
        cfg["db_secret_ocid"] = "a-password-value"
        with self.assertRaises(ValueError):
            lab.deployment_request(cfg)

    def test_incompatible_architecture_or_missing_nsg_is_rejected(self):
        for key, value in (("container_shape", "CI.Standard.A1.Flex"), ("nsg_ids", []),
                           ("assign_public_ip", "false"), ("container_ocpus", 32)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                lab.deployment_request(dict(deployment_config(), **{key: value}))


@unittest.skipUnless(importlib.util.find_spec("oci"), "Install requirements-runner.txt for SDK contract checks")
class OciSdkContractTests(unittest.TestCase):
    def test_native_request_and_response_shape(self):
        import oci
        models = oci.generative_ai_inference.models
        message = models.AssistantMessage(content=[models.TextContent(text="READY")])
        response = types.SimpleNamespace(headers={"opc-request-id": "test-request"},
            data=types.SimpleNamespace(chat_response=models.GenericChatResponse(
                choices=[models.ChatChoice(index=0, message=message, finish_reason="STOP")], usage=None)))
        client = mock.Mock()
        client.chat.return_value = response
        cfg = {"compartment_id": "ocid1.compartment.oc1..test", "model_id": "test-model",
               "max_tokens": 256, "temperature": 0.1}
        with mock.patch.object(lab, "client_and_models", return_value=(client, models)):
            raw, metadata = lab.chat(cfg, "system", "user")
        self.assertEqual(raw, "READY")
        self.assertEqual(metadata["request_id"], "test-request")
        details = client.chat.call_args.args[0]
        self.assertEqual(details.chat_request.api_format, "GENERIC")
        self.assertEqual(details.serving_mode.serving_type, "ON_DEMAND")
        self.assertEqual(details.chat_request.messages[0].role, "SYSTEM")

    def test_truncated_native_response_is_rejected(self):
        import oci
        models = oci.generative_ai_inference.models
        client = mock.Mock()
        client.chat.return_value = types.SimpleNamespace(data=types.SimpleNamespace(chat_response=models.GenericChatResponse(
            choices=[models.ChatChoice(index=0, finish_reason="length", message=models.AssistantMessage(
                content=[models.TextContent(text='{"files":')]))])))
        cfg = {"compartment_id": "test", "model_id": "test", "max_tokens": 256, "temperature": 0.1}
        with mock.patch.object(lab, "client_and_models", return_value=(client, models)), self.assertRaises(ValueError):
            lab.chat(cfg, "system", "user")

    def test_deployment_fields_match_real_sdk(self):
        import oci
        models = oci.container_instances.models
        request = lab.deployment_request(deployment_config())
        for payload, cls in ((request, models.CreateContainerInstanceDetails),
                             (request["shapeConfig"], models.CreateContainerInstanceShapeConfigDetails),
                             (request["vnics"][0], models.CreateContainerVnicDetails),
                             (request["containers"][0], models.CreateContainerDetails),
                             (request["containers"][0]["healthChecks"][0], models.CreateContainerHttpHealthCheckDetails)):
            with self.subTest(model=cls.__name__):
                self.assertTrue(set(payload).issubset(set(cls().attribute_map.values())))

    def test_cloud_shell_uses_sdk_delegation_signer(self):
        import oci
        cfg = dict(lab.read_json(lab.ROOT / "config.example.json"), region="us-ashburn-1",
                   compartment_id="ocid1.compartment.oc1..test", model_id="test-model")
        sdk_cfg = {"region": "us-ashburn-1", "authentication_type": "instance_principal",
                   "delegation_token_file": "fake-token-path"}
        signer = mock.Mock()
        with mock.patch.object(oci.config, "from_file", return_value=sdk_cfg), \
             mock.patch.object(oci.util, "get_signer_from_authentication_type", return_value=signer) as get_signer, \
             mock.patch.object(oci.generative_ai_inference, "GenerativeAiInferenceClient") as client:
            lab.client_and_models(cfg)
        get_signer.assert_called_once_with(sdk_cfg)
        self.assertIs(client.call_args.kwargs["signer"], signer)


if __name__ == "__main__":
    unittest.main()
