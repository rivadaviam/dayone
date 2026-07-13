# Lab 1 notes — local agent (completed)

> Record of what was actually done for Lab 1, per the steps in
> [`WORKSHOP_LABS.md`](WORKSHOP_LABS.md) and the LO4 checkpoint in [`PEDAGOGY_SPEC.md`](PEDAGOGY_SPEC.md).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Baseline run (existing profile + project)

```bash
python -m agent.app --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

Confirmed the reference output: repos to clone (`payments-api`, `payments-worker`,
`payments-infra`), AWS/repo/CI-CD permissions, day-1/week-1 checklist, approvals required, and
risk notes — all pulled from [`profiles/backend-dev.yaml`](../profiles/backend-dev.yaml) and
[`projects/payments-platform.yaml`](../projects/payments-platform.yaml).

## Exercise 1 — new profile

Added [`profiles/data-engineer.yaml`](../profiles/data-engineer.yaml):

- **AWS permissions:** `s3-read-write`, `athena-query`, `glue-read-write`, `cloudwatch-read`
- **Day 1 checklist:** swaps backend-dev's "run unit tests" / staging-deploy focus for "run a
  sample pipeline against the staging data lake"
- **Approvals required:** unchanged shape (`prod-write`, `secrets-prod-read`, `admin-access`) —
  same gate, different profile

## Exercise 2 — new project

Added [`projects/analytics-platform.yaml`](../projects/analytics-platform.yaml):

- **Repositories:** `analytics-ingestion`, `analytics-transform`, `analytics-infra` (data-lake
  equivalent of payments-platform's api/worker/infra split)
- **Business goal:** ingesting, transforming and exposing business analytics data
- **Risk notes:** same production-write gating as payments-platform

## Plan generation with the new combo

```bash
python -m agent.app --employee "Your Name" --email you@example.com \
  --profile data-engineer --project analytics-platform
```

Produced a complete plan: correct repos, S3/Athena/Glue permissions, data-pipeline-flavored day-1
checklist, and the same approvals/risk-notes gating as the reference profile. No errors.

## LO4 checkpoint — explain out loud

**Why these permissions/checklist items for a data engineer?**

A data engineer's day-1 work is pulling and transforming data, not deploying services, so the
AWS permissions reflect that: `s3-read-write` and `glue-read-write` because that's where the data
lake and ETL jobs live, `athena-query` so they can inspect the data they're transforming, and
`cloudwatch-read` for basic pipeline observability. Deliberately left off anything like
`secrets-read-dev` or direct deploy permissions from the backend-dev profile — a data engineer
doesn't need service secrets on day 1, and granting them anyway would be over-provisioning. Same
logic in the checklist: "run a sample pipeline against staging" replaces backend-dev's "deploy to
staging," because the thing that needs proving on day 1 is a pipeline run, not a service deploy.

**What breaks if `approvals_required` were empty?**

`approvals_required` is the boundary between what onboarding grants automatically and what needs a
human to say yes. It currently lists `prod-write`, `secrets-prod-read`, `admin-access`. Emptying it
wouldn't stop those from being silently treated as pre-approved — the plan would still print a
permissions section, but with no signal telling a reviewer "this one needs sign-off." The field
isn't enforcing anything by itself (Lab 1 permissions are simulated text, not IAM policy), but it's
the data a real backoffice or approval workflow would key off of. Empty, a new hire's plan would
look complete and safe while silently missing the guardrail that says "don't grant this without
asking someone."

## Completion criteria — met

- [x] Plan generates with correct repos, permissions, and checklist for the new profile+project
      combination.
- [x] `pytest` passes.
- [x] LO4 explanation written down (above), not just the files existing.
