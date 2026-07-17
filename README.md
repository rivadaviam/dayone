# Onboarding AgentCore Workshop

[![ci](https://github.com/rivadaviam/dayone/actions/workflows/ci.yml/badge.svg)](https://github.com/rivadaviam/dayone/actions/workflows/ci.yml)

Workshop MVP for building an agentic developer-onboarding assistant using **Amazon Bedrock AgentCore**, **Strands Agents** and native AWS services.

The goal of this repo is to serve as a starting point for the team to learn how to build, run and deploy an agent that, given an employee + profile + project, generates an onboarding plan, explains repositories, lists expected permissions and tracks progress.

> **Status: simulated vs. what you'll build.** This repo starts as **Lab 1** — a plain Python plan
> generator that runs **without** the Strands SDK. The real agent (Strands + Bedrock) is **Lab 2**
> and the AWS accelerator is **Lab 3**. Permissions, repos and state are **simulated** until later
> phases. Full labs guide: [`docs/WORKSHOP_LABS.md`](docs/WORKSHOP_LABS.md).

## Desired Product

The output of this project is a developer-focused onboarding assistant application that helps new team members understand the context of a project in no time so the ramp up is smooth and quick. The assistant should guide a developer through the practical information they need when joining a project, such as required technical setup, local environment configuration, project setup instructions, required credentials, access to tools and boards, and links to relevant project documentation.

Because onboarding needs can vary from project to project, the assistant should be flexible and driven by project-specific context. For example, one project might require a specific Node.js version, AWS access and Jira board access, while another project might require a different setup, credentials or documentation.

## MVP objectives

- Learn AgentCore Runtime and Strands Agents with a realistic case.
- Reduce external dependencies like Confluence/Jira/Slack during the MVP.
- Use local versioned documentation in the repo and/or S3.
- Model permissions and onboarding as declarative templates.
- Prepare the path for a backoffice UI where a manager selects employee, profile and project.

## MVP architecture

```text
Future backoffice / CLI
        |
        v
Strands Agent
        |
        +--> tools/load_profile.py
        +--> tools/load_project.py
        +--> tools/generate_plan.py
        +--> tools/track_progress.py
        |
        v
Future AgentCore Runtime
        |
        +--> Future DynamoDB: onboarding state
        +--> Future S3: versioned internal docs
        +--> Future IAM Identity Center: real permissions
        +--> Future CodeCommit/GitHub: real repos
```

## Structure

```text
.
├── agent/                         # Strands agent code
│   ├── app.py                      # Minimal agent
│   ├── config.py                   # Configuration
│   ├── prompts.py                  # System prompts
│   └── tools/                      # Simulated local tools
├── profiles/                       # Declarative onboarding profiles
├── projects/                       # Declarative projects
├── docs/                           # Objectives, context and decisions
├── accelerator/                    # Integration with the AWS sample
├── scripts/                        # Setup/demo scripts
├── infra/backoffice/               # Placeholder for the future backoffice
└── tests/                          # Minimal tests
```

## Local quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m agent.app --employee "Ada Lovelace" --email ada@example.com --profile backend-dev --project payments-platform
```

Expected output: an onboarding plan in Markdown with repos, permissions, checklist and first steps.

## Strands path (real agent, optional)

The local path above (`agent/app.py`) runs **without** the SDK. For a **Strands agent** to orchestrate
the same tools (Lab 2), use [`agent/strands_agent.py`](agent/strands_agent.py):

```bash
# 1) Enable the SDK (uncomment strands-agents and bedrock-agentcore in requirements.txt)
pip install strands-agents bedrock-agentcore

# 2) Configure AWS + Bedrock
cp .env.example .env          # set AWS_REGION and BEDROCK_MODEL_ID (requires model access)

# 3) Run the real agent
python -m agent.strands_agent --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

The tools are the **same** functions from `agent/tools/`, now wrapped as Strands `@tool`.
Tool contract details (read / generation / write / dangerous) in
[`docs/AGENTCORE_STRANDS_NOTES.md`](docs/AGENTCORE_STRANDS_NOTES.md).

## Using the AWS accelerator

This workshop includes a tracked AgentCore application under `agentcore/`,
based on the official accelerator `aws-samples/sample-strands-agentcore-starter`.

```bash
cd agentcore/cdk
./deploy-all.sh --region us-east-1 --profile <your-profile> --ingress furl
```

Then check `accelerator/INTEGRATION_PLAN.md` for the integration and testing workflow:

1. `agentcore/` contains the full-stack UI, infrastructure, and deployed agent.
2. The root `agent/`, `profiles/`, and `projects/` contain the local workshop domain.
3. Changes to the deployed agent should be made in `agentcore/` and committed to Git.

## Suggested roadmap

### Phase 1: Local workshop
- Run the local agent.
- Understand Strands tools and prompts.
- Add a new profile and project.
- Generate an onboarding plan.

### Phase 2: AgentCore
- Package the agent for AgentCore Runtime.
- Configure observability.
- Invoke per session.
- Compare local vs. managed runtime.

### Phase 3: Backoffice
- Create a minimal UI: employee, email, profile, project.
- Persist state in DynamoDB.
- Generate a checklist per employee.

### Phase 4: Real permissions
- Connect IAM Identity Center.
- Map profiles to permission sets.
- Approve sensitive actions human-in-the-loop.

## Design principle

Onboarding must be declarative:

```yaml
employee: ada@example.com
profile: backend-dev
project: payments-platform
```

The system automatically derives repos, permissions, tasks, documentation and next steps.
