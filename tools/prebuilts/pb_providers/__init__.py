import requests
from . import base, fdroid, github, symlink


PROVIDERS = {
    "direct": base.DirectDownloadProvider,
    "fdroid": fdroid.FDroidProvider(),
    "ghrelease": github.GithubReleaseProvider,
    "symlink": symlink.SymlinkProivder
}
