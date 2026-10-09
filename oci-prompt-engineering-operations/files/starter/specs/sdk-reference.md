# Grounding reference for the pilot

These examples were checked against official documentation on 2026-10-09. They establish the API surface; the final model, database grants, package compatibility, and resource-principal calls still require live testing.

## OCI authentication

The deployed application creates one resource-principal signer:

```python
import oci
signer = oci.auth.signers.get_resource_principals_signer()
compute = oci.core.ComputeClient({"region": settings.oci_region}, signer=signer)
network = oci.core.VirtualNetworkClient({"region": settings.oci_region}, signer=signer)
secrets = oci.secrets.SecretsClient({"region": settings.oci_region}, signer=signer)
```

Use SecretsClient.get_secret_bundle(secret_id=...) and decode the base64 content internally. Do not print the decoded value. Resource-principal access to Vault does not automatically log the application into SQL; configure a database user, connection string, TLS, and retrieved credential separately.

## Native inference

```python
models = oci.generative_ai_inference.models
request = models.GenericChatRequest(
    messages=[models.UserMessage(content=[models.TextContent(text="Reply READY.")])],
    max_tokens=256,
    temperature=0.1,
    is_stream=False,
)
details = models.ChatDetails(
    compartment_id=settings.model_compartment_id,
    serving_mode=models.OnDemandServingMode(model_id=settings.model_id),
    chat_request=request,
)
```

Use the GENERIC API for a facilitator-tested compatible on-demand model. This starter does not implement Cohere-specific or dedicated-endpoint request formats. Check model-specific output limits and response/tool behavior; documentation availability is not tenancy availability.

## Oracle AgentMemory

```python
from oracleagentmemory.core import SchemaPolicy
from oracleagentmemory.core.oracleagentmemory import OracleAgentMemory
from oracleagentmemory.apis.searchscope import SearchScope
from oracleagentmemory.core.llms.llm import Llm
from oracleagentmemory.core.embedders.embedder import Embedder

llm = Llm(model=settings.memory_model_id, oci_signer=signer,
          oci_region=settings.model_region,
          oci_compartment_id=settings.model_compartment_id)
embedder = Embedder(model=settings.embedding_model_id, oci_signer=signer,
                   oci_region=settings.model_region,
                   oci_compartment_id=settings.model_compartment_id)
memory = OracleAgentMemory(connection=db_pool, llm=llm, embedder=embedder,
                           memory_store_id=settings.memory_store_id,
                           schema_policy=SchemaPolicy.REQUIRE_EXISTING)
thread = memory.create_thread(user_id=authenticated_owner_id)
thread.add_messages([{"role": "user", "content": "I prefer private subnets."}])
results = memory.search(query="networking preferences",
                        scope=SearchScope(user_id=authenticated_owner_id))
```

Initialize the managed store with schema-owner privileges during facilitator setup. The normal runtime expects existing objects. Oracle AgentMemory requires Oracle AI Database 23.4 or later; hybrid search has additional requirements. Use vector search for the first pilot and verify the embedding dimension/model and grants. Never let model text or browser fields pick the memory scope.

## Sources

- [OCI Python inference API](https://docs.oracle.com/en-us/iaas/tools/python/latest/api/generative_ai_inference.html)
- [OCI SDK authentication](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm)
- [AgentMemory getting started](https://docs.oracle.com/en/database/oracle/agent-memory/26.8/guide/get-started.html)
- [AgentMemory model adapters](https://docs.oracle.com/en/database/oracle/agent-memory/26.8/guide/api/models.html)
- [AgentMemory caller trust and scoping](https://docs.oracle.com/en/database/oracle/agent-memory/26.8/guide/security.html)
