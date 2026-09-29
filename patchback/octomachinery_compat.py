"""Workarounds for the limitations of the pinned ``octomachinery``."""

import typing

import attr

from octomachinery.github.api import app_client
from octomachinery.github.models import (
    GitHubAppInstallation as _UpstreamGitHubAppInstallation,
)


@attr.dataclass
class GitHubAppInstallation(_UpstreamGitHubAppInstallation):
    """An installation model that knows the fields GitHub grew later.

    ``octomachinery`` feeds the ``/app/installations`` API response into
    its model through a wrapper that drops the keys the model does not
    declare, logging ``Excessive arguments passed to callback`` for each
    such response. GitHub has since added ``client_id`` and
    ``contact_email`` to that payload, so every installation lookup —
    meaning every webhook delivery — emits that warning.

    Declaring the two fields here makes the payload map onto the model
    exactly, which is both what silences the warning and what stops the
    values from being thrown away.
    """

    client_id: typing.Optional[str] = None
    """OAuth client ID of the GitHub App this installation belongs to."""
    contact_email: typing.Optional[str] = None
    """Contact e-mail address of the installation target."""


def patch_github_app_installation_model() -> None:
    """Teach ``octomachinery`` about the modern installation payload.

    This is a stopgap for the pinned ``octomachinery`` release and
    becomes redundant once its own model covers these fields.
    """
    app_client.GitHubAppInstallationModel = GitHubAppInstallation
