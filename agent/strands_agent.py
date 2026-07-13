"""OPTIONAL — Strands Agents implementation of the onboarding assistant.

This file is the goal of **Lab 2** of the workshop. The default path
(`agent/app.py`) runs WITHOUT the Strands SDK by calling `build_plan()` directly.
Here, instead, a **Strands agent reasons** and decides when to invoke each tool.

Requirements to run it (not needed for the local path in `agent/app.py`):

    # 1) Install the SDK (or uncomment the lines in requirements.txt)
    pip install strands-agents bedrock-agentcore

    # 2) Configure AWS credentials + Bedrock model access
    cp .env.example .env        # set AWS_REGION and BEDROCK_MODEL_ID

    # 3) Run the real agent
    python -m agent.strands_agent \\
        --employee "Ada Lovelace" --email ada@example.com \\
        --profile backend-dev --project payments-platform

The tools wrapped here are EXACTLY the same local functions used by
`agent/app.py`. The difference is who orchestrates them: before it was us, now it's the agent.
"""
from __future__ import annotations

import argparse
import os

from agent.prompts import SYSTEM_PROMPT
from agent.tools.load_profile import load_profile as _load_profile
from agent.tools.load_project import load_project as _load_project
from agent.tools.generate_plan import generate_onboarding_plan as _generate_onboarding_plan
from agent.tools.track_progress import mark_step_done as _mark_step_done

try:
    from strands import Agent, tool
    from strands.models import BedrockModel
except ImportError as exc:  # pragma: no cover - only triggers without the SDK installed
    raise SystemExit(
        "\n[onboard-assistant] The Strands SDK is not installed.\n"
        "This is the 'real agent' path of the workshop (Lab 2).\n"
        "  1) Uncomment 'strands-agents' and 'bedrock-agentcore' in requirements.txt\n"
        "     (or install: pip install strands-agents bedrock-agentcore).\n"
        "  2) Configure AWS credentials and Bedrock model access (.env).\n"
        "  3) For the LOCAL path without the SDK use: python -m agent.app ...\n"
        f"  (import detail: {exc})\n"
    )


# --- Tool policy -------------------------------------------------------------
# MVP rule from docs/AGENTCORE_STRANDS_NOTES.md:
# dangerous actions must never run automatically.
WRITE_TOOL_NAMES = {"mark_step_done"}
DANGEROUS_ACTIONS = (
    "create a real user",
    "grant production permissions",
    "read production secrets",
    "deploy to production",
)


def _is_yes(answer: str) -> bool:
    normalized = answer.strip().lower()
    return normalized in {"y", "yes"}


def _confirm_write_action(action_summary: str) -> bool:
    """Ask for human approval before running any write tool in CLI mode."""
    auto_approve = os.environ.get("ONBOARD_AUTO_APPROVE_WRITES", "").strip().lower()
    if auto_approve in {"1", "true", "yes"}:
        return True

    print("\n[HITL] Proposed write action")
    print(f"[HITL] {action_summary}")
    print("[HITL] Continue? Reply 'yes' to approve, anything else to cancel.")
    try:
        answer = input("[approval] > ")
    except EOFError:
        print("[HITL] No approval received (EOF). Write action cancelled.")
        return False
    return _is_yes(answer)


# --- Read tools --------------------------------------------------------------
@tool
def load_profile(profile_id: str) -> dict:
    """Load a declarative onboarding profile from profiles/<id>.yaml.

    Returns expected permissions, base checklist and required approvals.
    """
    return _load_profile(profile_id)


@tool
def load_project(project_id: str) -> dict:
    """Load a declarative project from projects/<id>.yaml.

    Returns repositories, architecture, first tasks and risk notes.
    """
    return _load_project(project_id)


# --- Generation tool ----------------------------------------------------------
@tool
def generate_onboarding_plan(
    employee_name: str,
    employee_email: str,
    profile: dict,
    project: dict,
) -> str:
    """Generate the onboarding plan in Markdown from a profile and a project.

    `profile` and `project` are the dicts returned by load_profile and load_project.
    """
    return _generate_onboarding_plan(employee_name, employee_email, profile, project)


# --- Write tool ----------------------------------------------------------------
@tool
def mark_step_done(employee_email: str, step_id: str, note: str = "") -> dict:
    """Record a completed onboarding step (local MVP state).

    In production this is replaced by a write to DynamoDB.
    """
    summary = (
        f"{WRITE_TOOL_NAMES} -> mark step '{step_id}' as done "
        f"for '{employee_email}'"
    )
    if note:
        summary += f" (note: {note})"
    if not _confirm_write_action(summary):
        return {
            "status": "cancelled",
            "reason": "human_rejected_or_missing_approval",
            "employee_email": employee_email,
            "step_id": step_id,
            "note": note,
        }
    return _mark_step_done(employee_email, step_id, note)


def build_agent() -> Agent:
    """Build the Strands agent with a Bedrock model + onboarding tools."""
    model = BedrockModel(
        model_id=os.environ.get(
            "BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        ),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            load_profile,
            load_project,
            generate_onboarding_plan,
            mark_step_done,
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an onboarding plan using a real Strands agent."
    )
    parser.add_argument("--employee", required=True, help="Employee full name")
    parser.add_argument("--email", required=True, help="Employee email")
    parser.add_argument("--profile", required=True, help="Profile id, e.g. backend-dev")
    parser.add_argument("--project", required=True, help="Project id, e.g. payments-platform")
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Keep a conversation open after plan generation (recommended for Lab 2).",
    )
    args = parser.parse_args()

    agent = build_agent()
    prompt = (
        f"Generate the onboarding plan for employee '{args.employee}' "
        f"(email {args.email}) with profile '{args.profile}' on project "
        f"'{args.project}'. Use the load_profile and load_project tools to get "
        f"the data and then generate_onboarding_plan to produce a detailed step by step plan in Markdown. Show me the checklist."
    )
    result = agent(prompt)
    print(result)

    if not args.chat:
        return

    print("\n[chat] Conversation mode enabled.")
    print("[chat] Example: 'I finished step env_setup, mark it done with note local setup ok'.")
    print("[chat] Type 'exit' or 'quit' to finish.\n")
    while True:
        try:
            user_message = input("you> ").strip()
        except EOFError:
            print("\n[chat] Input ended.")
            break

        if not user_message:
            continue
        if user_message.lower() in {"exit", "quit"}:
            print("[chat] Bye.")
            break

        turn_prompt = (
            f"Employee context: name='{args.employee}', email='{args.email}', "
            f"profile='{args.profile}', project='{args.project}'.\n"
            f"User message: {user_message}\n"
            "If this requires a write tool, explain your intended action first and "
            "request confirmation before completing it."
        )
        turn_result = agent(turn_prompt)
        print(f"agent> {turn_result}")


if __name__ == "__main__":
    main()
