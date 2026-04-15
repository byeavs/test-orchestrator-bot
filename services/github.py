import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"

STATUS_EMOJI = {
    "queued": "🟡",
    "in_progress": "🔄",
    "completed": "✅",
    "waiting": "⏳",
}

CONCLUSION_EMOJI = {
    "success": "✅",
    "failure": "❌",
    "cancelled": "⚪️",
    "skipped": "⏭",
    "timed_out": "⏰",
    "action_required": "⚠️",
}

@dataclass
class WorkflowRun:
    run_id:int
    status:str
    conclusion:Optional[str]
    html_url:str
    created_at:str
    jobs_url:str

@dataclass
class JobStatus:
    name:str
    status:str
    conclusion:Optional[str]


class GitHubService:
    def __init__(self, token:str, repo:str, workflow_id:str, branch:str = "main"):
        self.token = token
        self.repo = repo
        self.workflow_id = workflow_id
        self.branch = branch
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._last_run_id:Optional[int] = None

    async def dispatch_workflow(self, inputs:Optional[dict] = None) -> bool:
        url = f"{GITHUB_API}/repos/{self.repo}/actions/workflows/{self.workflow_id}/dispatches"
        payload = {"ref": self.branch}
        if inputs:
            payload["inputs"] = inputs

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self._headers, json=payload) as resp:
                if resp.status == 204:
                    logger.info("Workflow dispatched successfully")
                    await asyncio.sleep(3)
                    run = await self.get_latest_run()
                    if run:
                        self._last_run_id = run.run_id
                    return True
                else:
                    text = await resp.text()
                    logger.error("Dispatch failed %s: %s", resp.status, text)
                    return False

    async def get_latest_run(self) -> Optional[WorkflowRun]:
        """Fetch the most recent run for this workflow."""
        url = (
            f"{GITHUB_API}/repos/{self.repo}/actions/workflows/"
            f"{self.workflow_id}/runs?per_page=1&branch={self.branch}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                runs = data.get("workflow_runs", [])
                if not runs:
                    return None
                r = runs[0]
                return WorkflowRun(
                    run_id=r["id"],
                    status=r["status"],
                    conclusion=r.get("conclusion"),
                    html_url=r["html_url"],
                    created_at=r["created_at"],
                    jobs_url=r["jobs_url"],
                )

    async def get_run_by_id(self, run_id:int) -> Optional[WorkflowRun]:
        url = f"{GITHUB_API}/repos/{self.repo}/actions/runs/{run_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers) as resp:
                if resp.status != 200:
                    return None
                r = await resp.json()
                return WorkflowRun(
                    run_id=r["id"],
                    status=r["status"],
                    conclusion=r.get("conclusion"),
                    html_url=r["html_url"],
                    created_at=r["created_at"],
                    jobs_url=r["jobs_url"],
                )

    async def get_jobs(self, run:WorkflowRun) -> list[JobStatus]:
        async with aiohttp.ClientSession() as session:
            async with session.get(run.jobs_url, headers=self._headers) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return [
                    JobStatus(
                        name=j["name"],
                        status=j["status"],
                        conclusion=j.get("conclusion"),
                    )
                    for j in data.get("jobs", [])
                ]

    async def get_status_text(self) -> tuple[str, Optional[str]]:
        """Returns (status_message, run_url)."""
        run_id = self._last_run_id
        if run_id:
            run = await self.get_run_by_id(run_id)
        else:
            run = await self.get_latest_run()

        if not run:
            return "⚠️ No runs found for this workflow.", None

        jobs = await self.get_jobs(run)

        lines = [f"<b>Run #{run.run_id}</b>  •  <i>{run.created_at[:10]}</i>\n"]

        if jobs:
            for job in jobs:
                if job.status == "completed":
                    emoji = CONCLUSION_EMOJI.get(job.conclusion or "", "❓")
                else:
                    emoji = STATUS_EMOJI.get(job.status, "❓")
                lines.append(f"{emoji}  <code>{job.name}</code>: {job.conclusion or job.status}")
        else:
            if run.status == "completed":
                emoji = CONCLUSION_EMOJI.get(run.conclusion or "", "❓")
                lines.append(f"{emoji} Overall: {run.conclusion}")
            else:
                emoji = STATUS_EMOJI.get(run.status, "❓")
                lines.append(f"{emoji} Status: {run.status}")

        return "\n".join(lines), run.html_url

    @property
    def last_run_id(self) -> Optional[int]:
        return self._last_run_id

    def set_last_run_id(self, run_id:int):
        self._last_run_id = run_id
