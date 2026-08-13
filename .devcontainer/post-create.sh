#!/usr/bin/env bash
# Devcontainer post-create — prepare both tracks.
set -euo pipefail

echo "==> .NET track"
dotnet restore src/AgentOrchestrator/AgentHQDemo.slnx
dotnet build   src/AgentOrchestrator/AgentHQDemo.slnx

echo "==> Python track"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
(cd src/AgentOrchestrator-python && uv sync)

echo "==> Ready."
echo "    .NET   : dotnet run --project src/AgentOrchestrator/AgentHQDemo.Api --urls http://localhost:5050"
echo "    Python : cd src/AgentOrchestrator-python && uv run uvicorn app.main:app --port 5060"
