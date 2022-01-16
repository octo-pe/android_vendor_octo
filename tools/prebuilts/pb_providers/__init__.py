import requests
from . import base, fdroid, github


PROVIDERS = {
    "direct": base.DirectDownloadProvider,
    "fdroid": fdroid.FDroidProvider(),
    "ghrelease": github.GithubReleaseProvider
}
