Implement the configuration, API routes, authentication/confirmation flow, and natural-language planner.
Use the reviewed architecture.json and method signatures. Supply complete code for the requested files.
The planner returns clarification or a durable proposal. A chat request cannot directly trigger a write operation.
Confirmation consumes a stored plan using server-derived owner/session identity and returns an operation ID.
Keep imports free of network side effects. The UI, OCI tools, memory, and store are generated in later stages.
Preserve their reviewed interfaces and avoid circular imports.
