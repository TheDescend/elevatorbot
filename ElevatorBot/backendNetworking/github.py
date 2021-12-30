from typing import Optional

from anyio import to_thread
from github import Github
from github.GithubObject import NotSet
from github.Label import Label
from github.Repository import Repository

from rename_to_settings import (
    GITHUB_APPLICATION_API_KEY,
    GITHUB_ISSUE_LABEL_NAMES,
    GITHUB_REPOSITORY_ID,
)

_REPO: Optional[Repository] = None
_LABELS: Optional[list[Label]] = None


async def get_github_repo() -> Optional[Repository]:
    """Returns the GitHub api repo object"""

    global _REPO

    if not _REPO:
        if GITHUB_APPLICATION_API_KEY and GITHUB_REPOSITORY_ID:
            github_api = Github(GITHUB_APPLICATION_API_KEY)

            # run those in a thread with anyio since they are blocking
            _REPO = await to_thread.run_sync(github_api.get_repo, GITHUB_REPOSITORY_ID)

    return _REPO


async def get_github_labels() -> Optional[list[Label]]:
    """Returns the GitHub labels that should be used on the issue"""

    global _LABELS

    if not _LABELS and GITHUB_ISSUE_LABEL_NAMES:
        repo = await get_github_repo()
        if repo:
            _LABELS = []
            for label_name in GITHUB_ISSUE_LABEL_NAMES:
                # run those in a thread with anyio since they are blocking
                label = await to_thread.run_sync(repo.get_label, label_name)

                _LABELS.append(label)

    return _LABELS
