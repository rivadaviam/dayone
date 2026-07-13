# Workshop labs guide

This guide ties together the three workshop labs, from the simulated local path to the real agent and the AWS accelerator.
The goal is not to have everything solved, but to make **clear what we want to achieve at each step**.

## Map: what's simulated and what you'll build?

| Layer         | Lab 1 (local)                       | Lab 2 (Strands)                             | Lab 3 (accelerator)            |
| ------------- | ----------------------------------- | ------------------------------------------- | ------------------------------ |
| Orchestration | `build_plan()` in Python            | **Strands agent** decides which tool to use | Agent on AgentCore Runtime     |
| Tools         | Python functions                    | Same functions as `@tool`                   | Same tools + real AWS (future) |
| Data          | YAML in `profiles/` and `projects/` | YAML (same)                                 | YAML + S3 / DynamoDB (future)  |
| Permissions   | **Simulated** (text in the plan)    | Simulated                                   | IAM Identity Center (future)   |
| State         | JSON in `.local-progress/`          | Local JSON                                  | DynamoDB (future)              |

> Golden rule: **the repo must always run in Lab 1 without installing the Strands SDK.**
> Lab 2 and Lab 3 are optional and additive; they don't break the local path.

---

## Lab 1 — Local agent (understand the domain)

**Goal:** run the plan generator and understand the declarative model.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m agent.app --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
pytest
```

**Exercises:**

1. Add a new profile in `profiles/` (e.g. `data-engineer.yaml`).
2. Add a new project in `projects/`.
3. Generate a plan with that combination and review the resulting Markdown.

**Criterion to move to Lab 2:** the plan is generated with correct repos, permissions and checklist.

---

## Lab 2 — Strands tools (the agent reasons)

**Goal:** have an **agent** decide when to invoke each tool, instead of calling them ourselves.

```bash
# 1) Enable the SDK
#    Uncomment in requirements.txt: strands-agents, bedrock-agentcore
pip install strands-agents bedrock-agentcore

# 2) Configure AWS + Bedrock
cp .env.example .env          # set AWS_REGION and BEDROCK_MODEL_ID
#    Requires AWS credentials and enabled access to the model in Bedrock.

# 3) Run the real agent
python -m agent.strands_agent --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

See `agent/strands_agent.py`: it wraps the **same** functions from `agent/tools/` as `@tool`
(read: `load_profile`, `load_project`; generation: `generate_onboarding_plan`;
write: `mark_step_done`) and passes them to a Strands `Agent` with `SYSTEM_PROMPT`.

**Exercises:**

1. Add the `mark_step_done` write tool to a conversation and record a step.
2. Ask the agent to explain **what it would do** before doing it (human-in-the-loop).
3. Review the dangerous-tools contract in `docs/AGENTCORE_STRANDS_NOTES.md`.

**Criterion to move to Lab 3:** the agent loads profile + project, generates the plan and records a step.

---

## Lab 3 — AWS accelerator (path to production)

**Goal:** use `aws-samples/sample-strands-agentcore-starter` for infra/UI/deploy, keeping
this repo as the domain layer (**Option C** recommended — see `accelerator/INTEGRATION_PLAN.md`).

```bash
bash accelerator/clone_aws_starter.sh   # clones the starter into .aws-samples/ (already gitignored)
```

Then follow the concrete runbook in `accelerator/INTEGRATION_PLAN.md` (prerequisites, commands and
where the starter's agent lives).

**Workshop success criterion:** the team can explain, modify and extend the onboarding flow, and
knows how to evolve it toward an AWS-native production solution.
