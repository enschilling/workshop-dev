Generate a Dockerfile and .dockerignore for the complete application.
Target Python 3.11 on Debian slim, linux/amd64, and the E4 Container Instance shape used by this draft.
Install requirements.txt, copy the app, use a non-root runtime user, and start app.main:app on 0.0.0.0:8080.
Exclude .runs, .venv, config.json, deployment.json, validation.json, credentials, keys, wallets, and author artifacts.
No secrets in ARG, ENV, RUN, image layers, or source files. Fetch Vault credentials at application runtime.
Use the Docker image format for the build; the deployment request also supplies an explicit /health check.
Keep imports usable for a dependency smoke test that does not start the app or call OCI.
