#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="agentcore"
REPO_URL="https://github.com/aws-samples/sample-strands-agentcore-starter.git"

if [ -d "$TARGET_DIR/cdk" ]; then
  echo "AgentCore application already exists at $TARGET_DIR."
else
  echo "Cloning AWS starter into $TARGET_DIR..."
  git clone "$REPO_URL" "$TARGET_DIR"
fi

echo "Done. Read accelerator/INTEGRATION_PLAN.md for next steps."
