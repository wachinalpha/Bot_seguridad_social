#!/usr/bin/env python3
"""Download a corpus artifact from GitHub Releases."""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_app.config.settings import settings


def main():
    parser = argparse.ArgumentParser(description="Fetch a corpus zip from GitHub Releases")
    parser.add_argument("--version", required=True, help="Corpus version, for example v1")
    parser.add_argument("--repo", required=True, help="GitHub repository in OWNER/REPO format")
    args = parser.parse_args()

    tag = f"corpus-{args.version}"
    archive_name = f"anses-corpus-{args.version}.zip"
    target_root = settings.corpus_storage_path_resolved
    target_root.mkdir(parents=True, exist_ok=True)
    download_url = _resolve_asset_api_url(args.repo, tag, archive_name)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        archive_path = temp_path / archive_name
        _download_file(download_url, archive_path)

        with ZipFile(archive_path) as zip_file:
            zip_file.extractall(target_root)

        extracted_root = target_root / f"anses-corpus-{args.version}"
        final_target = target_root / args.version
        if final_target.exists():
            shutil.rmtree(final_target)
        extracted_root.rename(final_target)

    print(final_target)
def _resolve_asset_api_url(repo: str, tag: str, archive_name: str) -> str:
    response = requests.get(
        f"https://api.github.com/repos/{repo}/releases/tags/{tag}",
        headers=_github_headers(),
        timeout=30,
    )

    if response.status_code == 404:
        visible_tags = _list_visible_release_tags(repo)
        if visible_tags:
            joined_tags = ", ".join(visible_tags)
            raise SystemExit(
                f"Release tag not found: {repo} {tag}. Releases visibles para este token: {joined_tags}"
            )
        raise SystemExit(
            f"Release tag not found: {repo} {tag}. No hay releases visibles para este token o la release sigue en draft."
        )

    response.raise_for_status()
    release_payload = response.json()

    for asset in release_payload.get("assets", []):
        if asset.get("name") == archive_name:
            return asset["url"]

    raise SystemExit(f"Asset not found in release {tag}: {archive_name}")


def _download_file(url: str, target_path: Path) -> None:
    headers = _github_headers()
    headers["Accept"] = "application/octet-stream"

    with requests.get(url, headers=headers, stream=True, timeout=120) as response:
        response.raise_for_status()
        with target_path.open("wb") as output_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output_file.write(chunk)


def _github_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _list_visible_release_tags(repo: str) -> list[str]:
    response = requests.get(
        f"https://api.github.com/repos/{repo}/releases",
        headers=_github_headers(),
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return [release.get("tag_name", "") for release in payload if release.get("tag_name")]


if __name__ == "__main__":
    main()
