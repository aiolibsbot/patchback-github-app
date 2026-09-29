"""Tests for the ``octomachinery`` compatibility patches."""

import asyncio
import logging

import pytest


pytest.importorskip(
    'octomachinery',
    reason='the compat patches poke at the real `octomachinery` models',
)

from octomachinery.github.api import app_client  # noqa: E402
from octomachinery.github.models import (  # noqa: E402
    GitHubAppInstallation as UpstreamGitHubAppInstallation,
)
from octomachinery.utils.asynctools import (  # noqa: E402
    dict_to_kwargs_cb,
)

from patchback.octomachinery_compat import (  # noqa: E402
    patch_github_app_installation_model,
)


MODERN_INSTALLATION_PAYLOAD = {
    'id': 8_227_071,
    'client_id': 'Iv1.0123456789abcdef',
    'account': {'login': 'sanitizers', 'id': 45_432_694},
    'repository_selection': 'all',
    'access_tokens_url':
        'https://api.github.com/app/installations/8227071/access_tokens',
    'repositories_url': 'https://api.github.com/installation/repositories',
    'html_url': 'https://github.com/organizations/sanitizers/settings/'
                'installations/8227071',
    'app_id': 41_648,
    'app_slug': 'patchback',
    'target_id': 45_432_694,
    'target_type': 'Organization',
    'permissions': {'contents': 'write', 'pull_requests': 'write'},
    'events': ['pull_request'],
    'created_at': '2026-09-29T15:52:35Z',
    'updated_at': '2026-09-29T15:52:35Z',
    'single_file_name': None,
    'has_multiple_single_files': False,
    'single_file_paths': [],
    'suspended_by': None,
    'suspended_at': None,
    'contact_email': 'octocat@example.com',
}
"""A ``/app/installations/{id}`` response as GitHub sends it today."""


@pytest.fixture
def patched_installation_model(monkeypatch):
    """Return the installation model ``octomachinery`` would use."""
    monkeypatch.setattr(
        app_client, 'GitHubAppInstallationModel',
        app_client.GitHubAppInstallationModel,
    )
    patch_github_app_installation_model()
    return app_client.GitHubAppInstallationModel


def make_installation(model, payload):
    """Map an API payload onto the model the way ``octomachinery`` does."""
    return asyncio.run(dict_to_kwargs_cb(model)(payload))


def test_modern_payload_is_mapped_without_warnings(
        caplog, patched_installation_model,
):
    """Check that today's GitHub payload maps onto the model as is."""
    caplog.set_level(logging.WARNING)

    installation = make_installation(
        patched_installation_model, MODERN_INSTALLATION_PAYLOAD,
    )

    assert not caplog.records
    assert installation.id == MODERN_INSTALLATION_PAYLOAD['id']
    assert installation.client_id == MODERN_INSTALLATION_PAYLOAD['client_id']
    assert installation.contact_email == 'octocat@example.com'


def test_payload_without_the_new_fields_is_still_accepted(
        patched_installation_model,
):
    """Check that the added fields are optional."""
    legacy_payload = {
        payload_key: payload_value
        for payload_key, payload_value in MODERN_INSTALLATION_PAYLOAD.items()
        if payload_key not in {'client_id', 'contact_email'}
    }

    installation = make_installation(
        patched_installation_model, legacy_payload,
    )

    assert installation.client_id is None
    assert installation.contact_email is None


def test_unpatched_model_warns_about_the_new_fields(caplog):
    """Check that the upstream model is what triggers the warning."""
    caplog.set_level(logging.WARNING)

    make_installation(
        UpstreamGitHubAppInstallation, MODERN_INSTALLATION_PAYLOAD,
    )

    assert any(
        log_record.message.startswith('Excessive arguments passed to callback')
        for log_record in caplog.records
    )
