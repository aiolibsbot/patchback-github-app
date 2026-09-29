"""Patchback robot runner."""

from octomachinery.app.server.runner import run as run_app
from octomachinery.utils.versiontools import get_version_from_scm_tag

from . import event_handlers  # noqa: F401; pylint: disable=unused-import
from .octomachinery_compat import patch_github_app_installation_model


# NOTE: GitHub has grown `client_id` and `contact_email` in the
# NOTE: `/app/installations` API responses, which the installation model of
# NOTE: the pinned `octomachinery` does not declare. It drops the unknown
# NOTE: keys and logs a warning for every webhook delivery, so we widen the
# NOTE: model until an `octomachinery` release does it upstream.
patch_github_app_installation_model()

__name__ == '__main__' and run_app(  # pylint: disable=expression-not-assigned
    name='Patchback-Bot',
    version=get_version_from_scm_tag(root='..', relative_to=__file__),
    url='https://github.com/apps/patchback',
)
