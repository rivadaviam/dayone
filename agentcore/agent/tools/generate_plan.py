from typing import Any


def _bullet(items: list[str], indent: int = 0) -> str:
    prefix = " " * indent + "- "
    return "\n".join(prefix + str(item) for item in items)


def generate_onboarding_plan(
    employee_name: str,
    employee_email: str,
    profile: dict[str, Any],
    project: dict[str, Any],
) -> str:
    """Generate a personalized onboarding plan as Markdown."""
    repos = project.get("repositories", [])
    profile_permissions = profile.get("permissions", {})
    base_checklist = profile.get("base_checklist", {})

    repo_section = []
    for repo in repos:
        repo_section.append(
            f"### {repo['name']}\n"
            f"{repo.get('description', '')}\n\n"
            f"```bash\n"
            f"git clone {repo.get('clone_url', '<clone-url-pending>')}\n"
            f"cd {repo['name']}\n"
            f"{repo.get('bootstrap', '# bootstrap pending')}\n"
            f"{repo.get('test', '# test command pending')}\n"
            f"```"
        )

    day_1 = base_checklist.get("day_1", [])
    week_1 = base_checklist.get("week_1", [])

    plan = f"""# Onboarding plan - {employee_name}

**Employee:** {employee_name}
**Email:** {employee_email}
**Profile:** {profile.get('name', profile.get('id'))}
**Project:** {project.get('name', project.get('id'))}

## Project business goal

{project.get('business_goal', 'Pending documentation.')}

## Architecture summary

{project.get('architecture_summary', 'Pending documentation.')}

## Expected permissions

### AWS
{_bullet(profile_permissions.get('aws', []))}

### Repositories
- Expected access: {profile_permissions.get('repositories', {}).get('access', 'pending')}

### CI/CD
{_bullet(profile_permissions.get('ci_cd', []))}

## Repositories to clone

{chr(10).join(repo_section)}

## Day 1 checklist

{_bullet(day_1)}

## Week 1 checklist

{_bullet(week_1)}

## Suggested first tasks

{_bullet(project.get('first_tasks', []))}

## Suggested documentation

{_bullet(project.get('key_docs', []))}

## Approvals and risks

### Approvals required by profile
{_bullet(profile.get('approvals_required', []))}

### Project risk notes
{_bullet(project.get('risk_notes', []))}

## MVP status

This plan was generated with local declarative data. In the production version, these steps can be connected to IAM Identity Center, real repos, pipelines and DynamoDB.
"""
    return plan.strip() + "\n"
