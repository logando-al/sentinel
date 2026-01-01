"""
PDF Sentinel - Auto Updater
Checks GitHub releases for new versions.
"""

import urllib.request
import json
from typing import Optional
from dataclasses import dataclass


GITHUB_REPO = "logando-al/sentinel"
CURRENT_VERSION = "1.3.2"


@dataclass
class UpdateInfo:
    """Information about an available update."""
    available: bool
    current_version: str
    latest_version: str
    download_url: Optional[str] = None
    changelog: Optional[str] = None
    release_date: Optional[str] = None


def check_for_updates() -> UpdateInfo:
    """
    Check GitHub releases for a newer version.
    
    Returns:
        UpdateInfo with version comparison and download details
    """
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        
        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'PDF-Sentinel-Updater'}
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        latest_version = data.get('tag_name', '').lstrip('v')
        download_url = data.get('html_url', '')
        changelog = data.get('body', '')
        release_date = data.get('published_at', '')[:10] if data.get('published_at') else None
        
        # Compare versions
        is_newer = _compare_versions(latest_version, CURRENT_VERSION) > 0
        
        return UpdateInfo(
            available=is_newer,
            current_version=CURRENT_VERSION,
            latest_version=latest_version,
            download_url=download_url,
            changelog=changelog,
            release_date=release_date
        )
        
    except Exception as e:
        # Return no update available on error
        return UpdateInfo(
            available=False,
            current_version=CURRENT_VERSION,
            latest_version=CURRENT_VERSION,
            changelog=f"Could not check for updates: {str(e)}"
        )


def _compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.
    
    Returns:
        1 if v1 > v2, -1 if v1 < v2, 0 if equal
    """
    try:
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]
        
        # Pad with zeros
        while len(parts1) < 3:
            parts1.append(0)
        while len(parts2) < 3:
            parts2.append(0)
        
        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
    except:
        return 0


def open_download_page(url: str = None):
    """Open the download page in the default browser."""
    import webbrowser
    if url:
        webbrowser.open(url)
    else:
        webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
