import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass
class Config:
    bot_token:str
    github_token:str
    repo:str
    workflow_id:str
    github_branch: str = "main"


def load_config() -> Config:
    return Config(
        bot_token=os.environ["BOT_TOKEN"],
        github_token=os.environ["GITHUB_TOKEN"],
        repo=os.environ["REPO"],
        workflow_id=os.environ.get("WORKFLOW_ID", "tests.yml"),
        github_branch=os.environ.get("GITHUB_BRANCH", "main"),
    )